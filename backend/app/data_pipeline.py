import pandas as pd 
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/sales_data.csv')

def load_sales_data():
    """Reads sales dataset, normalizes columns and aggregates daily sales."""
    if not os.path.exists(DATA_PATH):
        return {'error': 'sales_data.csv missing in backend/data/ folder'}

    df = pd.read_csv(DATA_PATH)

    # Normalize column names with underscore (_) 
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')   

    date_col = next((col for col in ['order_date', 'date', 'orderdate', 'transaction_date'] if col in df.columns), None)
    sales_col = next((col for col in ['sales', 'total_sales', 'amount', 'sales_amount'] if col in df.columns), None)

    if not date_col or not sales_col:
        return {"error": f"Required columns not found in dataset. Detected: {list(df.columns)}"}

    # sales data usually parses standard datetime formats safely
    df['date'] = pd.to_datetime(df[date_col], errors='coerce')
    df['sales'] = pd.to_numeric(df[sales_col], errors='coerce')
    
    df = df.dropna(subset=['date', 'sales'])
    
    # Daily aggregation
    daily_sales = df.groupby('date')['sales'].sum().reset_index().sort_values('date')
    daily_sales['date'] = daily_sales['date'].dt.strftime('%Y-%m-%d')
    
    # Top 50 recent rows for quick frontend visualization
    return daily_sales.tail(50).to_dict(orient="records")