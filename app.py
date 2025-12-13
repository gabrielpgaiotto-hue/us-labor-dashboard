import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="US Labor Statistics Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    """Load and cache the labor data."""
    df = pd.read_csv("labor_data.csv")
    df["date"] = pd.to_datetime(df["date"])
    return df

def calculate_change(df, column_name):
    """Calculate the change from previous month."""
    if len(df) < 2:
        return 0
    latest = df[column_name].iloc[-1]
    previous = df[column_name].iloc[-2]
    return latest - previous

def format_value(value, metric_type):
    """Format values based on metric type."""
    if metric_type == "rate":
        return f"{value:.1f}%"
    elif metric_type == "employees":
        return f"{value:,.0f}K"
    elif metric_type == "earnings":
        return f"${value:.2f}"
    elif metric_type == "hours":
        return f"{value:.1f}"
    return str(value)

def main():
    # Title and description
    st.title("📊 US Labor Statistics Dashboard")
    st.markdown("""
    This interactive dashboard visualizes key trends in US labor statistics, 
    sourcing data directly from the **Bureau of Labor Statistics (BLS) Public API**.
    
    Data includes the last three years of monthly observations across four critical indicators:
    - **Unemployment Rate** (seasonally adjusted)
    - **Total Nonfarm Employment** (in thousands)
    - **Average Hourly Earnings** (private sector)
    - **Average Weekly Hours** (private sector)
    """)
    
    # Load data
    try:
        df = load_data()
    except FileNotFoundError:
        st.error("⚠️ Data file 'labor_data.csv' not found. Please run 'get_data.py' first to fetch the data.")
        st.stop()
    
    # Display date range
    st.info(f"📅 Data Range: {df['date'].min().strftime('%B %Y')} to {df['date'].max().strftime('%B %Y')}")
    
    # Key Metrics Section
    st.header("📈 Current Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Unemployment Rate
    with col1:
        latest_unemp = df["Unemployment_Rate"].iloc[-1]
        change_unemp = calculate_change(df, "Unemployment_Rate")
        st.metric(
            label="Unemployment Rate",
            value=format_value(latest_unemp, "rate"),
            delta=f"{change_unemp:+.1f}%",
            delta_color="inverse"
        )
    
    # Total Nonfarm Employees
    with col2:
        latest_emp = df["Total_Nonfarm_Employees"].iloc[-1]
        change_emp = calculate_change(df, "Total_Nonfarm_Employees")
        st.metric(
            label="Total Nonfarm Employees",
            value=format_value(latest_emp, "employees"),
            delta=f"{change_emp:+,.0f}K"
        )
    
    # Average Hourly Earnings
    with col3:
        latest_earnings = df["Avg_Hourly_Earnings"].iloc[-1]
        change_earnings = calculate_change(df, "Avg_Hourly_Earnings")
        st.metric(
            label="Avg Hourly Earnings",
            value=format_value(latest_earnings, "earnings"),
            delta=f"${change_earnings:+.2f}"
        )
    
    # Average Weekly Hours
    with col4:
        latest_hours = df["Avg_Weekly_Hours"].iloc[-1]
        change_hours = calculate_change(df, "Avg_Weekly_Hours")
        st.metric(
            label="Avg Weekly Hours",
            value=format_value(latest_hours, "hours"),
            delta=f"{change_hours:+.1f}"
        )
    
    st.divider()
    
    # Interactive Chart Section
    st.header("📉 Time Series Analysis")
    
    # Time range selector
    col1, col2 = st.columns([1, 3])
    
    with col1:
        time_range = st.selectbox(
            "Select Time Range:",
            options=["Full Range", "Last 12 Months", "Last 6 Months"],
            index=0
        )
    
    # Filter data based on time range
    if time_range == "Last 12 Months":
        df_filtered = df.tail(12)
    elif time_range == "Last 6 Months":
        df_filtered = df.tail(6)
    else:
        df_filtered = df
    
    # Series selector
    with col2:
        selected_series = st.multiselect(
            "Select Series to Display:",
            options=[
                "Unemployment_Rate",
                "Total_Nonfarm_Employees",
                "Avg_Hourly_Earnings",
                "Avg_Weekly_Hours"
            ],
            default=["Unemployment_Rate", "Total_Nonfarm_Employees"]
        )
    
    if selected_series:
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Color palette
        colors = {
            "Unemployment_Rate": "#FF6B6B",
            "Total_Nonfarm_Employees": "#4ECDC4",
            "Avg_Hourly_Earnings": "#45B7D1",
            "Avg_Weekly_Hours": "#FFA07A"
        }
        
        # Display names
        display_names = {
            "Unemployment_Rate": "Unemployment Rate (%)",
            "Total_Nonfarm_Employees": "Total Nonfarm Employees (thousands)",
            "Avg_Hourly_Earnings": "Avg Hourly Earnings ($)",
            "Avg_Weekly_Hours": "Avg Weekly Hours"
        }
        
        for series in selected_series:
            fig.add_trace(
                go.Scatter(
                    x=df_filtered["date"],
                    y=df_filtered[series],
                    name=display_names[series],
                    line=dict(color=colors[series], width=2),
                    mode="lines+markers"
                )
            )
        
        fig.update_layout(
            title="US Labor Statistics Trends",
            xaxis_title="Date",
            yaxis_title="Value",
            hovermode="x unified",
            height=500,
            template="plotly_white",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one series to display.")
    
    # Data table
    with st.expander("📋 View Raw Data"):
        st.dataframe(
            df_filtered.sort_values("date", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # Footer
    st.divider()
    st.markdown("""
    **Data Source:** [U.S. Bureau of Labor Statistics](https://www.bls.gov/)  
    **Last Updated:** Check the date range above for the most recent data point.
    """)

if __name__ == "__main__":
    main()