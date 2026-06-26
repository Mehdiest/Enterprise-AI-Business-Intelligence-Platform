"""
Disk persistence implementation.
"""

from __future__ import annotations

import pickle
from pathlib import Path

import faiss

from .base import BasePersistence


class DiskPersistence(
    BasePersistence,
):
    """
    Stores vector indexes on disk.
    """

    def __init__(
        self,
        directory: str = "storage/vector",
    ):
        self.directory = Path(directory)

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index_path = (
            self.directory / "index.faiss"
        )

        self.documents_path = (
            self.directory / "documents.pkl"
        )

    def exists(
        self,
    ) -> bool:

        return (
            self.index_path.exists()
            and self.documents_path.exists()
        )

    def save(
        self,
        index,
        documents: list,
    ) -> None:

        faiss.write_index(
            index,
            str(self.index_path),
        )

        with open(
            self.documents_path,
            "wb",
        ) as file:

            pickle.dump(
                documents,
                file,
            )

    def load(
        self,
    ) -> tuple:

        index = faiss.read_index(
            str(self.index_path)
        )

        with open(
            self.documents_path,
            "rb",
        ) as file:

            documents = pickle.load(
                file
            )

        return (
            index,
            documents,
        )