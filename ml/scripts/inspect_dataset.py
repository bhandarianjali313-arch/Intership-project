from pathlib import Path
import json
import pandas as pd


# -------------------------------------------------------
# Project paths
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"

JSON_PATH = DATA_DIR / "CUAD_v1.json"
MASTER_CLAUSES_PATH = DATA_DIR / "master_clauses.csv"

TXT_DIR = DATA_DIR / "full_contract_txt"
PDF_DIR = DATA_DIR / "full_contract_pdf"
LABEL_DIR = DATA_DIR / "label_group_xlsx"


# -------------------------------------------------------
# Utility functions
# -------------------------------------------------------

def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def check_paths() -> None:
    print_header("DATASET PATH CHECK")

    paths = {
        "Data directory": DATA_DIR,
        "CUAD JSON": JSON_PATH,
        "Master clauses CSV": MASTER_CLAUSES_PATH,
        "TXT contracts": TXT_DIR,
        "PDF contracts": PDF_DIR,
        "Label XLSX": LABEL_DIR,
    }

    for name, path in paths.items():
        status = "FOUND" if path.exists() else "MISSING"
        print(f"{name:<25}: {status}")
        print(f"  {path}")


def count_files() -> None:
    print_header("CONTRACT FILE COUNTS")

    txt_files = list(TXT_DIR.glob("*.txt")) if TXT_DIR.exists() else []
    pdf_files = list(PDF_DIR.glob("*.pdf")) if PDF_DIR.exists() else []
    xlsx_files = list(LABEL_DIR.glob("*.xlsx")) if LABEL_DIR.exists() else []

    print(f"TXT contracts   : {len(txt_files)}")
    print(f"PDF contracts   : {len(pdf_files)}")
    print(f"XLSX label files: {len(xlsx_files)}")


def inspect_master_clauses() -> None:
    print_header("MASTER CLAUSES CSV")

    if not MASTER_CLAUSES_PATH.exists():
        print("master_clauses.csv not found.")
        return

    df = pd.read_csv(MASTER_CLAUSES_PATH)

    print(f"Shape: {df.shape}")

    print("\nColumns:")
    for column in df.columns:
        print(f" - {column}")

    print("\nFirst 5 rows:")
    print(df.head().to_string())

    print("\nMissing values:")
    print(df.isnull().sum())


def inspect_json() -> None:
    print_header("CUAD JSON STRUCTURE")

    if not JSON_PATH.exists():
        print("CUAD_v1.json not found.")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    print(f"Top-level Python type: {type(data).__name__}")

    if isinstance(data, dict):

        print("\nTop-level keys:")
        for key in data.keys():
            print(f" - {key}")

        if "data" in data:
            print(f"\nNumber of documents: {len(data['data'])}")

            if data["data"]:
                first_document = data["data"][0]

                print("\nFirst document keys:")
                for key in first_document.keys():
                    print(f" - {key}")


def inspect_first_contract() -> None:
    print_header("SAMPLE CONTRACT")

    if not TXT_DIR.exists():
        print("TXT contract directory not found.")
        return

    txt_files = list(TXT_DIR.glob("*.txt"))

    if not txt_files:
        print("No TXT contracts found.")
        return

    contract_path = txt_files[0]

    text = contract_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    print(f"Contract name : {contract_path.name}")
    print(f"Characters    : {len(text):,}")
    print(f"Words         : {len(text.split()):,}")

    print("\nFirst 1200 characters:\n")

    print(text[:1200])

def inspect_first_annotation() -> None:
    print_header("FIRST CUAD ANNOTATION")

    if not JSON_PATH.exists():
        return

    with open(JSON_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

    documents = data.get("data", [])

    if not documents:
        print("No documents found.")
        return

    first_document = documents[0]

    print("Document title:")
    print(first_document.get("title"))

    paragraphs = first_document.get("paragraphs", [])

    print(f"\nParagraph count: {len(paragraphs)}")

    if not paragraphs:
        return

    first_paragraph = paragraphs[0]

    context = first_paragraph.get("context", "")

    print(f"\nContext length: {len(context):,} characters")

    questions = first_paragraph.get("qas", [])

    print(f"Questions / clause labels: {len(questions)}")

    if not questions:
        return

    first_question = questions[0]

    print("\nFirst question:")
    print(first_question.get("question"))

    print("\nAnswers:")

    answers = first_question.get("answers", [])

    if not answers:
        print("No answer present.")
    else:
        for answer in answers[:3]:
            print(
                f"Text: {answer.get('text')}\n"
                f"Start position: {answer.get('answer_start')}\n"
            )


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main() -> None:

    print_header("CUAD DATASET INSPECTION")

    check_paths()

    count_files()

    inspect_master_clauses()

    inspect_json()

    inspect_first_contract()

    inspect_first_annotation()


if __name__ == "__main__":
    main()