"""Agentic RAG workflow (LangGraph).

START -> prepare -> classify -+-> general_answer -> END
                              +-> retrieve -> [grade -> (good) generate | (weak) rewrite -> retrieve | (exhausted) fallback]
                                              generate -> END | fallback (insufficient evidence)
"""

