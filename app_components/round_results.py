import streamlit as st
import pandas as pd
from app_utils.app_config import APP_CONFIG
from app_utils.data_loader import get_filtered_rounds

def render_round_results():
    """Render the Round-by-Round Results tab with responsive layout."""
    st.header("Round-by-Round Results")
    
    if 'round_df' in st.session_state and not st.session_state['round_df'].empty:
        round_df = st.session_state['round_df']
        
        # Create responsive filter layout
        col1, col2 = st.columns(2)
        
        with col1:
            weight_classes = ['All'] + sorted(round_df['Weight'].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight Class:", weight_classes)
        
        with col2:
            teams = ['All'] + sorted(round_df['Owner'].unique().tolist())
            selected_team = st.selectbox("Filter by Team:", teams)
        
        # Get filtered data
        filtered_df = get_filtered_rounds(selected_weight, selected_team)
        
        if not filtered_df.empty:
            # Display data with win/loss highlighting
            st.markdown("### Match Results")
            st.markdown("Scroll horizontally if needed on mobile devices")
            
            # Format the dataframe for display
            formatted_df = format_round_results(filtered_df)
            
            # Display with styling
            st.dataframe(
                formatted_df.style.applymap(highlight_results),
                use_container_width=True,
                height=None  # Auto height based on content
            )
            
            # Add summary statistics
            display_summary_stats(filtered_df)
        else:
            st.info("No results found for the selected filters.")
    else:
        st.info("No round-by-round data available. Please update results.")

def format_round_results(df):
    """Format round results dataframe for better display."""
    # Select relevant columns
    display_cols = [
        'Wrestler', 'Weight', 'Owner', 'Seed', 
        'Round 1', 'Round 2', 'Quarters', 'Semis', 'Finals',
        'Cons R1', 'Cons R2', 'Cons R3', 'Cons R4', 'Cons Semis', 'Cons Finals'
    ]
    
    # Filter to columns that exist
    display_cols = [col for col in display_cols if col in df.columns]
    
    return df[display_cols]

def highlight_results(val):
    """
    Apply cell styling based on match result.
    Green for wins, red for losses.
    """
    colors = APP_CONFIG['colors']
    
    if pd.isna(val):
        return ''
    elif isinstance(val, str) and val.startswith('W'):
        return f'background-color: {colors["win"]}; color: {colors["win_text"]}'
    elif isinstance(val, str) and val.startswith('L'):
        return f'background-color: {colors["loss"]}; color: {colors["loss_text"]}'
    return ''

def display_summary_stats(df):
    """Display summary statistics for the filtered data."""
    # Only show if we have enough data
    if len(df) < 2:
        return
        
    st.markdown("### Summary Statistics")
    
    # Calculate win/loss stats
    stats = calculate_win_loss_stats(df)
    
    # Create columns for desktop or stack for mobile
    is_mobile = check_mobile_view()
    
    if is_mobile:
        # Stack on mobile
        for stat_name, stat_value in stats.items():
            st.metric(label=stat_name, value=stat_value)
    else:
        # Use columns on desktop
        cols = st.columns(len(stats))
        for i, (stat_name, stat_value) in enumerate(stats.items()):
            cols[i].metric(label=stat_name, value=stat_value)

def calculate_win_loss_stats(df):
    """Calculate win/loss statistics from the data."""
    stats = {}
    
    # Count total matches
    total_matches = 0
    total_wins = 0
    
    # Loop through all potential match columns
    match_columns = [col for col in df.columns if col.startswith('Round') or 
                   col.startswith('Cons') or 
                   col in ['Quarters', 'Semis', 'Finals']]
    
    for col in match_columns:
        matches = df[col].dropna()
        total_matches += len(matches)
        total_wins += sum(matches.str.startswith('W'))
    
    # Calculate stats
    win_percentage = round(total_wins / total_matches * 100, 1) if total_matches > 0 else 0
    
    # Build stats dictionary
    stats["Total Matches"] = total_matches
    stats["Wins"] = total_wins  
    stats["Losses"] = total_matches - total_wins
    stats["Win Rate"] = f"{win_percentage}%"
    
    return stats

def check_mobile_view():
    """Check if current view is likely on a mobile device."""
    # This is a simple estimation based on screen width
    try:
        # For now we'll use a simple check based on CSS media queries
        return False  # Default to desktop for server-side rendering
    except:
        return False