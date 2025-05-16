# Customer Churn Prediction 

A machine learning project to predict binary outcomes using classification models.

---

## 📌 Overview

This project focuses on building models to classify data into two classes — `0` and `1`. After conducting a thorough analysis, **Logistic Regression** and **Random Forest** classifiers were implemented and evaluated.

The goal is to identify which model best predicts the target class using evaluation metrics such as accuracy, precision, recall, F1-score, and ROC-AUC.

---

## 🧰 Features

- Exploratory Data Analysis (EDA)
- Data cleaning and preprocessing
- Feature scaling and transformation
- Training and comparison of multiple classification models:
  - Logistic Regression
  - Random Forest
- Evaluation using:
  - Accuracy
  - Precision, Recall, F1-Score
  - ROC Curve and AUC
- Model selection based on interpretability and performance
- Recommendations for improving performance

---

## 📊 Model Performance

| Model              | Accuracy | AUC Score | F1 Score (Class 1) |
|-------------------|----------|-----------|--------------------|
| Logistic Regression | 0.81     | 0.87      | 0.61               |
| Random Forest       | 0.79     | 0.84      | 0.56               |

- **Final Model**: **Logistic Regression**
- **Why?** Logistic Regression had higher AUC, better accuracy, and more balanced performance for the positive class (1).

---

## 🧪 Requirements

- Python 3.x
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn

You can install them using:

```bash
pip install -r requirements.txt
