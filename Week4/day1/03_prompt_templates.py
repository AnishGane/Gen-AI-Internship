"""
Reusable Prompt Templates (via OpenRouter)

Hardcoding prompt text inline doesn't scale once you have many prompts or need to reuse the same structure with different inputs. A PromptTemplate class separates FIXED instruction text from VARIABLE input, making prompts reusable, testable, and easy to version.
"""

import os
from string import Template
from openai import OpenAI
from Week2.config import BASE_URL, API_KEY, MODEL, MAX_TOKENS

client = OpenAI(
    base_url = BASE_URL, 
    api_key = API_KEY
)

class PromptTemplate:
    def __init__(self, name, template_text, system_prompt=None):
        self.name = name
        self.template = Template(template_text)
        self.system_prompt = system_prompt

    def render(self, **kwargs):
        return self.template.substitute(**kwargs)

    def run(self, **kwargs):
        prompt = self.render(**kwargs)
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(model=MODEL, max_tokens=MAX_TOKENS, messages=messages)
        return response.choices[0].message.content

SUMMARIZE_TEMPLATE = PromptTemplate(
    name="summarize_v1",
    system_prompt="Answer directly and concisely.",
    template_text="Summarize the following text in exactly $num_sentences sentences:\n\n$text",
)

CLASSIFY_TEMPLATE = PromptTemplate(
    name="classify_v1",
    system_prompt="Respond with only the single category label, nothing else.",
    template_text="Classify this message into one of these categories: $categories\n\nMessage: $text",
)

if __name__ == "__main__":
    sample_text = (
        "The new policy will take effect next month, requiring all employees "
        "to complete security training. Managers are responsible for tracking "
        "completion within their teams."
    )

    print("=== Using SUMMARIZE_TEMPLATE ===")
    print(SUMMARIZE_TEMPLATE.run(text=sample_text, num_sentences=1))

    print("\n=== Same template, different parameter ===")
    print(SUMMARIZE_TEMPLATE.run(text=sample_text, num_sentences=2))

    print("\n=== Using CLASSIFY_TEMPLATE ===")
    print(CLASSIFY_TEMPLATE.run(
        text=sample_text,
        categories="Announcement, Complaint, Question, Other",
    ))