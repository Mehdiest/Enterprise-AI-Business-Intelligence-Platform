"""LLM-driven tool-calling loop."""

from __future__ import annotations

import inspect
import json
import logging
import re
from typing import Any

from app.services.ai.providers import ProviderFactory

from .executor import ToolExecutor
from .models import ToolCall, ToolCallResult, ToolContext

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 3

SYSTEM_PROMPT = """\
You are a business intelligence assistant with access to a SQL database tool.

Available tools:
{tool_schemas}

CRITICAL RULES - YOU MUST FOLLOW THESE:

1. **ALWAYS call the SQL tool FIRST** for ANY question about:
   - Sales, revenue, amounts, totals
   - Products, regions, customers, channels
   - Rankings, comparisons, breakdowns
   - Dates, time periods, trends
   - Counts, averages, sums, percentages
   
2. **NEVER say "data is not available"** without trying the SQL tool first!

3. When you need data, respond with ONLY this JSON format (nothing else):
   {{"tool_call": {{"name": "run_sql_query", "arguments": {{"sql": "YOUR_QUERY_HERE"}}}}}}

4. After receiving tool results, provide a clear, human-readable summary

5. Format numbers as currency for money: $1,234.56

6. Available tables:
   - fact_sales (id, amount, quantity, product_id, region_id, customer_id, channel_id, date_id)
   - dim_product (id, product_name, category, price)
   - dim_region (id, region_name)
   - dim_customer (id, customer_name, segment)
   - dim_channel (id, channel_name)
   - dim_date (id, date, month, quarter, year)

For the final answer after getting data, respond with plain text only.
"""


class ToolCallingAgent:
    """Iterative LLM loop: propose tool calls, execute, feed results back."""

    def __init__(self, executor: ToolExecutor, provider=None) -> None:
        self.executor = executor
        self.provider = provider or ProviderFactory.create()

    async def run(self, question: str, session_id: str | None = None) -> ToolAgentResult:
        """Run the tool-calling loop until a final answer or max iterations."""
        context = ToolContext(question=question, session_id=session_id)
        messages: list[str] = [f"Question: {question}"]
        tool_results: list[ToolCallResult] = []

        logger.info("Starting tool-calling loop | question=%s | session=%s", question[:80], session_id)

        for iteration in range(MAX_ITERATIONS):
            logger.info("=== Iteration %d/%d ===", iteration + 1, MAX_ITERATIONS)
            
            prompt = self._build_prompt(messages)
            response = await self._generate(prompt)
            
            logger.info("LLM raw response (iter %d): [%s]", iteration + 1, 
                       (response[:300] + "...") if len(response or "") > 300 else response)

            call = self._parse_tool_call(response)
            
            if call is None:
                # No tool call found - this should be the final answer
                logger.info("No tool_call detected -> using as FINAL ANSWER")
                cleaned = self._clean_answer(response)
                logger.info("Final cleaned answer: [%s]", cleaned[:200] if cleaned else "EMPTY")
                return ToolAgentResult(
                    answer=cleaned, 
                    tool_results=tool_results, 
                    handled=True
                )

            logger.info("Tool call parsed | name=%s | sql=%s", 
                       call.tool_name, 
                       call.arguments.get("sql", "")[:100] if isinstance(call.arguments, dict) else "")

            # Execute the tool call
            try:
                result = await self.executor.dispatch(call, context)
                tool_results.append(result)
                
                logger.info("Tool executed | success=%s | rows=%d | error=%s",
                           result.success,
                           len(result.output.get("rows", [])) if result.success and isinstance(result.output, dict) else 0,
                           result.error or "None")
                
                # Add interaction to message history
                messages.append(f"Tool call: {call.tool_name}({json.dumps(call.arguments, default=str)[:200]})")
                messages.append(f"Tool result: {result.to_context_string()}")
                
                # If tool execution failed on last iteration, provide error summary
                if not result.success and iteration == MAX_ITERATIONS - 1:
                    error_msg = (
                        f"I attempted to query the data but encountered an issue: "
                        f"{result.error}. Please ensure data has been uploaded via /ingest/csv."
                    )
                    logger.warning("Tool FAILED on last iter | returning error")
                    return ToolAgentResult(answer=error_msg, tool_results=tool_results, handled=True)
                    
            except Exception as e:
                logger.exception("Tool execution EXCEPTION | tool=%s | err=%s", call.tool_name, e)
                if iteration == MAX_ITERATIONS - 1:
                    return ToolAgentResult(
                        answer=f"An error occurred while processing your request: {str(e)}",
                        tool_results=tool_results,
                        handled=True,
                    )

        # Max iterations reached - ask for final answer
        logger.info("Max iterations reached -> requesting FINAL SUMMARY")
        final_prompt = (
            self._build_prompt(messages)
            + "\n\n"
            "IMPORTANT: Based on all the tool results above, provide your final answer now.\n"
            "- Do NOT make another tool_call\n"
            "- Do NOT output any JSON\n"
            "- Just give me a clear, human-readable summary of the data results\n"
            "- Start directly with the answer (e.g., 'Total sales are $X...')"
        )
        
        answer = await self._generate(final_prompt)
        
        # Clean up but preserve meaningful content
        answer = self._clean_answer(answer)
        
        logger.info("Final summary generated: [%s]", answer[:250] if answer else "EMPTY")
        
        return ToolAgentResult(answer=answer, tool_results=tool_results, handled=True)

    def _build_prompt(self, messages: list[str]) -> str:
        schemas = json.dumps(self.executor.definitions(), indent=2)
        system = SYSTEM_PROMPT.format(tool_schemas=schemas)
        return system + "\n\n" + "\n".join(messages)

    async def _generate(self, prompt: str) -> str:
        try:
            result = self.provider.generate(prompt)
            return await result if inspect.isawaitable(result) else result
        except Exception:
            logger.exception("LLM generation FAILED")
            raise

    @staticmethod
    def _parse_tool_call(response: str) -> ToolCall | None:
        """Extract a tool_call JSON object from the LLM response."""
        if not response:
            return None
            
        response_clean = response.strip()
        
        # Try to find tool_call JSON in various formats
        
        # Pattern 1: Direct {"tool_call": {...}}
        patterns_to_try = [
            # Exact match for tool_call key at start of JSON
            (r'\{\s*"tool_call"\s*:\s*\{.*?\}\s*\}', False),
            # Flexible match with content around it
            (r'\{[^{}]*"tool_call"[^{}]*\}', False),
            # DOTALL version for multiline
            (r'\{.*?"tool_call".*?\}', True),
        ]
        
        for pattern, use_dotall in patterns_to_try:
            flags = re.DOTALL if use_dotall else 0
            match = re.search(pattern, response_clean, flags)
            if match:
                try:
                    json_str = match.group()
                    payload = json.loads(json_str)
                    
                    call_data = payload.get("tool_call")
                    if not isinstance(call_data, dict):
                        continue

                    name = call_data.get("name")
                    if not name:
                        continue

                    arguments = call_data.get("arguments", {})
                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            arguments = {}
                    elif not isinstance(arguments, dict):
                        arguments = {}

                    logger.debug("Successfully parsed tool_call | name=%s", name)
                    return ToolCall(tool_name=name, arguments=arguments)
                    
                except json.JSONDecodeError:
                    continue

        # Pattern 2: Entire response is a JSON with tool_call
        try:
            payload = json.loads(response_clean)
            if isinstance(payload, dict) and "tool_call" in payload:
                call_data = payload["tool_call"]
                if isinstance(call_data, dict) and call_data.get("name"):
                    args = call_data.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}
                    return ToolCall(tool_name=call_data["name"], arguments=args)
        except (json.JSONDecodeError, TypeError):
            pass
        
        logger.debug("No valid tool_call found in response")
        return None

    @staticmethod
    def _clean_answer(answer: str) -> str:
        """Clean the answer while preserving meaningful text content."""
        if not answer:
            return "I processed your request but couldn't generate a textual response."
            
        original = answer
        answer = answer.strip()
        
        # Only remove specific tool_call JSON blocks, NOT entire responses
        # Be very careful not to remove legitimate content
        
        # Remove standalone tool_call JSON objects (but leave surrounding text)
        answer = re.sub(
            r'\{[\s]*"tool_call"[\s]*:[\s]*\{.*?\}[\s]*\}', 
            '', 
            answer, 
            flags=re.DOTALL
        )
        
        # Remove any remaining obvious JSON artifacts that are JUST tool calls
        # But don't remove text that happens to contain braces
        
        # Clean up multiple blank lines
        answer = re.sub(r'\n{3,}', '\n\n', answer)
        
        # Remove leading/trailing whitespace but keep internal formatting
        answer = answer.strip()
        
        # If we accidentally removed everything, use original (better than empty!)
        if not answer or answer in ('', '{}', '}', '{', '[]'):
            logger.warning("Answer became empty after cleaning, using original: [%s]", original[:100])
            # Try to extract text from original
            extracted = re.sub(r'\{[^{}]*"tool_call"[^{}]*\}', '', original)
            extracted = extracted.strip()
            if extracted and len(extracted) > 5:
                return extracted
            # Last resort fallback
            return (
                "I've analyzed your data successfully. "
                "Please check the detailed results in the tool execution logs."
            )
        
        return answer


class ToolAgentResult:
    """Outcome of the tool-calling agent."""

    def __init__(
        self,
        answer: str,
        tool_results: list[ToolCallResult],
        handled: bool,
    ) -> None:
        self.answer = answer
        self.tool_results = tool_results
        self.handled = handled

    @property
    def sql_executed(self) -> bool:
        return any(r.tool_name == "run_sql_query" and r.success for r in self.tool_results)

    @property
    def sql_rows(self) -> list[dict[str, Any]]:
        for r in self.tool_results:
            if r.tool_name == "run_sql_query" and r.success and isinstance(r.output, dict):
                return r.output.get("rows", [])
        return []
