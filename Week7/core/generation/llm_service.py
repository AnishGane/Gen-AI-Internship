"""OpenAI-compatible LLM wrapper for OpenRouter."""
import time
import openai

from openai import OpenAI
from Week7.config import settings
from Week7.exceptions import LLMError
from Week7.logger import get_logger, log_event

log = get_logger("llm")

class LLMService:
    def __init__(self):
        settings.validate_for_llm()

        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.base_url,
            timeout=settings.llm_timeout_s,
            max_retries=0, 
        )

        self.usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "calls": 0,
        }

    def complete(self, system: str, user: str, max_tokens: int = 1024, temperature: float = 0.0) -> str:
        last_error = None

        for attempt in range(1, settings.llm_max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model = settings.llm_model,
                    messages = [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                )

                if response.usage:
                    self.usage["input_tokens"] += response.usage.prompt_tokens or 0
                    self.usage["output_tokens"] += response.usage.completion_tokens or 0

                self.usage["calls"] += 1

                answer = response.choices[0].message.content
                return answer or ""

            except (
                openai.APIConnectionError,
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.InternalServerError,
            ) as error:
                last_error = error
                log_event(
                    log,
                    "llm_retry",
                    attempt=attempt,
                    error=str(error),
                )

                if attempt < settings.llm_max_retries:
                    time.sleep(2**attempt)

            except openai.APIError as error:
                raise LLMError(str(error)) from error

        raise LLMError(f"LLM failed after retries: {last_error}")
