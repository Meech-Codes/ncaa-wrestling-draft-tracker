import streamlit as st
from .points_breakdown import render_points_breakdown
from .weight_analysis import render_weight_analysis
from .enhanced_rankings import render_enhanced_rankings

def render_analytics():
    """
    Render the Analytics Dashboard tab with responsive layout.
    This is the main entry point for the analytics components.
    """
    st.header("Advanced Analytics Dashboard")
    
    # Check if we have data
    if ('team_summary' not in st.session_state or 
        st.session_state['team_summary'].empty or 
        'results_df' not in st.session_state or 
        st.session_state['results_df'].empty):
        
        st.warning("No data available. Please update results to see analytics.")
        return
    
    # Create tabs for analytics sections
    analytics_tabs = st.tabs([
        "Points Breakdown", 
        "Weight Class Analysis", 
        "Enhanced Rankings"
    ])
    
    # Render each analytics component in its tab
    with analytics_tabs[0]:
        render_points_breakdown()
    
    with analytics_tabs[1]:
        render_weight_analysis()
    
    with analytics_tabs[2]:
        render_enhanced_rankings()