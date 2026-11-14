# InMemorySaver for dev, SQLite for persistence across restarts.

import sqlite3
from functools import lru_cache
from langgraph.checkpoint.memory import InMemorySaver
from Week10.config import settings

@lru_cache(maxsize=1)
def get_checkpointer(pointer: str | None = None):
    pointer = pointer or settings.checkpointer
    
    if pointer == "memory":
        return InMemorySaver()

    if pointer == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver

        conn = sqlite3.connect(
            settings.checkpoint_db,
            check_same_thread=False
        )

        checkpointer = SqliteSaver(conn)
        checkpointer.setup()

        return checkpointer

    raise ValueError(
        f"Unsupported checkpointer: {pointer}"
    )
