"""
Predictor Service

Loads the trained ML model and runs predictions on feature data.

Input:
    - DataFrame with ML features (from FeatureEngineer)

Output:
    - DataFrame with added columns: anomaly_score, is_anomaly
"""

import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from typing import Union, Optional, Dict, Any


class Predictor:
    """
    ML Predictor service.

    Loads a trained Isolation Forest model and runs anomaly detection.
    """

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        """
        Initialize predictor.

        Args:
            model_path: Path to sentinel_model.pkl. If None, must call load_model() later.
        """
        self.model = None
        self.scaler = None
        self.imputer = None
        self.features = None
        self.threshold = 0.0
        self.model_metadata: Dict[str, Any] = {}

        if model_path:
            self.load_model(model_path)

    def load_model(self, model_path: Union[str, Path]) -> "Predictor":
        """
        Load trained model from pickle file.

        Args:
            model_path: Path to sentinel_model.pkl

        Returns:
            self for chaining
        """
        artifact = joblib.load(model_path)

        self.model = artifact["model"]
        self.scaler = artifact["scaler"]
        self.imputer = artifact["imputer"]
        self.features = artifact["features"]
        self.threshold = artifact.get("threshold", 0.0)
        self.model_metadata = artifact.get("training_stats", {})

        return self

    def predict(
        self,
        df: pd.DataFrame,
        threshold: Optional[float] = None
    ) -> pd.DataFrame:
        """
        Run predictions on feature data.

        Args:
            df: DataFrame containing ML feature columns
            threshold: Override anomaly threshold (default: use model's threshold)

        Returns:
            DataFrame with added columns:
            - anomaly_score: 0-1 score (higher = more anomalous)
            - is_anomaly: Boolean flag
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")

        threshold = threshold if threshold is not None else self.threshold

        # Extract features
        X = df[self.features].copy()

        # Handle missing values
        X_imputed = self.imputer.transform(X)

        # Scale features
        X_scaled = self.scaler.transform(X_imputed)

        # Get anomaly scores
        # Isolation Forest: more negative decision_function = more anomalous
        raw_scores = self.model.decision_function(X_scaled)

        # Convert to 0-1 range (more positive = more anomalous)
        anomaly_scores = -raw_scores

        # Normalize to 0-1 range
        min_score = anomaly_scores.min()
        max_score = anomaly_scores.max()
        if max_score > min_score:
            anomaly_scores = (anomaly_scores - min_score) / (max_score - min_score)
        else:
            anomaly_scores = np.zeros_like(anomaly_scores)

        # Add to dataframe
        result = df.copy()
        result["anomaly_score"] = anomaly_scores
        result["is_anomaly"] = anomaly_scores > threshold

        return result

    def get_feature_names(self) -> list:
        """Get list of required feature names."""
        return self.features if self.features else []

    def get_model_info(self) -> Dict[str, Any]:
        """Get model metadata and configuration."""
        return {
            "features": self.features,
            "threshold": self.threshold,
            "model_type": type(self.model).__name__ if self.model else None,
            "metadata": self.model_metadata
        }
