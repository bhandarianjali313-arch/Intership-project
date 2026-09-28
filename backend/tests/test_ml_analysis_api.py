import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient


# Add backend directory to Python path so that
# imports match the backend application's structure.
BACKEND_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(
        0,
        str(BACKEND_DIR),
    )


from app.routes.ml_analysis import (
    router,
    get_ml_service,
)


# ============================================================================
# FAKE ML SERVICE
# ============================================================================


class FakeMLService:
    """
    Lightweight fake service used so that API tests
    do not need to load the real trained model.
    """

    def health(self):

        return {
            "status":
                "ready",

            "classifier":
                "TF-IDF + Logistic Regression",

            "risk_scorer":
                "ContractRiskScorer",

            "vectorizer_available":
                True,

            "model_available":
                True,
        }


    def analyze_clause(
        self,
        text,
        top_k=3,
    ):

        text = " ".join(
            text.split()
        )

        if not text:
            raise ValueError(
                "Clause text cannot be empty."
            )

        return {
            "text":
                text,

            "classification": {
                "predicted_label":
                    "NON_COMPETE",

                "confidence":
                    0.91,

                "confidence_level":
                    "HIGH",

                "prediction_margin":
                    0.70,

                "ambiguous":
                    False,

                "requires_human_review":
                    False,

                "top_predictions": [
                    {
                        "rank":
                            1,

                        "label":
                            "NON_COMPETE",

                        "confidence":
                            0.91,
                    },
                    {
                        "rank":
                            2,

                        "label":
                            "EXCLUSIVITY",

                        "confidence":
                            0.09,
                    },
                ],
            },

            "risk": {
                "risk_level":
                    "HIGH",

                "risk_score":
                    3,

                "risk_reason":
                    (
                        "Potential restrictive "
                        "contractual obligation."
                    ),
            },
        }


    def analyze_clauses(
        self,
        clauses,
        top_k=3,
    ):

        if not isinstance(
            clauses,
            list,
        ):
            raise TypeError(
                "clauses must be a list."
            )

        if not clauses:
            raise ValueError(
                "At least one clause is required."
            )

        return [
            self.analyze_clause(
                clause,
                top_k=top_k,
            )
            for clause in clauses
        ]


# ============================================================================
# TEST APPLICATION
# ============================================================================


app = FastAPI()

app.include_router(
    router,
    prefix="/api/ml",
)


fake_service = FakeMLService()


def override_ml_service():
    return fake_service


app.dependency_overrides[
    get_ml_service
] = override_ml_service


client = TestClient(app)


# ============================================================================
# TESTS
# ============================================================================


def test_ml_health():

    response = client.get(
        "/api/ml/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"

    assert (
        data["model_available"]
        is True
    )


def test_analyze_single_clause():

    response = client.post(
        "/api/ml/analyze-clause",
        json={
            "text":
                (
                    "The employee shall not "
                    "compete with the company."
                ),

            "top_k":
                3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "classification"
        ][
            "predicted_label"
        ]
        == "NON_COMPETE"
    )

    assert (
        data[
            "classification"
        ][
            "confidence"
        ]
        == 0.91
    )

    assert (
        data[
            "risk"
        ][
            "risk_level"
        ]
        == "HIGH"
    )


def test_batch_clause_analysis():

    response = client.post(
        "/api/ml/analyze-clauses",
        json={
            "clauses": [
                (
                    "The employee shall not "
                    "compete with the company."
                ),
                (
                    "Neither party may assign "
                    "this agreement."
                ),
            ],

            "top_k":
                3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "total_clauses"
        ]
        == 2
    )

    assert len(
        data["results"]
    ) == 2


def test_batch_summary():

    response = client.post(
        "/api/ml/analyze-clauses",
        json={
            "clauses": [
                "First legal clause.",
                "Second legal clause.",
            ]
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data[
            "human_review_required"
        ]
        == 0
    )

    assert (
        data[
            "automatic_review_accepted"
        ]
        == 2
    )


def test_empty_clause_returns_400():

    response = client.post(
        "/api/ml/analyze-clause",
        json={
            "text":
                "   "
        },
    )

    assert response.status_code == 400


def test_empty_batch_returns_400():

    response = client.post(
        "/api/ml/analyze-clauses",
        json={
            "clauses":
                []
        },
    )

    assert response.status_code == 400


def test_invalid_top_k():

    response = client.post(
        "/api/ml/analyze-clause",
        json={
            "text":
                "Valid clause text.",

            "top_k":
                0,
        },
    )

    assert response.status_code == 422


def test_top_k_upper_limit():

    response = client.post(
        "/api/ml/analyze-clause",
        json={
            "text":
                "Valid clause text.",

            "top_k":
                11,
        },
    )

    assert response.status_code == 422