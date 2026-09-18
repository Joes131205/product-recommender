import joblib
from fastapi import FastAPI, HTTPException

clf_model = joblib.load("../model/profit_classification.pkl")
kmeans_model = joblib.load("../model/user_clustering.pkl")
rfm_scaler = joblib.load("rfm_scale.pkl")

app = FastAPI(title="Product Recommendation Model")


@app.get("/")
def health_check():
    return {"ok": True, "message": "healthy"}
