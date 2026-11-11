<!-- uv run pytest .\tests\test_qdrant_vectorstore.py -v -->

# Week 8 - Learning Langchain & LangGraph

**`routes.py`** [Take me there](api/)

This code defines `FastAPI` endpoints for checking the service, sending a question to a RAG workflow, and retrieving a conversation’s history.

**Imports**

- `time` measures how long a chat request takes.
- FastAPI’s `APIRouter`, `HTTPException`, and `Request` define routes, return HTTP errors, and access the running application.
- `ConfigError` and `RetrievalError` represent expected configuration and retrieval failures.
- `get_logger` creates the API logger.
- `ChatRequest`, `ChatResponse`, and `Source` define the request and response data structures.
- `ask` runs the Week 8 RAG workflow.

**Router and logger**

```python
log = get_logger("api")
router = APIRouter()
```

The router groups these endpoints so the application can include them elsewhere. The logger records errors and workflow failures.

**Health endpoint**

```python
@router.get("/health")
def health():
    return {"status": "OK"}
```

`GET /health` returns a simple status response. It can be used to check whether the API is responding.

**Chat endpoint**

```python
@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):
```

`POST /chat` accepts a `ChatRequest` and returns a response validated against `ChatResponse`.

**Workflow execution**

```python
graph = request.app.state.graph
start = time.perf_counter()

state = ask(graph, req.question, req.thread_id, {"tags": ["week8", "api"]})
```

The endpoint gets the workflow graph from application `state`, starts a `timer`, and calls `ask` with:
- The workflow graph
- The user’s question
- The conversation’s thread ID
- Metadata tags identifying this request as Week 8 API traffic
The returned `state` is expected to contain fields such as `answer`, `status`, and `route`.

**Building the response**

```python
latency = int((time.perf_counter() - start) * 1000)
```

This calculates elapsed time in milliseconds.

The endpoint then builds a `ChatResponse` containing:
- The thread ID
- The generated answer
- The workflow status and route
- Sources converted into Source objects
- The number of attempts, defaulting to `0`
- Any rewrites, defaulting to an empty list
- Request latency in milliseconds

**Thread history endpoint**

```python
@router.get("/threads/{thread_id}/history")
def history(thread_id: str, request: Request):
```

`GET /threads/{thread_id}/history` retrieves stored messages for the given thread.

```python
snapshot = request.app.state.graph.get_state(
    {"configurable": {"thread_id": thread_id}}
)
```

The endpoint asks the graph for the saved state associated with that thread ID.

```python
msgs = snapshot.values.get("messages", []) if snapshot.values else []
```

If the snapshot contains values, it reads the `messages` entry. If not, it uses an empty list.

The response includes the thread ID and each message’s type and content:

```python
{
  "thread_id": "example-thread",
  "messages": [
    {
      "role": "human",
      "content": "Example question"
    }
  ]
}
```

**Request flow**
1. A client checks `GET /health` or sends a question to `POST /chat`.
2. For chat, the API passes the question and thread ID to the RAG workflow.
3. The workflow’s result is converted into a typed response with sources and timing information.
4. The client can request `GET /threads/{thread_id}/history` to retrieve the thread’s saved messages.

---

**`tools.py`** [Take me there](\core)

This module defines three tools that a LangChain-based assistant can call:
1. A calculator for arithmetic
2. A tool that returns the current UTC date and time
3. A keyword search over local Markdown documents
The `@tool` decorator turns a Python function into a LangChain tool. This makes its name, description, and input available to the model so it can choose when to call it.

**Imports and document directory**

```python
import ast
import operator
import re
from datetime import datetime, timezone
from pathlib import Path
from langchain_core.tools import tool
```

- `ast` parses arithmetic expressions into a syntax tree.
- `operator` supplies Python’s arithmetic operations.
- `re` handles regular-expression searches and paragraph splitting.
- `datetime` and `timezone` provide the current UTC time.
- `Path` builds filesystem paths.
- `tool` converts functions into LangChain tools.

**Calculator safety and allowed operations**

```python
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}
```

This mapping lists the arithmetic operations the calculator allows: addition, subtraction, multiplication, division, powers, modulo, floor division, and unary plus or minus.

`safe_eval`

```python
def safe_eval(expression: str) -> float:
```

This function evaluates an arithmetic expression without calling Python’s `eval()`. It parses the expression into an abstract syntax tree (AST), then walks the tree and accepts only:
- `Numeric constants`
- Binary arithmetic operations from `_OPS`
- Unary `plus` and `minus`
Anything else, such as a `function call` or `variable name`, `raises ValueError("unsupported expression")`.

It also tries to limit large operands and exponents. One detail to review: because of operator precedence, this condition

```python
if isinstance(node.op, ast.Pow) and abs(right) > 100 or abs(left) > 10**6:
```

means `“reject a power with an exponent above 100, or reject any operation whose left operand exceeds one million.”` 

`calculator`

```python
@tool
def calculator(expression: str) -> str:
```

This exposes the `calculator` as a LangChain tool. It calls `safe_eval()` and returns the result as text.

If division by zero occurs, it returns `"Error: division by zero"`. Other errors are also returned as text, which lets the assistant see that the calculation failed and respond or try again.

**Current date and time**

```python
@tool
def get_current_datetime() -> str:
```

This LangChain tool returns the current time in UTC as an ISO-formatted string, for example:

```text
2026-11-10T12:34:56+00:00
```

It is intended for questions about the current date or time. Because it always uses UTC, the result may differ from the user’s local time.

`Reading local documents`

`_paragraphs`

```python
def _paragraphs() -> list[tuple[str, str]]:
```

This helper reads every `.md` file in `KB_DIR`, in sorted filename order. It splits each file on blank lines and returns pairs of:
- The document filename
- A non-empty paragraph from that document
This function is an internal helper, not a LangChain tool, because it has no `@tool` decorator.

`search_text`

```python
@tool
def search_text(query: str) -> str:
```

This exposes local document search as a LangChain tool.

It:
1. Extracts words from the query and lowercases them.
2. Ignores terms shorter than three characters.
3. Extracts words from each document paragraph.
4. Scores a paragraph by how many query terms it shares.
5. Sorts paragraphs by score and returns up to three matches, including their filenames.
If no paragraph contains any query terms, it returns `"No matching text found."`

**What the three LangChain tools do**

| Tool | Input | Purpose |
|---|---|---|
| `calculator` | An arithmetic expression | Safely evaluates supported arithmetic |
| `get_current_datetime` | None | Returns the current UTC date and time |
| `search_text` | A keyword query | Finds matching paragraphs in local Markdown files |

**LangChain tool flow**

A typical setup binds the tools to a chat model or provides them to an agent. The model receives the tool names, descriptions, and input schemas. When it requests a tool call, your application runs the corresponding Python function and passes the result back to the model.

---

**`agents.py`** [Take me there](\lc)

It creates a `LangChain agent` and gives it a `language model`, a set of `tools`, and instructions for choosing when to use those tools.

**Imports**

```python
from langchain.agents import create_agent
from Week8.core.llm import get_llm
from Week8.core.tools import calculator, get_current_datetime, search_text
```

- `create_agent` builds an agent using LangChain’s agent interface.
- `get_llm()` returns the language model configured in [llm.py](\core\llm.py).
- The other imports are the `calculator`, `date/time`, and `local document search` tools.

**System prompt**

```python
SYSTEM_PROMPT = (
    "You are a helpful assistant with tools. Use `calculator` for ANY arithmetic, "
    "a search tool for knowledge questions, and `get_current_datetime` for date/time. "
    "Never guess numbers. If tools return nothing useful, say so."
)
```

The system prompt gives the `agent` its instructions:
- Use the calculator for arithmetic.
- Search local documents for knowledge questions.
- Use the date/time tool for current date or time.
- Avoid guessing numbers.
- Say when the tools do not provide a useful answer.

These instructions guide the model, but they do not enforce the rules by themselves. For example, if it is essential that every arithmetic question use the calculator, the application should also check or constrain the agent’s behavior.

`build_agent`

```python
def build_agent(tools: list | None = None, checkpointer=None):
```

This function creates and returns an agent.

**Choosing tools**

```python
tools = tools or [calculator, get_current_datetime, search_text]
```

If the caller supplies a non-empty tool list, the agent uses that list. Otherwise, it uses the three default tools.

Because this uses `or`, passing an empty list also selects the defaults.

**Creating the agent**

```python
return create_agent(
    model=get_llm(),
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer
)
```

The agent is created with:
- `Model`: The language model returned by get_llm().
- `Tools`: Functions the agent can request the application to run.
- `System prompt`: Instructions that guide the agent.
- `Checkpointer`: Optional storage for saving and restoring agent state.

**LangChain**

> LangChain is a framework for building applications that use language models. It provides interfaces for connecting models to prompts, tools, and workflow components.

**Agent**

> An agent uses a language model to decide what to do during a task. It can answer directly or request one or more tools. The application runs each requested tool and returns its result to the model.

For example, for “What is 17 × 24?”, the agent can request the calculator, receive its result, and use that result in its response.

**Tools**

> A tool is a function exposed to the model with a name, description, and input format. The model can request a tool call, but your application executes the Python function.

**What a checkpointer does?**

A checkpointer saves `agent state` so it can be restored later. Depending on the workflow and configuration, that state may include `conversation messages` and `other information` the agent needs to continue.

A checkpointer is useful when you want a conversation to continue across multiple requests. The application typically supplies a stable thread or session identifier when invoking the agent so it can load the saved state for that conversation.

If no checkpointer is provided, this code does not configure persistence through this parameter. The agent may still process the current invocation, but you should not rely on this setup to restore conversation state between separate requests.

**Memory and SQLite checkpointers**

The exact classes and setup depend on the LangChain and LangGraph versions used in the project. Commonly, checkpointers are provided by `LangGraph`.

**In-memory checkpointer**

An in-memory checkpointer stores state in the running process.
- Useful for local development, demos, and short-lived sessions.
- Usually loses saved state when the process restarts.
- Does not share state across separate application workers.

**SQLite checkpointer**

A SQLite checkpointer stores state in a local SQLite database.
- Useful for local applications or small deployments that need state to survive process restarts.
- Can restore saved state when the application reconnects to the same database.
- Requires a database file and suitable setup.
- It is still local storage; deployments with multiple servers may need a shared database or another storage backend.
A checkpointer’s persistence is associated with a conversation or thread identifier. If different conversations use different identifiers, their saved states stay separate.

**Where to configure it?**

This function accepts the checkpointer but does not create one:

```python
agent = build_agent(checkpointer=my_checkpointer)
```

The application that calls `build_agent` is responsible for `choosing` and `configuring an in-memory`, `SQLite`, or other checkpointer. It also needs to pass the correct thread identifier when invoking the agent if it expects the conversation to resume.

---

**`chains,py`** [Take me there](\lc)

**Reusable LangChain Chains**

This module defines two reusable chains using `LCEL`, `LangChain’s expression language` for connecting components into a processing pipeline.

The `|` operator passes each component’s output into the next component. For example:

```text
prompt | model | parser
```

means: format a prompt, send it to a model, then parse the model’s response.

**Imports**

```python
from langchain_core.output_parsers import StrOutputParser
from Week8.core.llm import get_llm
from Week8.core.prompts import EXTRACTION_PROMPT
from Week8.models import Extracted_info
```

- `StrOutputParser` converts a model response into plain text.
- `get_llm()` returns the configured chat model.
- `EXTRACTION_PROMPT` provides instructions for extracting information from text.
- `Extracted_info` is a Pydantic model used to validate structured extraction results.

**Structured extraction chain**

```python
def build_extraction_chain():
    """text -> prompt -> model(structured) -> ExtractedInfo (Pydantic-validated)."""
    structured_llm = get_llm().with_structured_output(
        Extracted_info,
        method="function_calling"
    )
    return EXTRACTION_PROMPT | structured_llm
```

This function builds a chain that takes text, asks the model to extract information, and returns the result in the structure defined by `Extracted_info`.

`with_structured_output(...)` configures the model to produce data matching that schema. The `"function_calling"` method asks the model provider to return structured data through its function-calling feature. LangChain then validates the result against the Pydantic model.

The chain is assembled as:

```python
EXTRACTION_PROMPT → structured model
```

The chain’s input must match the variables expected by `EXTRACTION_PROMPT`. Its output is typically an `Extracted_info` instance, or a validation/provider error if the output cannot be parsed into the required structure.

**Plain-text chain**

```python
def build_text_chain(system: str = "You are a concise assistant."):
```

This function builds a conversational chain that returns plain text. The `system` argument lets the caller customize the assistant’s instructions.

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", system),
    ("human", "{question}")
])
```

The prompt has two messages:
- A system message containing the `system` instructions.
- A human message whose `{question}` placeholder is filled with the chain’s input.

```python
return prompt | get_llm(temp=0.3) | StrOutputParser()
```

The chain runs through three steps:
1. `Prompt`: Combines the system instructions with the supplied question.
2. `Model`: Generates a response using the configured language model at temperature 0.3.
3. `Parser`: Converts the model output into a plain Python string.

For example, a caller might invoke the chain with:

```python
chain.invoke({"question": "Explain retrieval-augmented generation."})
```

The result is a string containing the model’s answer. Since the output parser handles chunks as text, this chain can also be used in streaming demos.

**Summary**

| Chain | Input | Processing | Output |
|---|---|---|---|
| `build_extraction_chain()` | Values required by `EXTRACTION_PROMPT` | Prompt → structured model output | Pydantic-validated `Extracted_info` |
| `build_text_chain(system)` | A `question` string in a dictionary | Prompt → model → string parser | Plain-text string |

The functions return configured chains; they do not run them. A caller runs a chain with methods such as `.invoke(...)` or `.stream(...)`.

---