# Naive Bayes classifier that predicts job category from text
# Trained on built-in keyword data from skills_db.py

import sys
import os
import logging
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.skills_db import NB_TRAINING_DATA

logger = logging.getLogger(__name__)


class JobCategoryClassifier:
    """
    Multinomial Naive Bayes classifier for job category prediction.

    Categories: Software Engineering, Data Science, Marketing,
                Finance, DevOps / Cloud, Cybersecurity

    Trained on lightweight built-in keyword corpus.
    """

    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.categories = list(NB_TRAINING_DATA.keys())
        self._is_trained = False

    def _build_training_data(self) -> tuple[list[str], list[str]]:
        """
        Build training corpus from NB_TRAINING_DATA dict.

        Returns:
            (texts, labels) lists
        """
        texts = []
        labels = []

        for category, samples in NB_TRAINING_DATA.items():
            for sample in samples:
                # Augment by repeating each sample 3x for better weighting
                texts.append(sample)
                labels.append(category)
                texts.append(sample + " " + sample)
                labels.append(category)

        return texts, labels

    def train(self) -> None:
        """
        Train the Naive Bayes model on built-in data.
        Called automatically on first predict() call.
        """
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.preprocessing import LabelEncoder

        texts, labels = self._build_training_data()

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),    # unigrams + bigrams
            max_features=5000,
            min_df=1,
            sublinear_tf=True,     # Apply log normalization
        )
        self.label_encoder = LabelEncoder()

        X = self.vectorizer.fit_transform(texts)
        y = self.label_encoder.fit_transform(labels)

        self.model = MultinomialNB(alpha=0.5)
        self.model.fit(X, y)

        self._is_trained = True
        logger.info("Naive Bayes classifier trained successfully.")

    def predict(self, text: str) -> dict:
        """
        Predict the job category for a given text.

        Args:
            text: Resume text or JD text

        Returns:
            dict with:
              - 'category': Top predicted category name
              - 'confidence': Confidence % for top category
              - 'all_scores': Dict of category → confidence %
        """
        if not self._is_trained:
            self.train()

        if not text.strip():
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "all_scores": {}
            }

        try:
            X = self.vectorizer.transform([text])
            proba = self.model.predict_proba(X)[0]
            classes = self.label_encoder.classes_

            # Map class → probability
            all_scores = {
                cls: round(float(prob) * 100, 1)
                for cls, prob in zip(classes, proba)
            }

            # Sort descending
            all_scores = dict(
                sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
            )

            top_category = list(all_scores.keys())[0]
            top_confidence = list(all_scores.values())[0]

            return {
                "category": top_category,
                "confidence": top_confidence,
                "all_scores": all_scores,
            }

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {
                "category": "Unknown",
                "confidence": 0.0,
                "all_scores": {}
            }

    def predict_both(self, resume_text: str, jd_text: str) -> dict:
        """
        Predict category for both resume and JD, then compare alignment.

        Args:
            resume_text: Resume text
            jd_text: Job description text

        Returns:
            dict with resume_result, jd_result, and alignment info
        """
        resume_result = self.predict(resume_text)
        jd_result = self.predict(jd_text)

        aligned = resume_result["category"] == jd_result["category"]

        return {
            "resume": resume_result,
            "jd": jd_result,
            "aligned": aligned,
            "alignment_note": (
                f"✅ Your resume ({resume_result['category']}) aligns with "
                f"the job category ({jd_result['category']})."
                if aligned else
                f"⚠️ Your resume appears to be in '{resume_result['category']}' "
                f"but the JD targets '{jd_result['category']}'. "
                "Consider tailoring your resume language."
            )
        }


# Singleton instance
_classifier_instance = None


def get_classifier() -> JobCategoryClassifier:
    """Return a singleton classifier instance (train once, reuse)."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = JobCategoryClassifier()
        _classifier_instance.train()
    return _classifier_instance
