# Create known queries and expected documents

from Week6.utils import EVALUATION_DATASET

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