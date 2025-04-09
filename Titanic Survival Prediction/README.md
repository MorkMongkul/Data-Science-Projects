# Titanic Survival Prediction

A machine learning project to predict passenger survival on the Titanic using classification models.

## Overview

This project uses the famous Titanic dataset to predict whether a passenger survived the disaster or not. Several machine learning models are implemented and evaluated, with Logistic Regression ultimately chosen as the final model due to its performance and interpretability.

## Features

- Comprehensive exploratory data analysis (EDA)
- Data cleaning and preprocessing
- Feature engineering (Title extraction, Family size, etc.)
- Multiple model training (Logistic Regression, Random Forest, Gradient Boosting, SVM, KNN)
- Model evaluation with various metrics
- Hyperparameter tuning
- Handling class imbalance with SMOTE

## Model Performance

| Model | Accuracy | AUC Score | F1 Score (Class 1) |
|-------|----------|-----------|-------------------|
| Logistic Regression | 0.80 | 0.86 | 0.74 |
| Random Forest | 0.82 | 0.85 | 0.76 |

## Requirements

- Python 3.x
- pandas
- numpy
- scikit-learn
- matplotlib
- seaborn
- plotly
- imbalanced-learn

## Usage

Open the Jupyter notebook `Titanics Survival Prediction.ipynb` to view the complete analysis and model development process.