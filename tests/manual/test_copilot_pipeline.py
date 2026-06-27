"""
Manual end-to-end test for the AI Copilot pipeline.

Run:

python tests/manual/test_copilot_pipeline.py
"""

from app.database import SessionLocal

from app.services.ai.vector_store.manager import (
    VectorManager,
)

from app.services.ai.copilot.intent import (
    RuleBasedIntentClassifier,
)

from app.services.ai.copilot.context import (
    ContextBuilder,
)

from app.services.ai.copilot.prompt import (
    PromptBuilder,
)

from app.services.ai.llm import (
    LLMFactory,
)

from app.services.ai.copilot.service import (
    CopilotService,
)

from app.services.ai.copilot.models import (
    CopilotRequest,
)


def section(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def main():

    db = SessionLocal()

    try:

        section("STEP 1 - Initialize Vector Store")

        VectorManager.initialize(db)

        print(
            "Indexed Documents:",
            VectorManager.indexed_documents(),
        )

        section("STEP 2 - Intent")

        classifier = (
            RuleBasedIntentClassifier()
        )

        intent = classifier.classify(
            "Top selling product"
        )

        print(intent.model_dump())

        section("STEP 3 - Context")

        context = (
            ContextBuilder()
            .build(
                "Top selling product"
            )
        )

        print(context.model_dump())

        section("STEP 4 - Prompt")

        prompt = (
            PromptBuilder()
            .build(
                question="Top selling product",
                context=context,
            )
        )

        print(prompt)

        section("STEP 5 - LLM")

        llm = (
            LLMFactory.create()
        )

        answer = (
            llm.generate(prompt)
        )

        print(answer)

        section("STEP 6 - Copilot")

        response = (
            CopilotService.ask(
                CopilotRequest(
                    question="Top selling product"
                )
            )
        )

        print(response.model_dump())

        section("SUCCESS")

        print(
            "Copilot pipeline completed successfully."
        )

    except Exception as exc:

        section("FAILED")

        print(type(exc).__name__)

        print(exc)

        raise

    finally:

        db.close()


if __name__ == "__main__":

    main()