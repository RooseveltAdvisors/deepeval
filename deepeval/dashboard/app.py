import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta
import glob
from deepeval.constants import RESULTS_DIR

# Set page config
st.set_page_config(
    page_title="DeepEval Dashboard",
    page_icon="🔍",
    layout="wide"
)

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_evaluation_data():
    """Load all CSV files from the results directory."""
    all_files = glob.glob(os.path.join(RESULTS_DIR, "deepeval_results_*.csv"))
    if not all_files:
        return None
        
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return None

def main():
    # Header
    st.title("🔍 DeepEval Dashboard")
    st.markdown("---")
    
    # Load data
    df = load_evaluation_data()
    if df is None:
        st.warning("No evaluation results found. Run some tests first!")
        return
        
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d_%H%M%S')
    
    # Sidebar filters
    st.sidebar.title("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['timestamp'].min().date(), df['timestamp'].max().date()),
        min_value=df['timestamp'].min().date(),
        max_value=df['timestamp'].max().date()
    )
    
    # Metric filter
    available_metrics = df['metric_name'].unique()
    selected_metrics = st.sidebar.multiselect(
        "Select Metrics",
        available_metrics,
        default=available_metrics
    )
    
    # Filter data
    mask = (
        (df['timestamp'].dt.date >= date_range[0]) &
        (df['timestamp'].dt.date <= date_range[1]) &
        (df['metric_name'].isin(selected_metrics))
    )
    filtered_df = df[mask]
    
    # Layout
    col1, col2 = st.columns(2)
    
    # Overall Success Rate
    with col1:
        success_rate = (filtered_df['success'].mean() * 100)
        st.metric("Overall Success Rate", f"{success_rate:.1f}%")
        
        # Success rate by metric
        fig_success = px.bar(
            filtered_df.groupby('metric_name')['success'].mean().reset_index(),
            x='metric_name',
            y='success',
            title='Success Rate by Metric',
            labels={'success': 'Success Rate', 'metric_name': 'Metric'},
            color='metric_name'
        )
        fig_success.update_yaxes(range=[0, 1])
        st.plotly_chart(fig_success, use_container_width=True)
    
    # Score Distribution
    with col2:
        avg_score = filtered_df['score'].mean()
        st.metric("Average Score", f"{avg_score:.2f}")
        
        # Score distribution by metric
        fig_scores = px.box(
            filtered_df,
            x='metric_name',
            y='score',
            title='Score Distribution by Metric',
            labels={'score': 'Score', 'metric_name': 'Metric'},
            color='metric_name'
        )
        st.plotly_chart(fig_scores, use_container_width=True)
    
    # Timeline
    st.subheader("Evaluation Timeline")
    timeline_df = filtered_df.groupby(['timestamp', 'metric_name'])['success'].mean().reset_index()
    fig_timeline = px.line(
        timeline_df,
        x='timestamp',
        y='success',
        color='metric_name',
        title='Success Rate Over Time',
        labels={'success': 'Success Rate', 'timestamp': 'Date'}
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Detailed Results Table
    st.subheader("Detailed Results")
    st.dataframe(
        filtered_df[[
            'timestamp', 'test_case_name', 'metric_name',
            'score', 'threshold', 'success', 'reason', 'error'
        ]].sort_values('timestamp', ascending=False),
        use_container_width=True
    )

if __name__ == "__main__":
    main() 