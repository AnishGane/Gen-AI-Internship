from openai import OpenAI

from Week6.config import API_KEY, BASE_URL, EMBEDDING_MODEL
from Week6.exceptions import EmbeddingError
from Week5.logger import logger

class EmbeddingService:
    """
    Handles the text embeddiding operations.
    """

    def __init__(self):
        if not API_KEY:
            raise EmbeddingError(
                "API_KEY is not configured."
            )
        
        if not BASE_URL:
            raise EmbeddingError(
                "BASE_URL is not configured."
            )

        if not EMBEDDING_MODEL:
            raise EmbeddingError(
                "EMBEDDING_MODEL is not configured."
            )

        self.client = OpenAI(
            api_key=API_KEY,
            base_url=BASE_URL
        )
        
        self.model = EMBEDDING_MODEL

def embed_text(self,text: str) -> list[float]:
    """
    Generate an embedding for single text.
    """

    if not text.strip():
        raise EmbeddingError(
                "Cannot generate embedding for empty text."
            )
    
    try:
        response = self.client.embeddings.create(
            model=self.model,
            input=text
            encoding_format="float"
        )

        vector = response.data[0].embedding

        logger.info(
            "Generated embedding with dimension %d",
            len(vector)
        )

        return vector

    except Exception as exc:
            logger.exception(
                "Failed to generate embedding"
            )

            raise EmbeddingError(
                "Failed to generate text embedding."
            ) from exc
        
def embed_batch(self, texts: list[str]) -> list[list[float]]:
    """
    Generate an embedding for multiple texts.
    """

    def __init__(self):
        if not texts:
            raise EmbeddingError(
                "Cannot generate embedding for empty text."
            )
            
        if any(not text.strip() for text in texts):
            raise EmbeddingError(
                "Input contains empty text."
            )

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
                encoding_format="float"
            )

            vectors = [result.embedding for result in response.data]

            logger.info(
                "Generated embedding with dimension %d",
                len(vectors[0])
            )

            return vectors
        
        except Exception as exc:
            logger.exception(
                "Failed to generate batch embeddings"
            )

            raise EmbeddingError(
                "Failed to generate batch embeddings."
            ) from exc