"""
SENTINEL ML Pipeline Orchestrator

Orchestrates the complete ML detection pipeline using clean services.

Supports two modes:
- B1 Mode: transactions.json with pre-computed aggregations
- B2 Mode: transactions_raw.json + auth_events.json + network_events.json
           (aggregations computed from raw events)

Flow:
    1. Load input JSONs (mode determines which files)
    2. FeatureEngineer: Compute ML features (+ aggregations in B2)
    3. Predictor: Run ML model, get anomaly scores
    4. AlertCreator: Create alerts from predictions
    5. CaseBuilder: Group alerts into cases
    6. Output: alerts.json, cases.json

Usage:
    python pipeline.py                    # B1 mode (default)
    python pipeline.py --mode b2          # B2 mode (raw events)
    python pipeline.py --threshold 0.3    # Custom threshold
    or
    GET /api/ml/run-pipeline/?mode=b2
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

try:
    # When running as Django app
    from api.ml_data.services import FeatureEngineer, Predictor, AlertCreator, CaseBuilder
except ImportError:
    # When running standalone
    from services import FeatureEngineer, Predictor, AlertCreator, CaseBuilder


class Pipeline:
    """
    Orchestrates the complete ML detection pipeline.
    """

    def __init__(
        self,
        model_path: str,
        threshold: float = 0.3,
        mode: str = "b1"
    ):
        """
        Initialize pipeline with model.

        Args:
            model_path: Path to sentinel_model.pkl
            threshold: Anomaly score threshold (default: 0.3)
            mode: "b1" for pre-computed aggregations, "b2" for raw events
        """
        self.threshold = threshold
        self.mode = mode

        # Initialize services
        self.feature_engineer = FeatureEngineer()
        self.predictor = Predictor(model_path)
        self.alert_creator = AlertCreator()
        self.case_builder = CaseBuilder()

    def run(
        self,
        input_dir: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline.

        Args:
            input_dir: Directory containing input JSON files
            output_dir: Directory to write alerts.json, cases.json

        Returns:
            Summary statistics
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print(f"SENTINEL ML PIPELINE (Mode: {self.mode.upper()})")
        print("=" * 60)

        # Step 1: Load input data
        print("\n[1/5] Loading input data...")

        if self.mode == "b2":
            # B2 mode: Load raw events
            self.feature_engineer.load_from_raw_events(
                transactions_path=input_path / "transactions_raw.json",
                profiles_path=input_path / "profiles.json",
                auth_events_path=input_path / "auth_events.json",
                network_events_path=input_path / "network_events.json"
            )
            print(f"      Mode: B2 (raw events -> computed aggregations)")
        else:
            # B1 mode: Load pre-computed aggregations
            self.feature_engineer.load_from_json(
                transactions_path=input_path / "transactions.json",
                profiles_path=input_path / "profiles.json"
            )
            print(f"      Mode: B1 (pre-computed aggregations)")

        n_transactions = len(self.feature_engineer.transactions_df)
        print(f"      Loaded {n_transactions} transactions")

        # Step 2: Compute features
        print("\n[2/5] Computing ML features...")
        if self.mode == "b2":
            print("      Computing aggregations from raw events...")
        features_df = self.feature_engineer.compute_features()
        print(f"      Computed {len(features_df.columns)} features")

        # Step 3: Run predictions
        print("\n[3/5] Running ML predictions...")
        predictions_df = self.predictor.predict(features_df, threshold=self.threshold)
        n_anomalies = predictions_df["is_anomaly"].sum()
        print(f"      Detected {n_anomalies} anomalies ({n_anomalies/len(predictions_df)*100:.1f}%)")

        # Step 4: Create alerts
        print("\n[4/5] Creating alerts...")
        alerts = self.alert_creator.create_alerts(predictions_df)
        print(f"      Created {len(alerts)} alerts")

        # Step 5: Build cases
        print("\n[5/5] Building cases...")
        cases = self.case_builder.build_cases(alerts)
        print(f"      Built {len(cases)} cases")

        # Write outputs
        print("\n" + "-" * 60)
        print("Writing output files...")

        alerts_path = output_path / "alerts.json"
        with open(alerts_path, "w") as f:
            json.dump(alerts, f, indent=2)
        print(f"  - {alerts_path.name}: {len(alerts)} alerts")

        cases_path = output_path / "cases.json"
        with open(cases_path, "w") as f:
            json.dump(cases, f, indent=2)
        print(f"  - {cases_path.name}: {len(cases)} cases")

        # Summary
        summary = self._build_summary(
            n_transactions=n_transactions,
            n_anomalies=int(n_anomalies),
            alerts=alerts,
            cases=cases,
            input_dir=str(input_path),
            output_dir=str(output_path)
        )

        summary_path = output_path / "pipeline_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"  - {summary_path.name}: pipeline metadata")

        # Print summary
        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"\nMode:                   {self.mode.upper()}")
        print(f"Transactions processed: {n_transactions}")
        print(f"Anomalies detected:     {n_anomalies} ({summary['statistics']['anomaly_rate']}%)")
        print(f"Alerts created:         {len(alerts)}")
        print(f"Cases built:            {len(cases)}")

        if summary["cases_by_type"]:
            print("\nCases by fraud type:")
            for ft, count in summary["cases_by_type"].items():
                print(f"  - {ft}: {count}")

        return summary

    def _build_summary(
        self,
        n_transactions: int,
        n_anomalies: int,
        alerts: list,
        cases: list,
        input_dir: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """Build pipeline summary."""
        summary = {
            "pipeline_run": datetime.utcnow().isoformat() + "Z",
            "mode": self.mode,
            "threshold": self.threshold,
            "input_dir": input_dir,
            "output_dir": output_dir,
            "statistics": {
                "total_transactions": n_transactions,
                "anomalies_detected": n_anomalies,
                "anomaly_rate": round(n_anomalies / n_transactions * 100, 2) if n_transactions > 0 else 0,
                "alerts_created": len(alerts),
                "cases_built": len(cases)
            },
            "cases_by_type": {},
            "alerts_by_severity": {}
        }

        for case in cases:
            ft = case.get("fraud_type", "unknown")
            summary["cases_by_type"][ft] = summary["cases_by_type"].get(ft, 0) + 1

        for alert in alerts:
            sev = alert.get("severity", "unknown")
            summary["alerts_by_severity"][sev] = summary["alerts_by_severity"].get(sev, 0) + 1

        return summary


def main():
    parser = argparse.ArgumentParser(description="SENTINEL ML Pipeline")
    parser.add_argument(
        "--model", "-m",
        default="sentinel_model.pkl",
        help="Path to trained model"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.3,
        help="Anomaly score threshold"
    )
    parser.add_argument(
        "--input-dir", "-i",
        default="input",
        help="Input directory"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default="output",
        help="Output directory"
    )
    parser.add_argument(
        "--mode",
        choices=["b1", "b2"],
        default="b1",
        help="Pipeline mode: b1 (pre-computed aggregations) or b2 (raw events)"
    )

    args = parser.parse_args()

    # Resolve paths relative to script
    script_dir = Path(__file__).parent
    model_path = script_dir / args.model if not Path(args.model).is_absolute() else Path(args.model)
    input_dir = script_dir / args.input_dir if not Path(args.input_dir).is_absolute() else Path(args.input_dir)
    output_dir = script_dir / args.output_dir if not Path(args.output_dir).is_absolute() else Path(args.output_dir)

    # Run pipeline
    pipeline = Pipeline(str(model_path), args.threshold, args.mode)
    pipeline.run(str(input_dir), str(output_dir))


if __name__ == "__main__":
    main()
