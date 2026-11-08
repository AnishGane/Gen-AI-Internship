# LangGraph overview

LangGraph orchestrates stateful workflows as graphs. A StateGraph has shared state (a TypedDict), nodes (functions that return state updates) and edges (fixed or conditional transitions between nodes).

Reducers such as operator.add or add_messages define how concurrent or repeated updates to a state key are merged.

Checkpointing saves the graph state after every step. A thread_id identifies one workflow instance, so many conversations can run independently and be resumed later. InMemorySaver is for development; SQLite or Postgres savers persist across restarts.

Human-in-the-loop uses interrupt() to pause a graph and Command(resume=...) to continue it after a person approves, rejects or edits the pending action. A checkpointer is required for interrupts.
