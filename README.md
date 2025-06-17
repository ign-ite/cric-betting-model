# 🏏 T20 Cricket Match Winner Predictor

> Predict the winner of a T20 cricket match using machine learning trained on 11,000+ real-world games.

This project uses historical T20 cricket data to train ML models that can predict match outcomes based on teams, venue, toss, and performance features.

---

## ✅ What’s Done

- 🧠 Trained multiple models (Logistic Regression, Random Forest, XGBoost)
- 📈 Achieved ~73% accuracy on unseen test data
- ⚙️ Performed hyperparameter tuning using GridSearchCV
- 📉 Evaluated model using:
  - Accuracy Score (`~73%`)
  - Log Loss (`~0.53`)
  - Brier Score (`~0.18`)

---

## 🚧 What’s Coming Next

- [ ] Save trained models to `.pkl` for later use
- [ ] Build a match simulator (`simulate_match(teamA, teamB)`)
- [ ] Allow user-defined fantasy teams (e.g., *India vs RCB*)
- [ ] Build betting EV calculator from model outputs
- [ ] Add web interface (Streamlit or Flask)

---

## 🧪 Quick Start (Model Training)

```python
# Load and preprocess dataset
df = pd.read_csv("t20_features_full.csv")
# Encode categorical variables, split into train/test
# Train model
model = RandomForestClassifier(...)
model.fit(X_train, y_train)
