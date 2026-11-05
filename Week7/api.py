"""FastAPI:  uvicorn api:app --reload"""

import shutil, tempfile
from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from Week7.core.ingestion.document_loader import ALLOWED
from Week7.core.rag_service import PipelineConfig, RAGService
from Week7.exceptions import IngestionError, LLMError, RAGError

app = FastAPI(title = "DOcument Intelligence RAG")
svc = RAGService()

class AskRequest(BaseModel):
    question: str = Field(min_length=1,max_length=2000)
    session_id: str = "default"
    filters: dict | None = None
    mode: str = "hybrid"
    use_rerank: bool = True

@app.get("/health")
def health():
    return {
        "status" : "OK"
    }

@app.get("/documents")
def documents():
    return svc.store.list_documents()

@app.post("/documents")
async def upload(file: UploadFile = File(...)):
    name = Path(file.filename or "").name
    if Path(name).suffix.lower() not in ALLOWED:
        raise HTTPException(400, f"Allowed types: {sorted(ALLOWED)}")
    with tempfile.TemporaryDirectory() as d:
        dest = Path(d) / name
        with dest.open("wb") as f:
            shutil.copyfileobj(file.file, f)
        try:
            return svc.ingest(dest)
        except IngestionError as e:
            raise HTTPException(422, str(e))

@app.delete("/documents/{document_id}")
def delete(document_id: str):
    svc.delete(document_id); return {
        "deleted": document_id
    }

@app.post("/ask")
def ask(req: AskRequest):
    try:
        return svc.ask(req.question, req.session_id, PipelineConfig(mode=req.mode, use_rerank=req.use_rerank), req.filters)
    except LLMError as e:
        raise HTTPException(502, str(e))
    except RAGError as e:
        raise HTTPException(400, str(e))