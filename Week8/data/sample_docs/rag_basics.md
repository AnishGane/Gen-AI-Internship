# RAG basics

Retrieval-augmented generation (RAG) retrieves relevant document chunks from a vector database and gives them to the model as context, so answers are grounded in your own data and can cite sources.

Agentic RAG adds decisions to the pipeline: a router decides whether retrieval is needed, a grader evaluates retrieved chunks, and a query rewriter improves the search query when retrieval is weak. Retries must be bounded so the loop always terminates.

When evidence is insufficient the assistant should use a fallback response and say it could not find the answer instead of guessing. Typical evaluation metrics are retrieval hit rate, answer faithfulness, correctness, latency and cost.
