import mlflow
import mlflow.sklearn
import pandas as pd
import yaml
import json
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

def train(
    params: dict,
    data_path: str = "data/train_phase1.csv",
    eval_path: str = "data/eval.csv",
) -> float:
    # --- Bonus 1: Tracking MLflow Từ Xa Với DagsHub ---
    if os.environ.get("MLFLOW_TRACKING_URI"):
        mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
        mlflow.set_experiment("Wine-Quality-Experiments")
        print(f"Tracking to remote MLflow: {os.environ.get('MLFLOW_TRACKING_URI')}")
    
    # --- Bonus 5: Canh bao lech lac du lieu ---
    df_train = pd.read_csv(data_path)
    df_eval  = pd.read_csv(eval_path)
    
    total_samples = len(df_train)
    label_dist = df_train["target"].value_counts(normalize=True).to_dict()
    
    print("--- Label Distribution ---")
    drift_warning = False
    for label, ratio in label_dist.items():
        print(f"Class {label}: {ratio:.2%}")
        if ratio < 0.10:
            print(f"⚠️ WARNING: Class {label} accounts for only {ratio:.2%}. Data is imbalanced!")
            drift_warning = True

    # Tach dac trung
    X_train = df_train.drop(columns=["target"])
    y_train = df_train["target"]
    X_eval  = df_eval.drop(columns=["target"])
    y_eval  = df_eval["target"]

    with mlflow.start_run():
        model_type = params.get("model_type", "random_forest")
        mlflow.log_param("model_type", model_type)
        
        # --- Bonus 2: Thí nghiệm với nhiều thuật toán ---
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=params.get("n_estimators", 100),
                max_depth=params.get("max_depth", 5),
                random_state=42
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=params.get("n_estimators", 100),
                max_depth=params.get("max_depth", 3),
                random_state=42
            )
        elif model_type == "logistic_regression":
            model = LogisticRegression(
                C=params.get("C", 1.0),
                max_iter=params.get("max_iter", 100),
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported model_type: {model_type}")

        # Huan luyen
        model.fit(X_train, y_train)
        
        # Danh gia
        preds = model.predict(X_eval)
        acc   = accuracy_score(y_eval, preds)
        f1    = f1_score(y_eval, preds, average="weighted")
        
        mlflow.log_metrics({"accuracy": acc, "f1_score": f1})
        mlflow.sklearn.log_model(model, "model")

        # --- Bonus 3: Báo cáo hiệu suất tự động ---
        os.makedirs("outputs", exist_ok=True)
        report_text = classification_report(y_eval, preds)
        conf_matrix = confusion_matrix(y_eval, preds)
        
        with open("outputs/report.txt", "w") as f:
            f.write(f"Model Type: {model_type}\n")
            f.write(f"Accuracy: {acc:.4f}\n")
            f.write(f"F1 Score: {f1:.4f}\n\n")
            f.write("--- Classification Report ---\n")
            f.write(report_text)
            f.write("\n--- Confusion Matrix ---\n")
            f.write(str(conf_matrix))

        # Luu metrics
        with open("outputs/metrics.json", "w") as f:
            json.dump({
                "accuracy": acc, 
                "f1_score": f1,
                "label_distribution": label_dist,
                "drift_warning": drift_warning
            }, f)

        # Luu model
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")
        
        print(f"Finished training {model_type}. Accuracy: {acc:.4f}")

    return acc

if __name__ == "__main__":
    with open("params.yaml") as f:
        config = yaml.safe_load(f)
    train(config)
