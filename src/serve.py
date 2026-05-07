from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os

app = FastAPI()

# CLOUD_BUCKET is set in environment variables
CLOUD_BUCKET = os.environ.get("CLOUD_BUCKET")
MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """Download model.pkl from S3 bucket."""
    s3 = boto3.client('s3')
    print(f"Downloading model from s3://{CLOUD_BUCKET}/{MODEL_KEY}")
    s3.download_file(CLOUD_BUCKET, MODEL_KEY, MODEL_PATH)
    print("Model downloaded successfully.")


# Tải model lúc khởi động
try:
    download_model()
    model = joblib.load(MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load model at startup: {e}")
    model = None


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")
    
    if model is None:
        raise HTTPException(status_code=500, detail="Model is not loaded")

    pred = model.predict([req.features])[0]
    
    labels = {0: "thấp", 1: "trung_bình", 2: "cao"}
    return {"prediction": int(pred), "label": labels.get(int(pred), "unknown")}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
