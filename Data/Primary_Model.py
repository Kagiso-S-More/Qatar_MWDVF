# ================================================================
# PRIMARY MACHINE LEARNING MODELS
# Municipal Water Distribution Vulnerability – Qatar
#
# Models:
#   1. Random Forest
#   2. Gradient Boosting
#   3. XGBoost
#
# Target:
#   SVI vulnerability class
#
# Predictors:
#   SHI, SAR, KR, TDS, MSP, PRSI, C_HA, hf, CSI
#
# Data split:
#   70% Training
#   15% Validation
#   15% Testing
# ================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
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
# 1. FILE PATH
# ================================================================

file_path = "Full_Dataset_2026_KM.xlsx"


# ================================================================
# 2. READ REQUIRED SHEETS
# ================================================================

hydro = pd.read_excel(
    file_path,
    sheet_name="Hydrochem_Indicators"
)

hydraulic = pd.read_excel(
    file_path,
    sheet_name="Hydraulic_Indicators"
)

gis = pd.read_excel(
    file_path,
    sheet_name="GIS_Indicator"
)


# ================================================================
# 3. EXTRACT REQUIRED VARIABLES
# ================================================================

# Hydrochemical predictors
hydro_ml = hydro[
    [
        "Sample_ID",
        "SHI",
        "SAR",
        "KR",
        "TDS_mg_L",
        "MSP"
    ]
].copy()

# Rename TDS for simpler plotting/output
hydro_ml = hydro_ml.rename(
    columns={"TDS_mg_L": "TDS"}
)


# Hydraulic predictors
hydraulic_ml = hydraulic[
    [
        "Sample_ID",
        "PRSI",
        "C_HA",
        "hf"
    ]
].copy()


# Target + climate variable
gis_ml = gis[
    [
        "Sample_ID",
        "CSI_2020",
        "SVI",
        "SVI_Class"
    ]
].copy()

gis_ml = gis_ml.rename(
    columns={"CSI_2020": "CSI"}
)


# ================================================================
# 4. MERGE DATASETS USING SAMPLE_ID
# ================================================================

df = hydro_ml.merge(
    hydraulic_ml,
    on="Sample_ID",
    how="inner"
)

df = df.merge(
    gis_ml,
    on="Sample_ID",
    how="inner"
)


# Sort by Sample_ID
df = df.sort_values("Sample_ID").reset_index(drop=True)


# ================================================================
# 5. CHECK DATASET
# ================================================================

print("=" * 70)
print("PRIMARY ML DATASET")
print("=" * 70)

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nSVI class distribution:")
print(df["SVI_Class"].value_counts())

print("\nSVI class percentages:")
print(
    df["SVI_Class"]
    .value_counts(normalize=True)
    .mul(100)
    .round(2)
)


# ================================================================
# 6. DEFINE PREDICTORS AND TARGET
# ================================================================

features = [
    "SHI",
    "SAR",
    "KR",
    "TDS",
    "MSP",
    "PRSI",
    "C_HA",
    "hf",
    "CSI"
]

X = df[features].copy()
y_text = df["SVI_Class"].copy()


# ================================================================
# 7. ENCODE TARGET CLASSES
# ================================================================

# We explicitly define the order so that:
# Moderate = 0
# High = 1
# Very High = 2

class_mapping = {
    "Moderate": 0,
    "High": 1,
    "Very High": 2
}

y = y_text.map(class_mapping)

if y.isnull().any():
    print("\nWARNING: Unexpected SVI class found:")
    print(y_text[y.isnull()].unique())
    raise ValueError("Unexpected SVI class detected.")


target_names = [
    "Moderate",
    "High",
    "Very High"
]

print("\nTarget encoding:")
for key, value in class_mapping.items():
    print(f"{key}: {value}")


# ================================================================
# 8. 70:15:15 STRATIFIED SPLIT
# ================================================================

# First split:
# 70% train
# 30% temporary

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=42
)

# Second split:
# temporary 30% divided equally:
# 15% validation
# 15% testing

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

print(f"\nTraining samples:   {len(X_train)}")
print(f"Validation samples: {len(X_val)}")
print(f"Testing samples:    {len(X_test)}")


def show_class_distribution(name, y_data):
    counts = pd.Series(y_data).value_counts().sort_index()

    print(f"\n{name}:")
    for label in range(3):
        print(
            f"{target_names[label]:10s}: "
            f"{counts.get(label, 0)}"
        )


show_class_distribution("Training set", y_train)
show_class_distribution("Validation set", y_val)
show_class_distribution("Testing set", y_test)


# ================================================================
# 9. CLASS-BALANCED SAMPLE WEIGHTS
# ================================================================

# This gives greater influence to the under-represented
# Moderate and Very High classes without synthesising new samples.

train_weights = compute_sample_weight(
    class_weight="balanced",
    y=y_train
)


# ================================================================
# 10. DEFINE BASELINE MODELS
# ================================================================

# ------------------------------------------------
# Random Forest
# ------------------------------------------------

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    bootstrap=True,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)


# ------------------------------------------------
# Gradient Boosting
# ------------------------------------------------

gb_model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.10,
    max_depth=3,
    random_state=42
)


# ------------------------------------------------
# XGBoost
# ------------------------------------------------

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
# 11. TRAIN MODELS
# ================================================================

print("\n" + "=" * 70)
print("TRAINING PRIMARY MODELS")
print("=" * 70)


# Random Forest
rf_model.fit(
    X_train,
    y_train
)

print("\nRandom Forest trained.")


# Gradient Boosting
gb_model.fit(
    X_train,
    y_train,
    sample_weight=train_weights
)

print("Gradient Boosting trained.")


# XGBoost
xgb_model.fit(
    X_train,
    y_train,
    sample_weight=train_weights
)

print("XGBoost trained.")


# ================================================================
# 12. MODEL EVALUATION FUNCTION
# ================================================================

def evaluate_model(model, X_data, y_data, model_name, dataset_name):

    predictions = model.predict(X_data)

    accuracy = accuracy_score(
        y_data,
        predictions
    )

    macro_precision = precision_score(
        y_data,
        predictions,
        average="macro",
        zero_division=0
    )

    macro_recall = recall_score(
        y_data,
        predictions,
        average="macro",
        zero_division=0
    )

    macro_f1 = f1_score(
        y_data,
        predictions,
        average="macro",
        zero_division=0
    )

    weighted_f1 = f1_score(
        y_data,
        predictions,
        average="weighted",
        zero_division=0
    )

    result = {
        "Model": model_name,
        "Dataset": dataset_name,
        "Accuracy": accuracy,
        "Macro Precision": macro_precision,
        "Macro Recall": macro_recall,
        "Macro F1": macro_f1,
        "Weighted F1": weighted_f1
    }

    return result, predictions


# ================================================================
# 13. VALIDATION PERFORMANCE
# ================================================================

models = {
    "Random Forest": rf_model,
    "Gradient Boosting": gb_model,
    "XGBoost": xgb_model
}


validation_results = []

for model_name, model in models.items():

    result, predictions = evaluate_model(
        model,
        X_val,
        y_val,
        model_name,
        "Validation"
    )

    validation_results.append(result)


validation_results_df = pd.DataFrame(validation_results)


print("\n" + "=" * 70)
print("VALIDATION PERFORMANCE")
print("=" * 70)

print(
    validation_results_df
    .round(3)
    .to_string(index=False)
)


# ================================================================
# 14. SELECT BEST MODEL USING MACRO F1
# ================================================================

best_row = validation_results_df.loc[
    validation_results_df["Macro F1"].idxmax()
]

best_model_name = best_row["Model"]
best_model = models[best_model_name]


print("\n" + "=" * 70)
print("BEST PRIMARY MODEL")
print("=" * 70)

print(
    f"\nBest model based on validation Macro F1: "
    f"{best_model_name}"
)

print(
    f"Validation Macro F1 = "
    f"{best_row['Macro F1']:.3f}"
)


# ================================================================
# 15. FINAL TEST-SET PERFORMANCE
# ================================================================

test_results = []
test_predictions = {}


for model_name, model in models.items():

    result, predictions = evaluate_model(
        model,
        X_test,
        y_test,
        model_name,
        "Test"
    )

    test_results.append(result)
    test_predictions[model_name] = predictions


test_results_df = pd.DataFrame(test_results)


print("\n" + "=" * 70)
print("INDEPENDENT TEST PERFORMANCE")
print("=" * 70)

print(
    test_results_df
    .round(3)
    .to_string(index=False)
)


# ================================================================
# 16. MAJORITY-CLASS BASELINE
# ================================================================

dummy_model = DummyClassifier(
    strategy="most_frequent"
)

dummy_model.fit(
    X_train,
    y_train
)

dummy_predictions = dummy_model.predict(X_test)


baseline_accuracy = accuracy_score(
    y_test,
    dummy_predictions
)

baseline_macro_f1 = f1_score(
    y_test,
    dummy_predictions,
    average="macro",
    zero_division=0
)


print("\n" + "=" * 70)
print("MAJORITY-CLASS BASELINE")
print("=" * 70)

print(
    f"\nBaseline test accuracy: "
    f"{baseline_accuracy:.3f}"
)

print(
    f"Baseline Macro F1: "
    f"{baseline_macro_f1:.3f}"
)


# ================================================================
# 17. DETAILED CLASSIFICATION REPORT
#     FOR BEST MODEL
# ================================================================

best_test_predictions = test_predictions[
    best_model_name
]


print("\n" + "=" * 70)
print(
    f"CLASSIFICATION REPORT – {best_model_name}"
)
print("=" * 70)


print(
    classification_report(
        y_test,
        best_test_predictions,
        labels=[0, 1, 2],
        target_names=target_names,
        digits=3,
        zero_division=0
    )
)


# ================================================================
# 18. CONFUSION MATRIX – BEST MODEL
# ================================================================

cm = confusion_matrix(
    y_test,
    best_test_predictions,
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
# 19. FEATURE IMPORTANCE
# ================================================================

importance_results = []

for model_name, model in models.items():

    importance_df = pd.DataFrame({
        "Feature": features,
        "Importance": model.feature_importances_
    })

    importance_df["Model"] = model_name

    importance_df = importance_df.sort_values(
        "Importance",
        ascending=False
    )

    importance_results.append(
        importance_df
    )


feature_importance_df = pd.concat(
    importance_results,
    ignore_index=True
)


print("\n" + "=" * 70)
print("FEATURE IMPORTANCE")
print("=" * 70)

for model_name in models.keys():

    print(f"\n{model_name}")

    temp = feature_importance_df[
        feature_importance_df["Model"] == model_name
    ]

    print(
        temp[
            ["Feature", "Importance"]
        ]
        .round(4)
        .to_string(index=False)
    )


# ================================================================
# 20. SAVE MODELLING DATASET
# ================================================================

df.to_excel(
    "Primary_ML_Dataset.xlsx",
    index=False
)


# ================================================================
# 21. SAVE ALL NUMERICAL RESULTS
# ================================================================

with pd.ExcelWriter(
    "Primary_ML_Results.xlsx",
    engine="openpyxl"
) as writer:

    # Model performance
    validation_results_df.to_excel(
        writer,
        sheet_name="Validation_Performance",
        index=False
    )

    test_results_df.to_excel(
        writer,
        sheet_name="Test_Performance",
        index=False
    )

    # Feature importance
    feature_importance_df.to_excel(
        writer,
        sheet_name="Feature_Importance",
        index=False
    )

    # Confusion matrix
    cm_df.to_excel(
        writer,
        sheet_name="Best_Model_ConfusionMatrix"
    )

    # Dataset splits
    pd.DataFrame({
        "Index": X_train.index,
        "Set": "Training"
    }).to_excel(
        writer,
        sheet_name="Data_Splits",
        index=False
    )

    pd.DataFrame({
        "Index": X_val.index,
        "Set": "Validation"
    }).to_excel(
        writer,
        sheet_name="Data_Splits",
        startrow=len(X_train) + 2,
        index=False
    )

    pd.DataFrame({
        "Index": X_test.index,
        "Set": "Testing"
    }).to_excel(
        writer,
        sheet_name="Data_Splits",
        startrow=len(X_train) + len(X_val) + 4,
        index=False
    )


print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print("\nFiles created:")
print("1. Primary_ML_Dataset.xlsx")
print("2. Primary_ML_Results.xlsx")