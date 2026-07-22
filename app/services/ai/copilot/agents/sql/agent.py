"""Enterprise SQL Agent."""

from __future__ import annotations

from app.services.ai.copilot.context_runtime import ExecutionContext

from .base import BaseSQLAgent
from .executor import SQLExecutor
from .formatter import SQLFormatter
from .generator import SQLGenerator
from .planner import SQLPlanner
from .validator import SQLValidator


class SQLAgent(BaseSQLAgent):
    def __init__(self) -> None:
        self.planner = SQLPlanner()
        self.generator = SQLGenerator()
        self.validator = SQLValidator()
        self.executor = SQLExecutor()
        self.formatter = SQLFormatter()

    async def run(self, context: ExecutionContext) -> ExecutionContext:
        plan = self.planner.build_plan(context.question)

        if not plan.requires_sql:
            return context

        generation = await self.generator.generate(context.question, plan)
        self.validator.validate(generation.sql)
        execution = await self.executor.execute(generation.sql)
        context.sql_result = self.formatter.format(execution)

        return context