from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from app.data_pipeline import load_sales_data
from app.forecaster import train_and_forecast_sales
from app.insights import generate_business_insights, generate_general_chat_response

app = FastAPI(title="SalesIQ Production API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
@app.get("/")
def read_root():
    return {"message": "SalesIQ Machine Learning API is active!"}

@app.get("/api/historical-sales")
def get_historical_sales():
    return {"data": load_sales_data()}

@app.get("/api/forecast")
def get_sales_forecast(days: int = 7):
    return train_and_forecast_sales(days_to_predict=days)

@app.get("/api/insights")
def get_ai_insights(type: str = "all"):
    historical = load_sales_data()
    forecast_result = train_and_forecast_sales(days_to_predict=7)
    
    forecast = forecast_result.get("forecast", [])
    metrics = forecast_result.get("metrics", {})
    
    insights = generate_business_insights(historical, forecast, metrics, insight_type=type)
    return insights

@app.get("/api/chat")
def general_chat(query: str):
    return generate_general_chat_response(query)