from fastapi import FastAPI
import joblib 
from .schemas import MatchInput
import pandas as pd
import numpy as np

app = FastAPI(title='Cricket Match Winner Prediction API')

MODELS_DIR = "backend/models/"
model = joblib.load(f"{MODELS_DIR}matchWinner.pkl")
label_enc = joblib.load(f"{MODELS_DIR}label_encoders.pkl")
scaler = joblib.load(f"{MODELS_DIR}scaler.pkl")

TRAINING_COLUMNS = [
    'teamA', 'teamB', 'venue', 'toss_winner', 'toss_decision', 'competition',
    'teamA_win_pct_last5', 'teamB_win_pct_last5', 'teamA_vs_teamB_h2h',
    'teamA_avg_runs_scored', 'teamB_avg_runs_conceded', 'teamB_avg_runs_scored',
    'teamA_avg_runs_conceded', 'venue_win_bias_teamA', 'venue_win_bias_teamB',
    'toss_helped_win_rate', 'batting_first_win_pct', 'toss_decision_match_teamA',
    'toss_decision_match_teamB', 'is_home_teamA', 'teamA_form_score', 'teamB_form_score'
]


@app.get("/")
def home():
    return {"message": "CricPred API is working!"}

@app.post("/predict")
def predict(input_data: MatchInput):
    input_df = pd.DataFrame([input_data.dict()])

    dummy_values = {
        'teamA_win_pct_last5': 0.48, 'teamB_win_pct_last5': 0.48, 'teamA_vs_teamB_h2h': 0.48,
        'teamA_avg_runs_scored': 140.0, 'teamB_avg_runs_conceded': 139.7, 'teamB_avg_runs_scored': 139.5,
        'teamA_avg_runs_conceded': 140.1, 'venue_win_bias_teamA': 0.18, 'venue_win_bias_teamB': 0.14,
        'toss_helped_win_rate': 0.48, 'batting_first_win_pct': 0.46, 'toss_decision_match_teamA': 0.18,
        'toss_decision_match_teamB': 0.18, 'is_home_teamA': 0.01, 'teamA_form_score': 14.5,
        'teamB_form_score': 14.4
    }
    
    for col, value in dummy_values.items():
        input_df[col] = value

    for col, encoder in label_enc.items():
        if col in input_df.columns:
            try:
                input_df[col] = encoder.transform(input_df[col])
            except ValueError:
                input_df[col] = -1
    
    input_df = input_df[TRAINING_COLUMNS]

    input_scaled = scaler.transform(input_df)

    win_probability_teamA = model.predict_proba(input_scaled)[0][1]

    return {
        "predicted_winner_is_teamA": bool(win_probability_teamA > 0.5),
        "win_probability_for_teamA": float(win_probability_teamA)
    }