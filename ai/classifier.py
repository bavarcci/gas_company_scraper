"""
classifier.py

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class ClassificationResult:
    categories: List[str]
    confidence: float
    reasoning: str


class AIProductClassifier:

    def __init__(self, model_client):
        """
        model_client should expose a classify(text) method.
        """
        self.client = model_client

    def classify(self, text: str) -> ClassificationResult:
        """
        Classify extracted company/product text.
        """

        if not text.strip():
            return ClassificationResult(
                categories=[],
                confidence=0.0,
                reasoning="No text provided."
            )

        response = self.client.classify(text)

        return ClassificationResult(
            categories=response["categories"],
            confidence=response["confidence"],
            reasoning=response.get("reasoning", "")
        )