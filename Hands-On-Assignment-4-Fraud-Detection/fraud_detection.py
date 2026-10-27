"""
Fraud Detection Using PyOD AutoEncoder
MSCS-633-M20 — Advance Artificial Intelligence
Student: Xhon Pelushi
University of the Cumberlands

This script uses PyOD's AutoEncoder model to detect fraudulent credit card
transactions. The AutoEncoder learns normal transaction patterns and flags
anomalies (potential fraud) based on high reconstruction error.

Dataset: Synthetic credit card transaction data modeled after the Kaggle
Credit Card Fraud Detection dataset (anonymized PCA features V1-V28,
Amount, and Class label).
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score
)
from sklearn.model_selection import train_test_split
from pyod.models.auto_encoder import AutoEncoder

# ──────────────────────────────────────────────────────────────────────
# 1. Generate Synthetic Credit Card Transaction Data
# ──────────────────────────────────────────────────────────────────────
print("=" * 65)
print("  Fraud Detection with PyOD AutoEncoder")
print("  MSCS-633 — Advance Artificial Intelligence")
print("  Student: Xhon Pelushi")
print("=" * 65)

np.random.seed(42)

n_normal = 5000
n_fraud = 50  # ~1% fraud rate, realistic imbalance

# Normal transactions: centered around 0 with moderate variance
normal_features = np.random.randn(n_normal, 28) * 1.0
normal_amounts = np.abs(np.random.exponential(scale=80, size=n_normal))

# Fraudulent transactions: shifted distributions to simulate anomalies
fraud_features = np.random.randn(n_fraud, 28) * 2.5 + np.random.choice(
    [-2, 2], size=(n_fraud, 28)
)
fraud_amounts = np.abs(np.random.exponential(scale=300, size=n_fraud))

# Combine into a DataFrame
feature_cols = [f'V{i}' for i in range(1, 29)]
normal_df = pd.DataFrame(normal_features, columns=feature_cols)
normal_df['Amount'] = normal_amounts
normal_df['Class'] = 0

fraud_df = pd.DataFrame(fraud_features, columns=feature_cols)
fraud_df['Amount'] = fraud_amounts
fraud_df['Class'] = 1

df = pd.concat([normal_df, fraud_df], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\nDataset shape: {df.shape}")
print(f"Normal transactions: {(df['Class'] == 0).sum()}")
print(f"Fraudulent transactions: {(df['Class'] == 1).sum()}")
print(f"Fraud percentage: {(df['Class'] == 1).mean() * 100:.2f}%")

# ──────────────────────────────────────────────────────────────────────
# 2. Data Preprocessing
# ──────────────────────────────────────────────────────────────────────
print("\n--- Data Preprocessing ---")
print(df.describe().round(2).to_string())

# Separate features and labels
X = df.drop('Class', axis=1).values
y = df['Class'].values

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.3, random_state=42, stratify=y
)

print(f"\nTraining set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")
print(f"Training fraud count: {y_train.sum()}")
print(f"Test fraud count: {y_test.sum()}")

# ──────────────────────────────────────────────────────────────────────
# 3. Build and Train AutoEncoder Model
# ──────────────────────────────────────────────────────────────────────
print("\n--- Training AutoEncoder Model ---")

# Configure the AutoEncoder with appropriate architecture
# Hidden neurons define the encoder layers; decoder mirrors automatically
auto_encoder = AutoEncoder(
    hidden_neuron_list=[64, 32, 16],
    hidden_activation_name='relu',
    epoch_num=30,
    batch_size=32,
    dropout_rate=0.2,
    batch_norm=True,
    contamination=0.01,
    verbose=1
)

# Train the model on training data
auto_encoder.fit(X_train)
print("AutoEncoder training complete.")

# ──────────────────────────────────────────────────────────────────────
# 4. Predict Anomalies and Evaluate
# ──────────────────────────────────────────────────────────────────────
print("\n--- Anomaly Detection Results ---")

# Get anomaly scores (reconstruction errors)
train_scores = auto_encoder.decision_function(X_train)
test_scores = auto_encoder.decision_function(X_test)

# Get binary predictions (0 = normal, 1 = anomaly/fraud)
train_preds = auto_encoder.predict(X_train)
test_preds = auto_encoder.predict(X_test)

# Classification report for test set
print("\nClassification Report (Test Set):")
print(classification_report(y_test, test_preds, target_names=['Normal', 'Fraud']))

# Confusion matrix
cm = confusion_matrix(y_test, test_preds)
print("Confusion Matrix:")
print(cm)

# ROC AUC Score
roc_auc = roc_auc_score(y_test, test_scores)
print(f"\nROC AUC Score: {roc_auc:.4f}")

# Average Precision Score
avg_precision = average_precision_score(y_test, test_scores)
print(f"Average Precision Score: {avg_precision:.4f}")

# ──────────────────────────────────────────────────────────────────────
# 5. Visualizations
# ──────────────────────────────────────────────────────────────────────
print("\n--- Generating Visualizations ---")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Fraud Detection with PyOD AutoEncoder', fontsize=14, fontweight='bold')

# Plot 1: Reconstruction Error Distribution
ax1 = axes[0, 0]
ax1.hist(test_scores[y_test == 0], bins=50, alpha=0.7, label='Normal', color='steelblue')
ax1.hist(test_scores[y_test == 1], bins=50, alpha=0.7, label='Fraud', color='crimson')
ax1.set_xlabel('Reconstruction Error (Anomaly Score)')
ax1.set_ylabel('Frequency')
ax1.set_title('Reconstruction Error Distribution')
ax1.legend()

# Plot 2: ROC Curve
ax2 = axes[0, 1]
fpr, tpr, _ = roc_curve(y_test, test_scores)
ax2.plot(fpr, tpr, color='darkorange', lw=2, label=f'AUC = {roc_auc:.4f}')
ax2.plot([0, 1], [0, 1], color='gray', linestyle='--')
ax2.set_xlabel('False Positive Rate')
ax2.set_ylabel('True Positive Rate')
ax2.set_title('ROC Curve')
ax2.legend()

# Plot 3: Confusion Matrix Heatmap
ax3 = axes[1, 0]
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax3,
            xticklabels=['Normal', 'Fraud'], yticklabels=['Normal', 'Fraud'])
ax3.set_xlabel('Predicted')
ax3.set_ylabel('Actual')
ax3.set_title('Confusion Matrix')

# Plot 4: Precision-Recall Curve
ax4 = axes[1, 1]
precision, recall, _ = precision_recall_curve(y_test, test_scores)
ax4.plot(recall, precision, color='purple', lw=2,
         label=f'Avg Precision = {avg_precision:.4f}')
ax4.set_xlabel('Recall')
ax4.set_ylabel('Precision')
ax4.set_title('Precision-Recall Curve')
ax4.legend()

plt.tight_layout()
plt.savefig('fraud_detection_results.png', dpi=150, bbox_inches='tight')
print("Saved: fraud_detection_results.png")

# ──────────────────────────────────────────────────────────────────────
# 6. Summary and Key Findings
# ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("  Summary of Key Findings")
print("=" * 65)
print(f"  Total transactions analyzed: {len(df)}")
print(f"  Fraud rate: {(df['Class'] == 1).mean() * 100:.2f}%")
print(f"  AutoEncoder architecture: [29] -> [64, 32, 16, 32, 64] -> [29]")
print(f"  ROC AUC Score: {roc_auc:.4f}")
print(f"  Average Precision: {avg_precision:.4f}")
print(f"  True Positives (Fraud detected): {cm[1, 1]}")
print(f"  False Negatives (Fraud missed): {cm[1, 0]}")
print(f"  False Positives (Normal flagged): {cm[0, 1]}")
print(f"  True Negatives (Normal correct): {cm[0, 0]}")
print("=" * 65)
print("\nThe AutoEncoder detects anomalies by learning to reconstruct")
print("normal transaction patterns. Transactions with high reconstruction")
print("error are flagged as potential fraud. This unsupervised approach")
print("is valuable when labeled fraud data is scarce.")
print("=" * 65)
