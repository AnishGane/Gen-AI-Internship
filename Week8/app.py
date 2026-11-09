import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from Week8.logger import get_logger
from Week8.api.routes import router
from Week8.lg.memory import get_checkpointer
from Week8.RAG.workflow import build_rag_graph

log = get_logger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.graph = build_rag_graph(checkpointer=get_checkpointer(), adaptive=True)  # built once, reused
    log.info("graph ready")
    yield

app = FastAPI(title="Agentic RAG Knowldege Assistant", lifespan=lifespan)
app.include_router(router)

@app.middleware("http")
async def access_log(request: Request, call_next):
    rid, start = uuid.uuid4().hex[:8], time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    log.info("%s %s -> %d (%d ms) rid=%s", request.method, request.url.path, response.status_code,
             (time.perf_counter() - start) * 1000, rid)
    return response