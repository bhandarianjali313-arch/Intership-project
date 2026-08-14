from pathlib import Path
import json


# -------------------------------------------------------
# Project paths
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

CUAD_JSON = DATA_DIR / "CUADv1.json"
TRAIN_JSON = DATA_DIR / "train_separate_questions.json"
TEST_JSON = DATA_DIR / "test.json"


# -------------------------------------------------------
# Utility
# -------------------------------------------------------

def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_json(path: Path):
    """Load a JSON file safely."""

    if not path.exists():
        print(f"File not found: {path}")
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# -------------------------------------------------------
# Path check
# -------------------------------------------------------

def check_paths() -> None:
    print_header("DATASET PATH CHECK")

    paths = {
        "Data directory": DATA_DIR,
        "CUADv1.json": CUAD_JSON,
        "Train dataset": TRAIN_JSON,
        "Test dataset": TEST_JSON,
    }

    for name, path in paths.items():
        status = "FOUND" if path.exists() else "MISSING"

        print(f"{name:<25}: {status}")
        print(f"  {path}")


# -------------------------------------------------------
# Generic JSON inspection
# -------------------------------------------------------

def inspect_json_file(path: Path, name: str) -> None:

    print_header(f"{name} INSPECTION")

    data = load_json(path)

    if data is None:
        return

    print(f"Python type: {type(data).__name__}")

    if isinstance(data, dict):

        print("\nTop-level keys:")

        for key in data.keys():
            print(f" - {key}")

        if "data" in data:

            documents = data["data"]

            print(f"\nDocuments: {len(documents)}")

            if documents:

                first_document = documents[0]

                print("\nFirst document keys:")

                for key in first_document.keys():
                    print(f" - {key}")

    elif isinstance(data, list):

        print(f"\nNumber of records: {len(data)}")

        if data:

            first_record = data[0]

            print("\nFirst record type:")
            print(type(first_record).__name__)

            if isinstance(first_record, dict):

                print("\nFirst record keys:")

                for key in first_record.keys():
                    print(f" - {key}")


# -------------------------------------------------------
# CUAD detailed inspection
# -------------------------------------------------------

def inspect_cuad_structure() -> None:

    print_header("CUAD DETAILED STRUCTURE")

    data = load_json(CUAD_JSON)

    if data is None:
        return

    documents = data.get("data", [])

    print(f"Total documents: {len(documents)}")

    if not documents:
        return

    document = documents[0]

    print("\nFirst contract title:")
    print(document.get("title"))

    paragraphs = document.get("paragraphs", [])

    print(f"\nParagraph groups: {len(paragraphs)}")

    if not paragraphs:
        return

    paragraph = paragraphs[0]

    print("\nParagraph keys:")

    for key in paragraph.keys():
        print(f" - {key}")

    context = paragraph.get("context", "")

    print(f"\nContract text length: {len(context):,} characters")
    print(f"Approximate words: {len(context.split()):,}")

    print("\nFirst 500 characters of contract:")
    print("-" * 80)
    print(context[:500])


# -------------------------------------------------------
# Annotation inspection
# -------------------------------------------------------

def inspect_annotations() -> None:

    print_header("CUAD ANNOTATION EXAMPLE")

    data = load_json(CUAD_JSON)

    if data is None:
        return

    documents = data.get("data", [])

    if not documents:
        return

    paragraphs = documents[0].get("paragraphs", [])

    if not paragraphs:
        return

    qas = paragraphs[0].get("qas", [])

    print(f"Questions / clause categories: {len(qas)}")

    if not qas:
        return

    qa = qas[0]

    print("\nAnnotation keys:")

    for key in qa.keys():
        print(f" - {key}")

    print("\nQuestion / clause:")
    print(qa.get("question"))

    print("\nID:")
    print(qa.get("id"))

    answers = qa.get("answers", [])

    print(f"\nNumber of answers: {len(answers)}")

    if answers:

        for index, answer in enumerate(answers[:3], start=1):

            print(f"\nAnswer {index}")
            print("-" * 40)

            print("Text:")
            print(answer.get("text"))

            print("\nAnswer start:")
            print(answer.get("answer_start"))


# -------------------------------------------------------
# Count clause categories
# -------------------------------------------------------

def inspect_clause_categories() -> None:

    print_header("CLAUSE CATEGORY SUMMARY")

    data = load_json(CUAD_JSON)

    if data is None:
        return

    documents = data.get("data", [])

    questions = set()

    total_questions = 0
    total_answers = 0

    for document in documents:

        for paragraph in document.get("paragraphs", []):

            for qa in paragraph.get("qas", []):

                question = qa.get("question")

                if question:
                    questions.add(question)

                total_questions += 1

                total_answers += len(
                    qa.get("answers", [])
                )

    print(f"Contracts            : {len(documents)}")
    print(f"Total QA entries     : {total_questions}")
    print(f"Unique questions     : {len(questions)}")
    print(f"Total answer spans   : {total_answers}")

    print("\nFirst 10 unique clause questions:")

    for index, question in enumerate(
        sorted(questions)[:10],
        start=1
    ):
        print(f"{index}. {question}")


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main() -> None:

    print_header("CUAD DATASET INSPECTION")

    check_paths()

    inspect_json_file(
        CUAD_JSON,
        "CUADv1.json"
    )

    inspect_json_file(
        TRAIN_JSON,
        "train_separate_questions.json"
    )

    inspect_json_file(
        TEST_JSON,
        "test.json"
    )

    inspect_cuad_structure()

    inspect_annotations()

    inspect_clause_categories()


if __name__ == "__main__":
    main()