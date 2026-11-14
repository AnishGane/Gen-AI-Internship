# LangChain overview

LangChain is a framework of building blocks for LLM applications: chat models, prompt templates, output parsers, tools and retrievers.

LCEL (LangChain Expression Language) composes Runnables with the pipe operator, for example prompt | model | parser. Every Runnable supports invoke, stream, batch and their async versions.

Structured output lets a chat model return data that matches a Pydantic schema, so the result is validated JSON instead of free text.

Tool calling lets a model request a function call with JSON arguments. The application runs the tool and sends the result back to the model. An agent repeats this loop until the model can give a final answer.
