import streamlit as st
import pandas as pd
from ncaa_wrestling_tracker.main import main
from ncaa_wrestling_tracker.processors.scorer import calculate_team_points

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_tournament_data():
    """
    Fetch tournament data from the ncaa_wrestling_tracker package.
    Uses caching to improve performance.
    
    Returns:
        tuple: (results_df, round_df, placements_df)
    """
    try:
        # Run the main function from your package
        results_df, round_df, placements_df = main(return_results=True)
        
        # Check for expected columns
        if 'champ_wins' not in results_df.columns:
            st.warning("Data missing expected columns. Some visualizations may not display correctly.")
        
        return results_df, round_df, placements_df
    except Exception as e:
        st.error(f"Error fetching tournament data: {e}")
        # Return empty DataFrames if there's an error
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def calculate_team_summary(results_df):
    """
    Calculate team summary statistics using the scorer from your package.
    
    Args:
        results_df (DataFrame): DataFrame with wrestler results
        
    Returns:
        DataFrame: Team summary statistics
    """
    if results_df.empty:
        return pd.DataFrame()
    
    try:
        team_summary = calculate_team_points(results_df)
        return team_summary
    except Exception as e:
        st.error(f"Error calculating team points: {e}")
        return pd.DataFrame()

def load_or_process_data(update_button=False):
    """
    Load or process data and store in session state.
    
    Args:
        update_button (bool): Whether the update button was clicked
    """
    # Check if we need to update the data
    if update_button or 'results_df' not in st.session_state:
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
                    st.success("Results updated successfully!")
            except Exception as e:
                # Only show error if explicitly updating
                if update_button:
                    st.error(f"Error processing results: {e}")
                    
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