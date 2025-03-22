import streamlit as st
import pandas as pd
import os
import sys
import traceback

# Try to import from the package
try:
    from ncaa_wrestling_tracker.main import main
    from ncaa_wrestling_tracker.processors.scorer import calculate_team_points
    PACKAGE_AVAILABLE = True
except ImportError:
    PACKAGE_AVAILABLE = False
    st.warning("NCAA Wrestling Tracker package not available in this environment.")

# Import the config from app_utils
from app_utils.app_config import setup_config_paths

# Get the configuration
config = setup_config_paths()

# Function to read and parse data files directly if package is not available
def parse_data_files_directly():
    """Parse wrestling data files directly when the package is not available"""
    try:
        st.info("Attempting to read data files directly.")
        
        # Check if data files exist
        if not hasattr(config, 'RESULTS_FILE') or not os.path.exists(config.RESULTS_FILE):
            st.error(f"Results file not found: {getattr(config, 'RESULTS_FILE', 'Not set')}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
            
        if not hasattr(config, 'DRAFT_CSV') or not os.path.exists(config.DRAFT_CSV):
            st.error(f"Draft CSV not found: {getattr(config, 'DRAFT_CSV', 'Not set')}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        # Read the draft CSV
        draft_df = pd.read_csv(config.DRAFT_CSV)
        st.success(f"Draft CSV loaded: {len(draft_df)} rows")
        
        # Create placeholder DataFrames
        results_df = pd.DataFrame()
        round_df = pd.DataFrame()
        placements_df = pd.DataFrame()
        
        # Return preliminary results
        return draft_df, round_df, placements_df
    except Exception as e:
        st.error(f"Error parsing data files: {e}")
        st.error(traceback.format_exc())
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_tournament_data():
    """
    Fetch tournament data from the ncaa_wrestling_tracker package or directly from files.
    
    Returns:
        tuple: (results_df, round_df, placements_df)
    """
    try:
        if PACKAGE_AVAILABLE:
            # Try to use the package's main function
            st.info("Using NCAA Wrestling Tracker package to process data.")
            results_df, round_df, placements_df = main(return_results=True)
            
            # Check for expected columns
            if results_df is not None and not results_df.empty:
                if 'champ_wins' not in results_df.columns:
                    st.warning("Data missing expected columns. Some visualizations may not display correctly.")
                else:
                    st.success("Data loaded successfully through the package.")
                
                return results_df, round_df, placements_df
            else:
                st.warning("Package returned empty data. Trying direct file parsing.")
                return parse_data_files_directly()
        else:
            # Package not available, try direct parsing
            return parse_data_files_directly()
    except Exception as e:
        st.error(f"Error fetching tournament data: {e}")
        st.error(traceback.format_exc())
        # Try direct parsing as a fallback
        return parse_data_files_directly()

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def calculate_team_summary(results_df):
    """
    Calculate team summary statistics.
    
    Args:
        results_df (DataFrame): DataFrame with wrestler results
        
    Returns:
        DataFrame: Team summary statistics
    """
    if results_df.empty:
        return pd.DataFrame()
    
    try:
        if PACKAGE_AVAILABLE:
            # Use the package's function
            team_summary = calculate_team_points(results_df)
        else:
            # Simple calculation as fallback
            st.info("Package not available. Using simplified team summary calculation.")
            teams = results_df['owner'].unique() if 'owner' in results_df.columns else []
            
            # Create an empty DataFrame
            team_summary = pd.DataFrame(index=teams)
            
            # Add base columns
            if 'total_points' in results_df.columns:
                team_summary['total_points'] = results_df.groupby('owner')['total_points'].sum()
            
            if all(col in results_df.columns for col in ['champ_advancement', 'cons_advancement']):
                team_summary['total_advancement'] = (
                    results_df.groupby('owner')['champ_advancement'].sum() + 
                    results_df.groupby('owner')['cons_advancement'].sum()
                )
            
            if all(col in results_df.columns for col in ['champ_bonus', 'cons_bonus']):
                team_summary['total_bonus'] = (
                    results_df.groupby('owner')['champ_bonus'].sum() + 
                    results_df.groupby('owner')['cons_bonus'].sum()
                )
            
            if 'placement_points' in results_df.columns:
                team_summary['placement_points'] = results_df.groupby('owner')['placement_points'].sum()
            
            # Fill NaN values
            team_summary = team_summary.fillna(0)
            
        return team_summary
    except Exception as e:
        st.error(f"Error calculating team points: {e}")
        st.error(traceback.format_exc())
        return pd.DataFrame()

def load_or_process_data(update_button=False):
    """
    Load or process data and store in session state.
    
    Args:
        update_button (bool): Whether the update button was clicked
    """
    # Debug config settings
    st.sidebar.markdown("### Config Settings")
    if hasattr(config, 'DATA_PATH'):
        st.sidebar.info(f"Data path: {config.DATA_PATH}")
        st.sidebar.info(f"Exists: {os.path.exists(config.DATA_PATH)}")
    
    if hasattr(config, 'RESULTS_FILE'):
        st.sidebar.info(f"Results file: {config.RESULTS_FILE}")
        st.sidebar.info(f"Exists: {os.path.exists(config.RESULTS_FILE)}")
    
    if hasattr(config, 'DRAFT_CSV'):
        st.sidebar.info(f"Draft CSV: {config.DRAFT_CSV}")
        st.sidebar.info(f"Exists: {os.path.exists(config.DRAFT_CSV)}")
    
    # Check if we need to update the data
    if update_button or 'results_df' not in st.session_state:
        # Clear cache if update button was clicked
        if update_button:
            st.cache_data.clear()
        
        with st.spinner("Loading tournament results..."):
            try:
                # Fetch data
                results_df, round_df, placements_df = fetch_tournament_data()
                
                # Calculate team summary
                team_summary = calculate_team_summary(results_df)
                
                # Save to session state
                st.session_state['results_df'] = results_df
                st.session_state['round_df'] = round_df
                st.session_state['placements_df'] = placements_df
                st.session_state['team_summary'] = team_summary
                
                # Only show success message if explicitly updating
                if update_button:
                    if not results_df.empty:
                        st.success("Results updated successfully!")
                    else:
                        st.error("No results data was loaded.")
                        
                # Debug output 
                st.sidebar.markdown("### Data Status")
                st.sidebar.info(f"Results DataFrame: {results_df.shape if not results_df.empty else 'Empty'}")
                st.sidebar.info(f"Team Summary: {team_summary.shape if not team_summary.empty else 'Empty'}")
                
            except Exception as e:
                # Only show error if explicitly updating
                if update_button:
                    st.error(f"Error processing results: {e}")
                    st.error(traceback.format_exc())
                    
                # Create empty DataFrames if needed
                if 'results_df' not in st.session_state:
                    st.session_state['results_df'] = pd.DataFrame()
                    st.session_state['round_df'] = pd.DataFrame()
                    st.session_state['placements_df'] = pd.DataFrame()
                    st.session_state['team_summary'] = pd.DataFrame()

# Helper functions for data processing
def get_filtered_results(weight_class='All', team='All'):
    """
    Get filtered results data.
    
    Args:
        weight_class (str): Weight class to filter by, or 'All'
        team (str): Team to filter by, or 'All'
        
    Returns:
        DataFrame: Filtered results data
    """
    if 'results_df' not in st.session_state or st.session_state['results_df'].empty:
        return pd.DataFrame()
        
    filtered_df = st.session_state['results_df'].copy()
    
    if weight_class != 'All':
        filtered_df = filtered_df[filtered_df['weight'] == weight_class]
        
    if team != 'All':
        filtered_df = filtered_df[filtered_df['owner'] == team]
        
    return filtered_df

def get_filtered_rounds(weight_class='All', team='All'):
    """
    Get filtered round-by-round data.
    
    Args:
        weight_class (str): Weight class to filter by, or 'All'
        team (str): Team to filter by, or 'All'
        
    Returns:
        DataFrame: Filtered round data
    """
    if 'round_df' not in st.session_state or st.session_state['round_df'].empty:
        return pd.DataFrame()
        
    filtered_df = st.session_state['round_df'].copy()
    
    if weight_class != 'All':
        filtered_df = filtered_df[filtered_df['Weight'] == weight_class]
        
    if team != 'All':
        filtered_df = filtered_df[filtered_df['Owner'] == team]
        
    return filtered_df