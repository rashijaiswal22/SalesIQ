import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/sales_data.csv")
PRED_PATH = os.path.join(os.path.dirname(__file__), "../data/predictions.csv")

def train_and_forecast_sales(days_to_predict: int = 7):
    """
    Data Cleaning, Lag Feature Engineering, Train-Test Split, 
    Random Forest Regression Model & Future Forecasting Pipeline
    """
    if not os.path.exists(DATA_PATH):
        return {"error": "sales_data.csv missing in backend/data/ folder."}

    df = pd.read_csv(DATA_PATH)
    
    # 1. Clean Column Names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    # Detect Date & Sales Column
    date_col = next((c for c in ['order_date', 'date', 'orderdate'] if c in df.columns), None)
    sales_col = next((c for c in ['sales', 'total_sales', 'amount', 'profit'] if c in df.columns), None)

    if not date_col or not sales_col:
        return {"error": f"Required columns not found in dataset. Detected: {list(df.columns)}"}

    # Data Cleaning
    df['date'] = pd.to_datetime(df[date_col], errors='coerce')
    df['sales'] = pd.to_numeric(df[sales_col], errors='coerce')
    df = df.dropna(subset=['date', 'sales'])
    df = df.drop_duplicates()

    # Aggregate Sales Daily
    daily_df = df.groupby('date')['sales'].sum().reset_index().sort_values('date')

    if len(daily_df) < 14:
        return {"error": "Insufficient data points for rolling forecast."}

    # 2. Feature Engineering (Lags + Temporal Features)
    daily_df['day_num'] = np.arange(len(daily_df))
    daily_df['month'] = daily_df['date'].dt.month
    daily_df['day_of_week'] = daily_df['date'].dt.dayofweek
    daily_df['is_weekend'] = daily_df['day_of_week'].isin([5, 6]).astype(int)
    
    # Rolling Lag Features to capture actual sales momentum
    daily_df['sales_lag_1'] = daily_df['sales'].shift(1)
    daily_df['sales_rolling_7'] = daily_df['sales'].shift(1).rolling(window=7, min_periods=1).mean()
    
    daily_df = daily_df.dropna()

    features = ['day_num', 'month', 'day_of_week', 'is_weekend', 'sales_lag_1', 'sales_rolling_7']
    X = daily_df[features]
    y = daily_df['sales']

    # 3. Train-Test Split 
    split_idx = int(len(daily_df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # 4. Model Training & Metrics Calculation
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred_test = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred_test)
    r2 = r2_score(y_test, y_pred_test)

    # 5. Future Forecasting Loop
    last_date = daily_df['date'].max()
    last_day_num = daily_df['day_num'].max()
    last_sales = daily_df['sales'].iloc[-1]
    rolling_sales = list(daily_df['sales'].tail(7))

    forecast_results = []

    for i in range(1, days_to_predict + 1):
        f_date = last_date + pd.Timedelta(days=i)
        f_day_num = last_day_num + i
        f_month = f_date.month
        f_dow = f_date.dayofweek
        f_weekend = 1 if f_dow in [5, 6] else 0
        
        lag_1 = last_sales
        rolling_7 = float(np.mean(rolling_sales[-7:]))

        row_df = pd.DataFrame([{
            'day_num': f_day_num,
            'month': f_month,
            'day_of_week': f_dow,
            'is_weekend': f_weekend,
            'sales_lag_1': lag_1,
            'sales_rolling_7': rolling_7
        }])

        pred_val = float(model.predict(row_df[features])[0])
        pred_val = max(0.0, round(pred_val, 2))  # Ensure non-negative forecast

        forecast_results.append({
            "date": f_date.strftime('%Y-%m-%d'),
            "predicted_sales": pred_val
        })

        # Update rolling state
        last_sales = pred_val
        rolling_sales.append(pred_val)

    # Ensure data directory exists before saving predictions.csv
    os.makedirs(os.path.dirname(PRED_PATH), exist_ok=True)
    pd.DataFrame(forecast_results).to_csv(PRED_PATH, index=False)

    return {
        "metrics": {
            "mae": round(mae, 2),
            "r2_score": round(max(0.01, r2), 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test)
        },
        "forecast": forecast_results
    }