import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
from datetime import datetime

# Add the current directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from your package
from ncaa_wrestling_tracker.main import main
from ncaa_wrestling_tracker.processors.scorer import calculate_team_points
from ncaa_wrestling_tracker import config

# Update config paths to use the repository's Data folder
def setup_config_paths():
    # Determine if we're running on Streamlit Cloud or locally
    is_streamlit_cloud = os.getenv('STREAMLIT_SHARING', '') == 'true'
    
    # Get the repository root path
    if is_streamlit_cloud:
        repo_root = os.path.dirname(os.path.abspath(__file__))
    else:
        repo_root = os.getcwd()  # Current working directory
    
    # Update config paths
    config.BASE_PATH = repo_root
    config.DATA_PATH = os.path.join(repo_root, "Data")
    config.RESULTS_FILE = os.path.join(config.DATA_PATH, "wrestling_results.txt")
    config.DRAFT_CSV = os.path.join(config.DATA_PATH, "ncaa_wrestling_draft.csv")
    config.OUTPUT_DIR = os.path.join(repo_root, "Results")
    
    # Ensure the output directory exists
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    print(f"Using data path: {config.DATA_PATH}")
    print(f"Results file: {config.RESULTS_FILE}")
    print(f"Draft CSV: {config.DRAFT_CSV}")

# Call the setup function
setup_config_paths()

# Set page configuration
st.set_page_config(
    page_title="NCAA Wrestling Tournament Tracker", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page header
st.title("NCAA Wrestling Tournament Tracker")
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Sidebar for debugging information
st.sidebar.subheader("Data Paths")
st.sidebar.text(f"Data folder: {config.DATA_PATH}")
st.sidebar.text(f"Results file: {config.RESULTS_FILE}")
st.sidebar.text(f"Draft CSV: {config.DRAFT_CSV}")

# Check if files exist and display status
results_exists = os.path.exists(config.RESULTS_FILE)
draft_exists = os.path.exists(config.DRAFT_CSV)

st.sidebar.text(f"Results file exists: {results_exists}")
st.sidebar.text(f"Draft CSV exists: {draft_exists}")

if not results_exists or not draft_exists:
    st.sidebar.error("One or more data files are missing!")
    st.sidebar.info("Make sure your repository contains the following files:")
    st.sidebar.code("Data/wrestling_results.txt\nData/ncaa_wrestling_draft.csv")

# Sidebar for controls
st.sidebar.title("Controls")
update_button = st.sidebar.button("Update Results")

# Function to load or process data
def load_or_process_data():
    if update_button or 'results_df' not in st.session_state:
        with st.spinner("Processing tournament results..."):
            try:
                # Verify files exist
                if not os.path.exists(config.RESULTS_FILE):
                    st.error(f"Results file not found: {config.RESULTS_FILE}")
                    return
                if not os.path.exists(config.DRAFT_CSV):
                    st.error(f"Draft CSV not found: {config.DRAFT_CSV}")
                    return
                
                # Run the main function from your package
                results_df, round_df, placements_df = main(return_results=True)
                
                # Debug output to see what's being returned
                st.sidebar.text(f"Results DF shape: {results_df.shape}")
                st.sidebar.text(f"Round DF shape: {round_df.shape}")
                
                # Check if the DataFrames contain the expected columns
                if 'champ_wins' not in results_df.columns:
                    st.warning("Results data is missing expected columns. Available columns:")
                    st.write(results_df.columns.tolist())
                
                team_summary = calculate_team_points(results_df)
                
                # Save to session state
                st.session_state['results_df'] = results_df
                st.session_state['round_df'] = round_df
                st.session_state['placements_df'] = placements_df
                st.session_state['team_summary'] = team_summary
                st.success("Results updated successfully!")
            except Exception as e:
                st.error(f"Error processing results: {e}")
                import traceback
                st.error(traceback.format_exc())
                if 'results_df' not in st.session_state:
                    st.session_state['results_df'] = pd.DataFrame()
                    st.session_state['round_df'] = pd.DataFrame()
                    st.session_state['team_summary'] = pd.DataFrame()
                    st.session_state['placements_df'] = pd.DataFrame()

# Load the data
load_or_process_data()

# Create tabs for different views
tabs = st.tabs(["Team Standings", "Round-by-Round", "Wrestler Details", "Placements"])

with tabs[0]:
    st.header("Team Standings")
    if 'team_summary' in st.session_state and not st.session_state['team_summary'].empty:
        # Display the team standings table
        team_df = st.session_state['team_summary'].copy()
        team_df = team_df.reset_index(drop=True)
        team_df.index = team_df.index + 1  # Start rank at 1
        
        # Format columns for display
        display_df = team_df.copy()
        display_cols = ['owner', 'total_points', 'total_advancement', 'total_bonus', 'placement_points']
        display_cols = [col for col in display_cols if col in display_df.columns]
        display_df = display_df[display_cols]
        
        # Rename columns for display
        display_df.columns = ['Team', 'Total Points', 'Advancement Points', 'Bonus Points', 
                             'Placement Points' if 'placement_points' in display_cols else '']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Create bar chart of team points
        if not team_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(team_df['owner'], team_df['total_points'], color='navy')
            ax.set_ylabel('Total Points')
            ax.set_xlabel('Team')
            ax.set_title('Team Standings')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            st.pyplot(fig)
    else:
        st.info("No team standings data available. Please update results.")

with tabs[1]:
    st.header("Round-by-Round Results")
    if 'round_df' in st.session_state and not st.session_state['round_df'].empty:
        round_df = st.session_state['round_df']
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            weight_classes = ['All'] + sorted(round_df['Weight'].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight Class:", weight_classes)
        
        with col2:
            teams = ['All'] + sorted(round_df['Owner'].unique().tolist())
            selected_team = st.selectbox("Filter by Team:", teams)
        
        # Apply filters
        filtered_df = round_df.copy()
        if selected_weight != 'All':
            filtered_df = filtered_df[filtered_df['Weight'] == selected_weight]
        if selected_team != 'All':
            filtered_df = filtered_df[filtered_df['Owner'] == selected_team]
        
        # Format the dataframe - highlight wins and losses
        def highlight_results(val):
            if pd.isna(val):
                return ''
            elif isinstance(val, str) and val.startswith('W'):
                return 'background-color: #c6efce; color: #006100'  # Green for wins
            elif isinstance(val, str) and val.startswith('L'):
                return 'background-color: #ffc7ce; color: #9c0006'  # Red for losses
            return ''
        
        # Apply styling and display
        st.dataframe(filtered_df.style.applymap(highlight_results), use_container_width=True)
    else:
        st.info("No round-by-round data available. Please update results.")

with tabs[2]:
    st.header("Wrestler Details")
    if 'results_df' in st.session_state and not st.session_state['results_df'].empty:
        results_df = st.session_state['results_df']
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            teams = ['All'] + sorted(results_df['owner'].unique().tolist())
            selected_team = st.selectbox("Filter by Team:", teams, key="wrestler_team")
        
        with col2:
            weight_classes = ['All'] + sorted(results_df['weight'].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight Class:", weight_classes, key="wrestler_weight")
        
        # Apply filters
        filtered_df = results_df.copy()
        if selected_team != 'All':
            filtered_df = filtered_df[filtered_df['owner'] == selected_team]
        if selected_weight != 'All':
            filtered_df = filtered_df[filtered_df['weight'] == selected_weight]
        
        # Reorder and select columns for display
        cols_to_display = ['Wrestler', 'weight', 'seed', 'owner', 
                          'champ_wins', 'champ_advancement', 'champ_bonus',
                          'cons_wins', 'cons_advancement', 'cons_bonus', 
                          'placement', 'placement_points', 'total_points']
        cols_to_display = [col for col in cols_to_display if col in filtered_df.columns]
        
        # Rename columns for better display
        display_df = filtered_df[cols_to_display].copy()
        display_df = display_df.rename(columns={
            'Wrestler': 'Wrestler',
            'weight': 'Weight',
            'seed': 'Seed',
            'owner': 'Team',
            'champ_wins': 'Champ Wins',
            'champ_advancement': 'Champ Adv Pts',
            'champ_bonus': 'Champ Bonus Pts',
            'cons_wins': 'Cons Wins',
            'cons_advancement': 'Cons Adv Pts',
            'cons_bonus': 'Cons Bonus Pts',
            'placement': 'Placement',
            'placement_points': 'Place Pts',
            'total_points': 'Total Pts'
        })
        
        st.dataframe(display_df, use_container_width=True)
        
        # Show match details for selected wrestler
        if not filtered_df.empty:
            st.subheader("Match Details")
            wrestlers = filtered_df['Wrestler'].tolist()
            selected_wrestler = st.selectbox("Select Wrestler:", wrestlers)
            
            wrestler_row = filtered_df[filtered_df['Wrestler'] == selected_wrestler].iloc[0]
            if 'matches' in wrestler_row and wrestler_row['matches']:
                matches_data = []
                for match in wrestler_row['matches']:
                    matches_data.append({
                        'Round': match.get('round', ''),
                        'Opponent': match.get('opponent', ''),
                        'Result': match.get('result', ''),
                        'Type': match.get('win_type_full', ''),
                        'Advancement': match.get('advancement_points', 0),
                        'Bonus': match.get('bonus_points', 0),
                        'Total': match.get('total_points', 0)
                    })
                
                if matches_data:
                    st.dataframe(pd.DataFrame(matches_data))
                else:
                    st.info("No match details available for this wrestler.")
            else:
                st.info("No match details available for this wrestler.")
    else:
        st.info("No wrestler data available. Please update results.")

with tabs[3]:
    st.header("Placements")
    if 'placements_df' in st.session_state and not st.session_state['placements_df'].empty:
        placements_df = st.session_state['placements_df']
        
        # Add weight class filter
        weight_classes = ['All'] + sorted(placements_df['weight'].unique().tolist())
        selected_weight = st.selectbox("Filter by Weight Class:", weight_classes, key="placement_weight")
        
        # Apply filter
        filtered_df = placements_df.copy()
        if selected_weight != 'All':
            filtered_df = filtered_df[filtered_df['weight'] == selected_weight]
        
        # Sort by placement
        if 'placement' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(['weight', 'placement'])
        
        # Display the dataframe
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("No placement data available. Please update results.")

# Footer
st.markdown("---")
st.markdown("NCAA Wrestling Tournament Tracker - Created with Streamlit")