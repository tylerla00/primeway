import os
import joblib
import numpy as np

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Load the trained model and scaler
model = joblib.load(f'{os.getenv("ARTIFACT_DIR_FROM_STEP_2")}/model.pkl')
scaler = joblib.load(f'{os.getenv("ARTIFACT_DIR_FROM_STEP_1")}/scaler.pkl')

class PredictRequest(BaseModel):
    features: list

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        # Validate input
        features = np.array(request.features).reshape(1, -1)

        # Preprocess and predict
        features_scaled = scaler.transform(features)
        prediction = model.predict(features_scaled)

        return {"prediction": int(prediction[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)