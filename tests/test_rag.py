"""RAG knowledge base tests."""

from __future__ import annotations

import pytest

from app.services.ai.embeddings import EmbeddingService
from app.services.ai.knowledge.engine import KnowledgeEngine
from app.services.ai.vector_store.manager import VectorManager


class TestEmbeddingService:
    def test_local_embedding_deterministic(self):
        svc = EmbeddingService()
        vec_a = svc.encode("total sales")
        vec_b = svc.encode("total sales")
        assert vec_a == vec_b

    def test_local_embedding_dimension(self):
        svc = EmbeddingService()
        vec = svc.encode("hello")
        assert len(vec) == svc.dimension

    def test_local_embedding_normalized(self):
        svc = EmbeddingService()
        vec = svc.encode("normalize me")
        magnitude = sum(x * x for x in vec) ** 0.5
        assert abs(magnitude - 1.0) < 1e-6

    def test_encode_many(self):
        svc = EmbeddingService()
        vecs = svc.encode_many(["a", "b", "c"])
        assert len(vecs) == 3
        assert all(len(v) == svc.dimension for v in vecs)


class TestKnowledgeEngine:
    @pytest.mark.asyncio
    async def test_empty_warehouse(self, db):
        docs = await KnowledgeEngine(db).build()
        assert docs == []

    @pytest.mark.asyncio
    async def test_builds_documents_after_ingest(self, db, admin_client, sample_csv):
        with open(sample_csv, "rb") as f:
            await admin_client.post(
                "/ingest/csv",
                files={"file": ("sales.csv", f, "text/csv")},
            )

        docs = await KnowledgeEngine(db).build()
        assert len(docs) > 0
        assert any("Laptop" in d.text for d in docs)


class TestVectorManager:
    @pytest.mark.asyncio
    async def test_initialize_empty_warehouse(self, db):
        await VectorManager.initialize(db)
        assert VectorManager.indexed_documents() == 0

    @pytest.mark.asyncio
    async def test_rebuild_after_ingest(self, db, admin_client, sample_csv):
        with open(sample_csv, "rb") as f:
            await admin_client.post(
                "/ingest/csv",
                files={"file": ("sales.csv", f, "text/csv")},
            )

        await VectorManager.rebuild(db)
        assert VectorManager.indexed_documents() > 0

    @pytest.mark.asyncio
    async def test_search_returns_results(self, db, admin_client, sample_csv):
        with open(sample_csv, "rb") as f:
            await admin_client.post(
                "/ingest/csv",
                files={"file": ("sales.csv", f, "text/csv")},
            )

        await VectorManager.rebuild(db)
        store = VectorManager.get_store()
        assert store is not None

        svc = EmbeddingService()
        hits = store.search(svc.encode("Laptop sales"), top_k=3)
        assert len(hits) > 0
        assert "document" in hits[0]
        assert "score" in hits[0]


class TestCopilotRAGIntegration:
    @pytest.mark.asyncio
    async def test_copilot_returns_sources_after_ingest(
        self, db, admin_client, sample_csv
    ):
        with open(sample_csv, "rb") as f:
            await admin_client.post(
                "/ingest/csv",
                files={"file": ("sales.csv", f, "text/csv")},
            )

        resp = await admin_client.post(
            "/copilot/query",
            json={"question": "What are the total sales?"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "answer" in body
        assert "session_id" in body