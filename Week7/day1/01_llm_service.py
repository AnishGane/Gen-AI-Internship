import ssl
import httpx
import truststore

from openai import OpenAI
from Week7.config import BASE_URL, API_KEY, CHAT_MODEL

class LLMService:
    def __init__(self):
        ssl_context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        self.http_client = httpx.Client(
            verify=ssl_context,
        )

        self.openai_client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
            http_client=self.http_client,
        )

    def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        response = self.openai_client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        
        answer = response.choices[0].message.content

        if not answer or not answer.strip():
            raise RuntimeError("Failed to generate response")

        return answer
    
    def close(self):
        self.client.close()
        self.http_client.close()