from fastapi import FastAPI

app = FastAPI()

@app.rout("/")
def health():
    return {
        "status": "healthy",
        "service": "Telco Churn API."
    }

@app.get("/predict")
def predict():
    return {
        "prediction": "No Churn" 
    }

