import time
from fastapi import APIRouter, HTTPException, Request
from Week8.exceptions import ConfigError, RetrievalError
from Week8.logger import get_logger
from Week8.models import ChatRequest, ChatResponse, Source
from Week8.RAG.workflow import ask

log = get_logger("api")
router = APIRouter()

@router.get("/health")
def health():
    return {
        "status": "OK"
    }

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, request: Request):
    graph = request.app.state.graph
    start = time.perf_counter()

    try:
        state = ask(graph, req.question, req.thread_id, {"tags": ["week8", "api"]})
        pass
    except ConfigError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except RetrievalError as exc:
        log.error("retrieval failed: %s", exc)
        raise HTTPException(status_code=502, detail="Vector store unavailable") from exc
    except Exception:
        log.exception("workflow failed (thread=%s)", req.thread_id)  # do not log the user's question text
        raise HTTPException(status_code=502, detail="The model provider failed. Try again.")
    latency = int((time.perf_counter() - start) * 1000)
    return ChatResponse(
        thread_id=req.thread_id, answer=state["answer"], status=state["status"], route=state["route"],
        sources=[Source(**s) for s in state.get("sources", [])], attempts=state.get("attempts", 0),
        rewrites=state.get("rewrites", []), latency_ms=latency)

# single user endpoint
@router.get("/threads/{thread_id}/history")
def history(thread_id: str, request: Request):

    snapshot = request.app.state.graph.get_state(
        {"configurable": {"thread_id": thread_id}}
    )

    msgs = snapshot.values.get("messages", []) if snapshot.values else []

    return {
        "thread_id": thread_id,
        "messages": [
            {"role": m.type, "content": m.content}
            for m in msgs
        ]
    }