"""Tests for the live SQL tool-calling framework."""

from __future__ import annotations

import json

from app.services.ai.copilot.agents.planner.models import ExecutionStep
from app.services.ai.copilot.agents.planner.rules import PlannerRules
from app.services.ai.copilot.tools import (
    SQLQueryTool,
    ToolCall,
    ToolCallingAgent,
    ToolContext,
    ToolExecutor,
)


class TestToolDefinition:
    def test_json_schema_shape(self):
        schema = SQLQueryTool().definition.to_json_schema()

        assert schema["type"] == "function"
        assert schema["function"]["name"] == "run_sql_query"
        assert "sql" in schema["function"]["parameters"]["properties"]
        assert "sql" in schema["function"]["parameters"]["required"]


class TestSQLQueryToolValidation:
    async def test_rejects_empty_sql(self):
        tool = SQLQueryTool()
        result = await tool.execute({}, ToolContext(question="q"))

        assert not result.success
        assert "No SQL" in result.error

    async def test_rejects_write_statement(self):
        tool = SQLQueryTool()
        result = await tool.execute(
            {"sql": "DELETE FROM fact_sales"}, ToolContext(question="q")
        )

        assert not result.success
        assert "rejected" in result.error

    async def test_rejects_multi_statement(self):
        tool = SQLQueryTool()
        result = await tool.execute(
            {"sql": "SELECT 1; DROP TABLE fact_sales"}, ToolContext(question="q")
        )

        assert not result.success


class TestToolExecutor:
    async def test_unknown_tool(self):
        executor = ToolExecutor(tools=[SQLQueryTool()])
        call = ToolCall(tool_name="nonexistent", arguments={})

        result = await executor.dispatch(call, ToolContext(question="q"))

        assert not result.success
        assert "Unknown tool" in result.error

    async def test_missing_required_argument(self):
        executor = ToolExecutor(tools=[SQLQueryTool()])
        call = ToolCall(tool_name="run_sql_query", arguments={})

        result = await executor.dispatch(call, ToolContext(question="q"))

        assert not result.success
        assert "Missing required parameter" in result.error

    def test_definitions_list(self):
        executor = ToolExecutor(tools=[SQLQueryTool()])
        definitions = executor.definitions()

        assert len(definitions) == 1
        assert definitions[0]["function"]["name"] == "run_sql_query"


class FakeToolProvider:
    """Returns scripted responses to simulate an LLM tool-calling session."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[str] = []

    def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses.pop(0)


class TestToolCallingAgent:
    def _agent(self, responses: list[str]) -> tuple[ToolCallingAgent, FakeToolProvider]:
        provider = FakeToolProvider(responses)
        executor = ToolExecutor(tools=[SQLQueryTool()])
        return ToolCallingAgent(executor=executor, provider=provider), provider

    async def test_final_answer_without_tool_call(self):
        agent, provider = self._agent(["The answer is 42."])

        result = await agent.run("What is the meaning?")

        assert result.handled
        assert result.answer == "The answer is 42."
        assert result.tool_results == []
        assert len(provider.calls) == 1

    async def test_parse_tool_call_json(self):
        call_json = json.dumps(
            {
                "tool_call": {
                    "name": "run_sql_query",
                    "arguments": {"sql": "SELECT 1 AS x"},
                }
            }
        )
        agent, _ = self._agent([call_json, "Final answer."])

        parsed = agent._parse_tool_call(call_json)

        assert parsed is not None
        assert parsed.tool_name == "run_sql_query"
        assert parsed.arguments["sql"] == "SELECT 1 AS x"

    async def test_parse_returns_none_for_plain_text(self):
        agent, _ = self._agent([])

        assert agent._parse_tool_call("Just a plain answer.") is None

    async def test_unknown_tool_error_fed_back(self):
        call_json = json.dumps(
            {"tool_call": {"name": "bad_tool", "arguments": {}}}
        )
        agent, provider = self._agent([call_json, "Final answer."])

        result = await agent.run("question")

        assert len(result.tool_results) == 1
        assert not result.tool_results[0].success
        assert "Unknown tool" in result.tool_results[0].error
        assert len(provider.calls) == 2


class TestPlannerToolCallingRoute:
    def test_analytics_question_uses_tool_call_step(self):
        steps, reason = PlannerRules.resolve("What are the top products by revenue?")

        assert ExecutionStep.TOOL_CALL in steps
        assert ExecutionStep.SQL not in steps
        assert "tool calling" in reason

    def test_chart_question_unchanged(self):
        steps, _ = PlannerRules.resolve("Show me a chart of sales")

        assert ExecutionStep.CHART in steps
        assert ExecutionStep.TOOL_CALL not in steps