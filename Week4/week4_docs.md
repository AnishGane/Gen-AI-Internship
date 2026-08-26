# Week 4 — Prompt Engineering Deep Dive + Mini Project — Notes

---

## Week 2/3 → Week 4 Carryover

These Week 4 task-list items overlap with earlier weeks — noted for the record rather than redone:

| Week 4 task                               | Covered in                               |
| ----------------------------------------- | ---------------------------------------- |
| Zero-shot / few-shot examples             | `Week2/day5/09_zero_shot_vs_few_shot.py` |
| Step-by-step reasoning (chain-of-thought) | `Week2/day5/10_chain_of_thought.py`      |
| Structured (JSON) output, basic           | `Week2/day5/11_structured_output.py`     |

Week 4 instead goes deeper: making prompting techniques **reliable** (self-consistency, schema validation, self-correction) rather than just functional, then applies all of it in one deliverable project.

---

## Day 1 — Advanced Prompting Techniques

### Task 1 — Self-Consistency (Majority-Vote Reasoning)

**Concept:** Chain-of-thought asks the model to reason once. Self-consistency runs the _same_ reasoning prompt multiple times (with temperature > 0 so runs can differ), then takes the majority answer — trading more API calls for higher reliability on problems where the model sometimes slips.

```python
answers = []
for i in range(N_SAMPLES):
    response = get_answer(PROBLEM)  # temperature=0.7
    answers.append(extract_final_answer(response))
majority_answer, count = Counter(answers).most_common(1)[0]
```

Run: `uv run Week4/day1/01_self_consistency.py`

### Task 2 — Positive vs. Negative (Counter-)Examples

**Concept:** Few-shot prompts usually show only correct examples. Explicitly labeling _bad_ examples ("BAD: too vague...") can steer the model away from a specific failure mode more directly than positive examples alone.

Run: `uv run Week4/day1/02_positive_vs_negative_examples.py`

### Task 3 — Reusable Prompt Templates

**Concept:** Separating fixed instruction text from variable input (via a `PromptTemplate` class) makes prompts reusable, testable, and versionable — instead of hardcoding prompt text inline every time.

```python
class PromptTemplate:
    def __init__(self, name, template_text, system_prompt=None):
        self.template = Template(template_text)
        ...
    def run(self, **kwargs):
        prompt = self.template.substitute(**kwargs)
        ...
```

Run: `uv run Week4/day1/03_prompt_templates.py`

---

## Day 2 — Structured Output & Validation

### Task 1 — Pydantic Schema Validation

**Concept:** `json.loads()` only confirms text is valid JSON, not that it has the _right shape_. Pydantic validates structure AND types in one step.

```python
class ProductInfo(BaseModel):
    name: str
    price: float
    in_stock: bool

product = ProductInfo(**json.loads(raw_text))  # raises ValidationError if shape is wrong
```

Run: `uv run Week4/day2/04_pydantic_validation.py`

### Task 2 — Self-Correcting Retry Loop

**Concept:** Instead of giving up on invalid output, feed the validation error back to the model and ask it to fix its own response.

```python
except (json.JSONDecodeError, ValidationError) as e:
    messages.append({"role": "user", "content": f"That response was invalid: {e}. Please correct it."})
```

Run: `uv run Week4/day2/05_self_correcting_retry.py`

### Task 3 — Entity Extraction from Unstructured Text

**Concept:** A practical structured-output use case — pulling names, dates, and action items out of free-form notes into a defined schema.

Run: `uv run Week4/day2/06_entity_extraction.py`

---

## Day 3 — Prompt Engineering Best Practices

### Task 1 — Delimiters & Prompt Injection Awareness

**Concept:** Wrapping user-provided data in clear delimiters (e.g. `<data>` tags) helps the model separate instructions from data — and offers partial (not complete) resistance to injection attempts embedded in that data.

```python
prompt = f"""Summarize the text between <data> tags...
<data>
{user_provided_text}
</data>"""
```

Run: `uv run Week4/day3/07_delimiters_and_injection.py`

### Task 2 — Prompt Version Comparison Harness

**Concept:** A repeatable way to compare prompt wording (v1 vs v2) across multiple test inputs using an LLM judge, instead of eyeballing one example.

Run: `uv run Week4/day3/08_prompt_version_comparison.py`

---

## Day 4 — Mini Project: Smart Text Toolkit

**What it does:** a CLI tool combining everything from Weeks 1–4: `argparse` (Week 3), prompt structuring (Day 1), Pydantic validation (Day 2), and delimiter-based prompting (Day 3) — three tasks in one tool: summarize, extract key details, classify.

```bash
uv run .\Week4\day4\09_smart_text_toolkit.py --task summarize --text "..."
uv run .\Week4\day4\09_smart_text_toolkit.py --task extract --text "..."
uv run .\Week4\day4\09_smart_text_toolkit.py --task classify --text "..." --categories "Complaint,Question,Praise,Other"
uv run .\Week4\day4\09_smart_text_toolkit.py --task summarize --file notes.txt
```
