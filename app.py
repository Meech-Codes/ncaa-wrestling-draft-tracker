import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import os
import sys

# Import from app components
from app_components.team_standings import render_team_standings
from app_components.round_results import render_round_results
from app_components.wrestler_details import render_wrestler_details
from app_components.placements import render_placements
from app_components.analytics import render_analytics

# Import app utilities
from app_utils.app_config import setup_config_paths
from app_utils.data_loader import load_or_process_data

# Set up the configuration
setup_config_paths()

# Set page configuration with responsive layout
st.set_page_config(
    page_title="NCAA Wrestling Tournament Tracker", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS for better mobile experience
def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "app_assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback inline CSS if file doesn't exist
        st.markdown("""
            <style>
            /* Mobile-friendly adjustments */
            @media (max-width: 768px) {
                .stButton button {
                    width: 100%;
                }
                
                /* Make tables scroll horizontally on mobile */
                .stDataFrame {
                    overflow-x: auto;
                }
                
                /* Adjust chart size for mobile */
                .js-plotly-plot {
                    max-height: 300px !important;
                }
            }
            
            /* Better padding for all devices */
            .stTabs [data-baseweb="tab-panel"] {
                padding-top: 1rem;
            }
            
            /* Improved table styling */
            .dataframe {
                font-size: 14px;
            }
            
            /* Header styling */
            h1, h2, h3 {
                margin-bottom: 0.5rem;
            }
            </style>
        """, unsafe_allow_html=True)

# Load custom CSS
load_custom_css()

# Page header with responsive design
def render_header():
    # Get current time in EST timezone
    eastern = pytz.timezone('US/Eastern')
    est_time = datetime.now(eastern)
    formatted_time = est_time.strftime("%m/%d/%Y %I:%M:%S %p EST")
    
    # Two-column layout for header that stacks on mobile
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("NCAA Wrestling Tournament Tracker")
    with col2:
        st.write(f"Last updated: {formatted_time}")

# Simplified sidebar
def render_sidebar():
    st.sidebar.title("NCAA Wrestling Tournament Tracker")
    st.sidebar.subheader("Controls")
    update_button = st.sidebar.button("Update Results", key="update_results")
    
    # Additional controls can be added here
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("Track NCAA Wrestling Tournament results for fantasy drafts")
    
    return update_button

# Main function
def main():
    # Render header
    render_header()
    
    # Render sidebar and get update button state
    update_button = render_sidebar()
    
    # Load data
    load_or_process_data(update_button)
    
    # Create tabs for different views - responsive tabs work well on mobile
    tabs = st.tabs([
        "Team Standings", 
        "Round-by-Round", 
        "Wrestler Details", 
        "Placements", 
        "Analytics"
    ])
    
    # Render each tab with its component
    with tabs[0]:
        render_team_standings()
    
    with tabs[1]:
        render_round_results()
    
    with tabs[2]:
        render_wrestler_details()
    
    with tabs[3]:
        render_placements()
    
    with tabs[4]:
        render_analytics()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "NCAA Wrestling Draft Tournament Tracker - Created by Demetri D'Orsaneo - v1.0"
    )

# Run the app
if __name__ == "__main__":
    main()