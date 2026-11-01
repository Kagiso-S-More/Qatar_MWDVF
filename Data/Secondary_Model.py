# ================================================================
# SECONDARY MACHINE LEARNING MODELS
# Composite-index benchmark model
#
# Predictors: HRI, CSI, HVI
# Target:     SVI_Class
# Models:     RF, GB, XGBoost
# Split:      70:15:15
# ================================================================

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.dummy import DummyClassifier

from xgboost import XGBClassifier

import warnings
warnings.filterwarnings("ignore")


# ================================================================
# 1. LOAD DATA
# ================================================================

file_path = "Full_Dataset_2026_KM.xlsx"

gis = pd.read_excel(
    file_path,
    sheet_name="GIS_Indicator"
)


# ================================================================
# 2. CREATE SECONDARY MODEL DATASET
# ================================================================

# The GIS sheet contains the required composite indices.
# Rename fields for cleaner output.

df = gis[
    [
        "Sample_ID",
        "HRI",
        "CSI_2020",
        "HVI",
        "SVI",
        "SVI_Class"
    ]
].copy()

df = df.rename(
    columns={
        "CSI_2020": "CSI"
    }
)

df = df.sort_values(
    "Sample_ID"
).reset_index(drop=True)


# ================================================================
# 3. DATA CHECK
# ================================================================

print("=" * 70)
print("SECONDARY ML DATASET")
print("=" * 70)

print("\nDataset shape:")
print(df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nSVI class distribution:")
print(df["SVI_Class"].value_counts())

print("\nClass percentages:")
print(
    df["SVI_Class"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ================================================================
# 4. DEFINE PREDICTORS AND TARGET
# ================================================================

features = [
    "HRI",
    "CSI",
    "HVI"
]

X = df[features].copy()

class_mapping = {
    "Moderate": 0,
    "High": 1,
    "Very High": 2
}

y = df["SVI_Class"].map(
    class_mapping
)

target_names = [
    "Moderate",
    "High",
    "Very High"
]

if y.isnull().any():
    raise ValueError(
        "Unexpected SVI class detected."
    )


# ================================================================
# 5. CHECK FEATURE VARIABILITY
# ================================================================

print("\nPredictor variability:")
print(
    X.agg(
        ["min", "max", "mean", "std"]
    ).T
)


# ================================================================
# 6. 70:15:15 STRATIFIED SPLIT
# ================================================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=42
)


print("\n" + "=" * 70)
print("DATA SPLIT")
print("=" * 70)

print(f"Training:   {len(X_train)}")
print(f"Validation: {len(X_val)}")
print(f"Testing:    {len(X_test)}")


# ================================================================
# 7. CLASS-BALANCED TRAINING WEIGHTS
# ================================================================

train_weights = compute_sample_weight(
    class_weight="balanced",
    y=y_train
)


# ================================================================
# 8. DEFINE MODELS
# ================================================================

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    bootstrap=True,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.10,
    max_depth=3,
    random_state=42
)


xgb_model = XGBClassifier(
    n_estimators=100,
    learning_rate=0.10,
    max_depth=6,
    subsample=0.80,
    objective="multi:softprob",
    num_class=3,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)


# ================================================================
# 9. TRAIN
# ================================================================

rf_model.fit(
    X_train,
    y_train
)

gb_model.fit(
    X_train,
    y_train,
    sample_weight=train_weights
)

xgb_model.fit(
    X_train,
    y_train,
    sample_weight=train_weights
)


models = {
    "Random Forest": rf_model,
    "Gradient Boosting": gb_model,
    "XGBoost": xgb_model
}


# ================================================================
# 10. EVALUATION FUNCTION
# ================================================================

def evaluate_model(
    model,
    X_data,
    y_data,
    model_name,
    dataset_name
):

    pred = model.predict(X_data)

    return {
        "Model": model_name,
        "Dataset": dataset_name,

        "Accuracy": accuracy_score(
            y_data,
            pred
        ),

        "Macro Precision": precision_score(
            y_data,
            pred,
            average="macro",
            zero_division=0
        ),

        "Macro Recall": recall_score(
            y_data,
            pred,
            average="macro",
            zero_division=0
        ),

        "Macro F1": f1_score(
            y_data,
            pred,
            average="macro",
            zero_division=0
        ),

        "Weighted F1": f1_score(
            y_data,
            pred,
            average="weighted",
            zero_division=0
        )

    }, pred


# ================================================================
# 11. VALIDATION RESULTS
# ================================================================

validation_results = []

for name, model in models.items():

    result, _ = evaluate_model(
        model,
        X_val,
        y_val,
        name,
        "Validation"
    )

    validation_results.append(result)


validation_df = pd.DataFrame(
    validation_results
)


print("\n" + "=" * 70)
print("SECONDARY MODEL – VALIDATION PERFORMANCE")
print("=" * 70)

print(
    validation_df
    .round(3)
    .to_string(index=False)
)


# ================================================================
# 12. INDEPENDENT TEST RESULTS
# ================================================================

test_results = []
test_predictions = {}

for name, model in models.items():

    result, pred = evaluate_model(
        model,
        X_test,
        y_test,
        name,
        "Test"
    )

    test_results.append(result)

    test_predictions[name] = pred


test_df = pd.DataFrame(
    test_results
)


print("\n" + "=" * 70)
print("SECONDARY MODEL – INDEPENDENT TEST PERFORMANCE")
print("=" * 70)

print(
    test_df
    .round(3)
    .to_string(index=False)
)


# ================================================================
# 13. IDENTIFY BEST SECONDARY MODEL BY TEST MACRO F1
# ================================================================

best_row = test_df.loc[
    test_df["Macro F1"].idxmax()
]

best_model_name = best_row["Model"]

best_predictions = test_predictions[
    best_model_name
]


print("\n" + "=" * 70)
print("BEST SECONDARY MODEL")
print("=" * 70)

print(
    f"\nBest secondary model: "
    f"{best_model_name}"
)

print(
    f"Test accuracy: "
    f"{best_row['Accuracy']:.3f}"
)

print(
    f"Test Macro F1: "
    f"{best_row['Macro F1']:.3f}"
)


# ================================================================
# 14. CLASSIFICATION REPORT
# ================================================================

print("\nClassification report:")

print(
    classification_report(
        y_test,
        best_predictions,
        labels=[0, 1, 2],
        target_names=target_names,
        digits=3,
        zero_division=0
    )
)


# ================================================================
# 15. CONFUSION MATRIX
# ================================================================

cm = confusion_matrix(
    y_test,
    best_predictions,
    labels=[0, 1, 2]
)

cm_df = pd.DataFrame(
    cm,
    index=[
        "Actual Moderate",
        "Actual High",
        "Actual Very High"
    ],
    columns=[
        "Predicted Moderate",
        "Predicted High",
        "Predicted Very High"
    ]
)


print("\nConfusion matrix:")
print(cm_df)


# ================================================================
# 16. FEATURE IMPORTANCE
# ================================================================

importance_results = []

for name, model in models.items():

    temp = pd.DataFrame({
        "Feature": features,
        "Importance": model.feature_importances_,
        "Model": name
    })

    temp = temp.sort_values(
        "Importance",
        ascending=False
    )

    importance_results.append(temp)


feature_importance_df = pd.concat(
    importance_results,
    ignore_index=True
)


print("\n" + "=" * 70)
print("SECONDARY MODEL FEATURE IMPORTANCE")
print("=" * 70)

for name in models.keys():

    print(f"\n{name}")

    temp = feature_importance_df[
        feature_importance_df["Model"] == name
    ]

    print(
        temp[
            ["Feature", "Importance"]
        ]
        .round(4)
        .to_string(index=False)
    )


# ================================================================
# 17. MAJORITY-CLASS BASELINE
# ================================================================

dummy = DummyClassifier(
    strategy="most_frequent"
)

dummy.fit(
    X_train,
    y_train
)

dummy_pred = dummy.predict(
    X_test
)


print("\n" + "=" * 70)
print("MAJORITY-CLASS BASELINE")
print("=" * 70)

print(
    "Accuracy:",
    round(
        accuracy_score(
            y_test,
            dummy_pred
        ),
        3
    )
)

print(
    "Macro F1:",
    round(
        f1_score(
            y_test,
            dummy_pred,
            average="macro",
            zero_division=0
        ),
        3
    )
)


# ================================================================
# 18. SAVE RESULTS
# ================================================================

df.to_excel(
    "Secondary_ML_Dataset.xlsx",
    index=False
)


with pd.ExcelWriter(
    "Secondary_ML_Results.xlsx",
    engine="openpyxl"
) as writer:

    validation_df.to_excel(
        writer,
        sheet_name="Validation_Performance",
        index=False
    )

    test_df.to_excel(
        writer,
        sheet_name="Test_Performance",
        index=False
    )

    feature_importance_df.to_excel(
        writer,
        sheet_name="Feature_Importance",
        index=False
    )

    cm_df.to_excel(
        writer,
        sheet_name="Best_Model_ConfusionMatrix"
    )


print("\nAnalysis complete.")

print("\nFiles created:")
print("1. Secondary_ML_Dataset.xlsx")
print("2. Secondary_ML_Results.xlsx")