"""Day 2 / Task 1 - custom tools with @tool: name, description and schema are what the model sees."""
from Week8.core.tools import calculator, get_current_datetime, search_text

def main():
    for t in (calculator, get_current_datetime, search_text):
        print("-" * 60)
        print("name       :", t.name)
        print("description:", t.description)
        print("args schema:", t.args)

    print("\ncalculator   ->", calculator.invoke({"expression": "(12 + 8) * 3"}))
    print("div by zero  ->", calculator.invoke({"expression": "1/0"}))
    print("injection    ->", calculator.invoke({"expression": "__import__('os').system('echo hacked')"}))
    print("datetime     ->", get_current_datetime.invoke({}))
    print("search_text  ->", search_text.invoke({"query": "what is a checkpointer thread_id"})[:300])

if __name__ == "__main__":
    main()
