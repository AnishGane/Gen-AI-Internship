# Create known queries and expected documents

from Week6.models import EvaluationQuery

EVALUATION_DATASET = [

    EvaluationQuery(
        query="What is Python used for?",
        expected_sources={"python.txt"},
    ),

    EvaluationQuery(
        query="What is React?",
        expected_sources={"React.txt"},
    ),

    EvaluationQuery(
        query="How is React used?",
        expected_sources={"React.txt"},
    ),

    EvaluationQuery(
        query="Which language is used for artificial intelligence?",
        expected_sources={"python.txt"},
    ),

]

def main():

    print("=" * 20)
    print("WEEK 6 - EVALUATION DATASET")
    print("=" * 20)

    for index, item in enumerate(
        EVALUATION_DATASET,
        start=1,
    ):

        print(f"\nQuery {index}")
        print(f"Question: {item.query}")
        print(
            f"Expected sources: "
            f"{', '.join(item.expected_sources)}"
        )


if __name__ == "__main__":
    main()