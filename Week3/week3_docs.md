# Week3 - Working with LLM APIs - Notes

---

## Week 2 → Week 3 Carryover

These Week 3 task-list items were already covered in Week 2 — noted here for the record rather than redone:

| Week 3 task                        | Covered in                                                                          |
| ---------------------------------- | ----------------------------------------------------------------------------------- |
| CLI chatbot sending input to API   | `Week2/day6/11_mini_chatbot.py`                                                     |
| System prompt for role/personality | `Week2/day2/03_system_vs_user_prompt.py`                                            |
| Conversation history across turns  | `Week2/day4/07_multiturn_conversation.py`                                           |
| Temperature/max_tokens experiments | `Week2/day1/02_temperature_experiment.py`, `Week2/day3/06_context_window_limits.py` |

**Week 3** instead goes deeper into what makes an LLM integration production-grade: CLI design, tool use, logging, testing, and concurrency.

---

## Day1 - CLI Design with `argparse`

**Concept:** Real CLI takes flags instead of hardcoded values or ineractive `input()` prompts - this makes the scripts scriptable, automatable, and usable in pipelines.

```python
parser = argparse.ArgumentParser(description="A configurable chatbot.")
parser.add_argument("--prompt", type=str, required=True)
parser.add_argument("--temperature", type=float, default=0.7)
args = parser.parse_args()
```

Run: `uv run Week3/day1/01_cli_chatbot_w_argparse.py --prompt "..." --temperature 0.3`

Also introduced: a `ChatSession` class — bundling model config + history into one reusable object instead of loose functions and a raw list.

**What each parameter changes:**

- `--temperature` — output randomness (0.0 = focused/repeatable, 1.0 = varied).
- `--max-tokens` — hard cap on reply length; too low → truncated output (`finish_reason: "length"`).
- `--system` — the model's role/persona for the whole exchange.
- `--model` — which underlying model handles the request.
