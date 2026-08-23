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
