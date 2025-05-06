# ml_model/train_hybrid_model.py (Incremental, Resume-safe, Self-healing, Final Version)

import os
import sys
import joblib
import numpy as np
from xgboost import XGBClassifier
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report, f1_score

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 📦 Feature extractor for rebuild
from utils.feature_engineering import extract_features_in_batches
import sqlite3
import pandas as pd

# 📁 Config
DB_PATH = "data/phishing_dataset.db"
TABLE_NAME = "phishing_dataset"
BATCH_FOLDER = "ml_model/feature_batches"
CHECKPOINT_PATH = "ml_model/phish_model_checkpoint.pkl"
STATE_PATH = "ml_model/last_batch.txt"

# 🧠 Get last trained batch index
def get_last_trained_batch():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            return int(f.read().strip())
    return -1

# 📂 Save model + batch state
def save_checkpoint(model, batch_index):
    joblib.dump(model, CHECKPOINT_PATH)
    with open(STATE_PATH, "w") as f:
        f.write(str(batch_index))

# 📦 Load one batch from disk
def load_batch(batch_idx):
    x_path = os.path.join(BATCH_FOLDER, f"X_batch_{batch_idx}.pkl")
    y_path = os.path.join(BATCH_FOLDER, f"y_batch_{batch_idx}.pkl")
    if os.path.exists(x_path) and os.path.exists(y_path):
        X = joblib.load(x_path)
        y = joblib.load(y_path)
        return np.array(X), np.array(y)
    return None, None

# 🚀 Main training loop
def train_incrementally():
    # Check if batch folder exists and has content
    if not os.path.exists(BATCH_FOLDER) or len(os.listdir(BATCH_FOLDER)) == 0:
        print("📊 No batches found. Rebuilding them now...")
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        extract_features_in_batches(df)

    batch_files = sorted([f for f in os.listdir(BATCH_FOLDER) if f.startswith("X_batch_")])
    total_batches = len(batch_files)
    last_batch_done = get_last_trained_batch()

    print(f"🧠 Found {total_batches} batches.")
    print(f"⏩ Resuming from batch {last_batch_done + 1}")

    model = None

    for batch_idx in range(last_batch_done + 1, total_batches):
        X, y = load_batch(batch_idx)
        if X is None or y is None:
            print(f"⚠️ Skipping batch {batch_idx} (not found or incomplete)")
            continue

        if len(np.unique(y)) < 2:
            print(f"⚠️ Skipping batch {batch_idx} – only one class present: {np.unique(y)}")
            continue

        print(f"📦 Training on batch {batch_idx} ({len(X)} samples)")

        if model is None:
            class_weights = compute_class_weight("balanced", classes=np.unique(y), y=y)
            weight_dict = {i: class_weights[i] for i in range(len(class_weights))}
            model = XGBClassifier(
                n_estimators=150,
                max_depth=10,
                learning_rate=0.1,
                use_label_encoder=False,
                eval_metric="logloss",
                scale_pos_weight=weight_dict.get(1, 1.0)
            )
            model.fit(X, y)
        else:
            model.fit(X, y, xgb_model=model)

        print(f"✅ Trained on batch {batch_idx}")
        save_checkpoint(model, batch_idx)

    if model is None and os.path.exists(CHECKPOINT_PATH):
        print("♻️ Loading model checkpoint since no new batches trained...")
        model = joblib.load(CHECKPOINT_PATH)

    print("🎉 All batches trained.")
    return model

# 🥪 Final model evaluation
def evaluate_model(model):
    print("🥪 Evaluating final model...")
    all_X = []
    all_y = []

    for f in sorted(os.listdir(BATCH_FOLDER)):
        if f.startswith("X_batch_"):
            batch_idx = int(f.split("_")[-1].split(".")[0])
            X, y = load_batch(batch_idx)
            if X is not None and y is not None:
                all_X.extend(X)
                all_y.extend(y)

    if len(all_X) == 0:
        print("⚠️ No data available for evaluation. Please check your batches.")
        return

    X = np.array(all_X)
    y = np.array(all_y)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

    y_pred = model.predict(X_test)
    print("\n📊 Evaluation Report:")
    print(classification_report(y_test, y_pred))
    print("F1 Score:", f1_score(y_test, y_pred))

# 🏁 Main Execution
if __name__ == "__main__":
    os.makedirs("ml_model", exist_ok=True)
    model = train_incrementally()
    joblib.dump(model, "ml_model/phish_model.pkl")
    print("📎 Final model saved to ml_model/phish_model.pkl")
    evaluate_model(model)

