"""Train loan approval classifiers and save the best model."""

from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from inference import (
    ENCODERS_PATH,
    METADATA_PATH,
    TARGET_COLUMN,
    apply_encoders,
    fit_encoders,
    strip_categoricals,
)

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "loan_approval_dataset_cleaned.csv"
MODEL_PATH = ROOT / "loan_model.pkl"
SCALER_PATH = ROOT / "scaler.pkl"


def main() -> None:
    df = pd.read_csv(DATASET)
    print(df.head())

    df = strip_categoricals(df)
    encoders = fit_encoders(df)
    df = apply_encoders(df, encoders)
    df[TARGET_COLUMN] = LabelEncoder().fit_transform(df[TARGET_COLUMN])

    X = df.drop(TARGET_COLUMN, axis=1)
    y = df[TARGET_COLUMN]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )

    models = {
        "Logistic Regression": LogisticRegression(),
        "Decision Tree": DecisionTreeClassifier(),
        "Random Forest": RandomForestClassifier(),
        "SVM": SVC(probability=True),
    }

    results = {}
    print("\n=== Model Accuracy ===")
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        results[name] = acc
        print(f"{name}: {acc:.4f}")

    best_model_name = max(results, key=results.get)
    best_model = models[best_model_name]
    print(f"\nBest Model: {best_model_name}")

    y_pred = best_model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)

    ConfusionMatrixDisplay(confusion_matrix=cm).plot()
    plt.title(f"Confusion Matrix ({best_model_name})")
    plt.savefig(ROOT / "confusion_matrix.png", bbox_inches="tight")
    plt.close()

    y_prob = best_model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    auc = roc_auc_score(y_test, y_prob)

    plt.plot(fpr, tpr, label=f"AUC = {auc:.2f}")
    plt.plot([0, 1], [0, 1], linestyle="--")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve")
    plt.legend()
    plt.savefig(ROOT / "roc_curve.png", bbox_inches="tight")
    plt.close()

    precision, recall, _ = precision_recall_curve(y_test, y_prob)
    plt.plot(recall, precision)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.savefig(ROOT / "precision_recall_curve.png", bbox_inches="tight")
    plt.close()

    if best_model_name == "Random Forest":
        importance = best_model.feature_importances_
        pd.Series(importance, index=X.columns).sort_values().plot(kind="barh")
        plt.title("Feature Importance")
        plt.savefig(ROOT / "feature_importance.png", bbox_inches="tight")
        plt.close()

    tn, fp, fn, tp = cm.ravel()
    print("\nType I Error (False Positive):", fp)
    print("Type II Error (False Negative):", fn)

    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    joblib.dump(
        {"best_model_name": best_model_name, "feature_columns": list(X.columns)},
        METADATA_PATH,
    )
    print(f"\nSaved model to {MODEL_PATH}")
    print(f"Saved scaler to {SCALER_PATH}")
    print(f"Saved encoders to {ENCODERS_PATH}")


if __name__ == "__main__":
    main()
