"""Execution-step adapter for the tool-calling agent."""

from __future__ import annotations

import logging

from app.services.ai.copilot.context_runtime import ExecutionContext

from .agent import ToolAgentResult, ToolCallingAgent
from .executor import ToolExecutor
from .sql_tool import SQLQueryTool

logger = logging.getLogger(__name__)


class ToolCallStep:
    """Run the LLM tool-calling loop inside the execution engine."""

    def __init__(self, provider=None) -> None:
        executor = ToolExecutor(tools=[SQLQueryTool()])
        self.agent = ToolCallingAgent(executor=executor, provider=provider)

    async def run(self, context: ExecutionContext) -> ExecutionContext:
        """Execute tool calls and merge results into the runtime context."""
        session_id = context.metadata.get("session_id")

        logger.info(
            "ToolCallStep starting | question=%s | session=%s",
            context.question[:50] if context.question else "None",
            session_id,
        )

        try:
            agent_result = await self.agent.run(context.question, session_id)
            
            logger.info(
                "ToolCallStep completed | answer_length=%d | sql_executed=%d | tool_count=%d",
                len(agent_result.answer) if agent_result.answer else 0,
                agent_result.sql_executed,
                len(agent_result.tool_results),
            )
            
            self._merge(context, agent_result)
            
        except Exception as e:
            logger.exception("Tool-calling agent failed | question=%s", context.question)
            # Set an error response so the user gets feedback
            context.response = f"Sorry, I encountered an error while processing your request: {str(e)}"
            context.metadata["tool_calling"] = False
            context.metadata["tool_call_error"] = str(e)

        return context

    @staticmethod
    def _merge(context: ExecutionContext, agent_result: ToolAgentResult) -> None:
        """Merge tool calling results into execution context."""
        
        logger.debug(
            "Merging agent result | sql_executed=%d | rows=%d",
            agent_result.sql_executed,
            len(agent_result.sql_rows),
        )
        
        if agent_result.sql_executed:
            rows = agent_result.sql_rows
            context.sql_result = {
                "row_count": len(rows),
                "execution_time_ms": 0.0,
                "rows": rows,
            }
            logger.info("SQL result merged | row_count=%d", len(rows))

        context.response = agent_result.answer
        context.metadata["tool_calling"] = True
        context.metadata["tool_calls"] = [
            {"tool": r.tool_name, "success": r.success} for r in agent_result.tool_results
        ]
        
        logger.debug("Context response set | length=%d", len(agent_result.answer) if agent_result.answer else 0)