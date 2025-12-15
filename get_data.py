import requests
import pandas as pd
import json
from datetime import datetime

def fetch_bls_data(series_ids, start_year, end_year):
    """Fetch data from BLS Public API."""
    url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year)
    }
    
    headers = {"Content-Type": "application/json"}
    
    print(f"Fetching data from BLS API for years {start_year}-{end_year}...")
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")
    
    data = response.json()
    
    if data.get("status") != "REQUEST_SUCCEEDED":
        raise Exception(f"API request failed: {data.get('message', 'Unknown error')}")
    
    print("Data fetched successfully!")
    return data

def clean_and_process_data(api_response):
    """Clean and process the BLS API response."""
    series_names = {
        "LNS14000000": "Unemployment_Rate",
        "CES0000000001": "Total_Nonfarm_Employees",
        "CES0500000003": "Avg_Hourly_Earnings",
        "CES0500000007": "Avg_Weekly_Hours"
    }
    
    all_data = []
    
    for series in api_response["Results"]["series"]:
        series_id = series["seriesID"]
        series_name = series_names.get(series_id, series_id)
        
        print(f"Processing {series_name}...")
        
        for item in series["data"]:
            year = item["year"]
            period = item["period"]
            
            if period.startswith("M"):
                month = period[1:]
                date_str = f"{year}-{month}-01"
                
                all_data.append({
                    "date": date_str,
                    "series_name": series_name,
                    "value": item["value"]
                })
    
    df = pd.DataFrame(all_data)
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    
    df_pivot = df.pivot(index="date", columns="series_name", values="value")
    df_pivot = df_pivot.reset_index()
    df_pivot = df_pivot.sort_values("date")
    df_pivot = df_pivot.dropna()
    
    print(f"Processed {len(df_pivot)} rows of data")
    
    return df_pivot

# Main execution
series_ids = [
    "LNS14000000",
    "CES0000000001",
    "CES0500000003",
    "CES0500000007"
]

start_year = 2022
end_year = 2025

api_response = fetch_bls_data(series_ids, start_year, end_year)
df_clean = clean_and_process_data(api_response)

df_clean.to_csv("labor_data.csv", index=False)
print(f"\nData successfully saved to labor_data.csv")
print(f"Shape: {df_clean.shape}")
print(f"Date range: {df_clean['date'].min()} to {df_clean['date'].max()}")
