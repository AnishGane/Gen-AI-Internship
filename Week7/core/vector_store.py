"""Qdrant wrapper: hybrid collection (dense + BM25 sparse), filters, delete-by-document."""
from qdrant_client import QdrantClient, models
from Week7.config import settings
from Week7.exceptions import RetrievalError
from Week7.models import RetrievedChunk, Chunk

PAYLOAD_FIELDS = ("document_id", "source", "chunk_id", "chunk_index", "page", "section", "text")

class VectorStore:
    def __init__(self, client: QdrantClient | None = None, collection: str | None = None):
        self.client = client or QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
        self.collection = collection or settings.collection_name

    # ---- setup (Day 5: NEW collection with sparse config; reindex from scratch) ----
    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection):
            return
        self.client.create_collection(
            self.collection,
            vectors_config={"dense": models.VectorParams(size=settings.dense_dim,
                                                         distance=models.Distance.COSINE)},
            sparse_vectors_config={"bm25": models.SparseVectorParams(modifier=models.Modifier.IDF)},
        )
        for f in ("document_id", "source"):
            self.client.create_payload_index(self.collection, f, models.PayloadSchemaType.KEYWORD)

    # ---- write ----
    def upsert(self, chunks: list[Chunk], dense: list[list[float]], sparse: list[models.SparseVector]):
        points = [
            models.PointStruct(id=c.point_id, vector={"dense": d, "bm25": s},
                               payload=c.model_dump(exclude={"point_id"}))
            for c, d, s in zip(chunks, dense, sparse)
        ]
        self.client.upsert(self.collection, points=points, wait=True)

    def delete_document(self, document_id: str) -> None:
        self.client.delete(self.collection, points_selector=models.FilterSelector(
            filter=models.Filter(must=[models.FieldCondition(
                key="document_id", match=models.MatchValue(value=document_id))])))

    def list_documents(self) -> dict[str, str]:
        docs, offset = {}, None
        while True:
            pts, offset = self.client.scroll(self.collection, limit=256, offset=offset,
                                             with_payload=["document_id", "source"])
            for p in pts:
                docs[p.payload["document_id"]] = p.payload["source"]
            if offset is None:
                return docs

     # ---- read ----
    @staticmethod
    def build_filter(filters: dict | None) -> models.Filter | None:
        if not filters:
            return None
        must = []
        for k, v in filters.items():
            match = models.MatchAny(any=v) if isinstance(v, (list, tuple, set)) else models.MatchValue(value=v)
            must.append(models.FieldCondition(key=k, match=match))
        return models.Filter(must=must)

    def search(self, *, mode: str, dense_vec=None, sparse_vec=None, limit: int = 10,
               filters: dict | None = None, score_threshold: float | None = None) -> list[RetrievedChunk]:
        flt = self.build_filter(filters)
        try:
            if mode == "dense":
                res = self.client.query_points(self.collection, query=dense_vec, using="dense",
                                               query_filter=flt, limit=limit,
                                               score_threshold=score_threshold, with_payload=True)
            elif mode == "sparse":
                res = self.client.query_points(self.collection, query=sparse_vec, using="bm25",
                                               query_filter=flt, limit=limit, with_payload=True)
            elif mode == "hybrid":  # server-side RRF fusion
                res = self.client.query_points(
                    self.collection,
                    prefetch=[
                        models.Prefetch(query=dense_vec, using="dense", limit=limit * 2, filter=flt),
                        models.Prefetch(query=sparse_vec, using="bm25", limit=limit * 2, filter=flt),
                    ],
                    query=models.FusionQuery(fusion=models.Fusion.RRF),
                    limit=limit, with_payload=True)
            else:
                raise RetrievalError(f"Unknown mode: {mode}")
        except RetrievalError:
            raise
        except Exception as e:
            raise RetrievalError(f"Qdrant search failed: {e}") from e
        return [RetrievedChunk(point_id=str(p.id), score=p.score,
                               **{k: p.payload.get(k) for k in PAYLOAD_FIELDS if p.payload.get(k) is not None})
                for p in res.points]