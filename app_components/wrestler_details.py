import streamlit as st
import pandas as pd
import plotly.express as px
from app_utils.data_loader import get_filtered_results

def render_wrestler_details():
    """
    Render the Wrestler Details tab with responsive layout.
    Shows detailed information about individual wrestlers.
    """
    st.header("Wrestler Details")
    
    if 'results_df' in st.session_state and not st.session_state['results_df'].empty:
        results_df = st.session_state['results_df']
        
        # Create a more mobile-friendly filter layout
        col1, col2 = st.columns(2)
        
        with col1:
            teams = ['All'] + sorted(results_df['owner'].unique().tolist())
            selected_team = st.selectbox("Filter by Team:", teams, key="wrestler_team")
        
        with col2:
            weight_classes = ['All'] + sorted(results_df['weight'].unique().tolist())
            selected_weight = st.selectbox("Filter by Weight Class:", weight_classes, key="wrestler_weight")
        
        # Get filtered data
        filtered_df = get_filtered_results(selected_weight, selected_team)
        
        if not filtered_df.empty:
            # Display wrestler table
            display_wrestler_table(filtered_df)
            
            # Show match details for selected wrestler
            display_wrestler_matches(filtered_df)
            
            # Add visualization for the filtered wrestlers
            if len(filtered_df) > 1:  # Only show visualization if multiple wrestlers
                display_wrestler_visualization(filtered_df)
        else:
            st.info("No wrestlers found for the selected filters.")
    else:
        st.info("No wrestler data available. Please update results.")

def display_wrestler_table(filtered_df):
    """Display the table of wrestlers with all details."""
    # Reorder and select columns for display
    cols_to_display = [
        'Wrestler', 'weight', 'seed', 'owner', 
        'champ_wins', 'champ_advancement', 'champ_bonus',
        'cons_wins', 'cons_advancement', 'cons_bonus', 
        'placement', 'placement_points', 'total_points'
    ]
    
    # Filter to columns that exist
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
    
    # Sort by total points (highest first)
    display_df = display_df.sort_values('Total Pts', ascending=False)
    
    # Add informative message for mobile users
    st.markdown("Scroll horizontally if needed on mobile devices")
    
    # Display the dataframe
    st.dataframe(display_df, use_container_width=True)

def display_wrestler_matches(filtered_df):
    """Display match details for a selected wrestler."""
    st.subheader("Match Details")
    
    # Get list of wrestlers
    wrestlers = filtered_df['Wrestler'].tolist()
    
    if wrestlers:
        # Let user select a wrestler
        selected_wrestler = st.selectbox("Select Wrestler:", wrestlers)
        
        # Get the wrestler's row
        wrestler_row = filtered_df[filtered_df['Wrestler'] == selected_wrestler].iloc[0]
        
        # Check if match data exists
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
                # Convert to DataFrame
                matches_df = pd.DataFrame(matches_data)
                
                # Style the dataframe
                def highlight_result(val):
                    if isinstance(val, str) and val.startswith('W'):
                        return 'background-color: #c6efce; color: #006100'
                    elif isinstance(val, str) and val.startswith('L'):
                        return 'background-color: #ffc7ce; color: #9c0006'
                    return ''
                
                # Display matches with styling
                st.dataframe(
                    matches_df.style.applymap(highlight_result, subset=['Result']),
                    use_container_width=True
                )
                
                # Display point summary
                display_point_summary(matches_df)
            else:
                st.info("No match details available for this wrestler.")
        else:
            st.info("No match details available for this wrestler.")

def display_point_summary(matches_df):
    """Display a summary of points earned by the wrestler."""
    total_advancement = matches_df['Advancement'].sum()
    total_bonus = matches_df['Bonus'].sum()
    total_points = matches_df['Total'].sum()
    
    # Create a responsive layout
    is_mobile = check_mobile_view()
    
    if is_mobile:
        # Stack metrics on mobile
        st.metric("Total Advancement Points", f"{total_advancement}")
        st.metric("Total Bonus Points", f"{total_bonus}")
        st.metric("Total Points", f"{total_points}")
    else:
        # Use columns on desktop
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Advancement Points", f"{total_advancement}")
        col2.metric("Total Bonus Points", f"{total_bonus}")
        col3.metric("Total Points", f"{total_points}")

def display_wrestler_visualization(filtered_df):
    """Display a visualization of wrestler performance."""
    st.subheader("Wrestler Performance Comparison")
    
    # Create a bar chart of total points by wrestler
    try:
        # Prepare data
        chart_df = filtered_df[['Wrestler', 'total_points']].copy()
        chart_df.columns = ['Wrestler', 'Total Points']
        
        # Sort by points (descending)
        chart_df = chart_df.sort_values('Total Points', ascending=False)
        
        # Create chart
        fig = px.bar(
            chart_df,
            x='Wrestler',
            y='Total Points',
            color='Total Points',
            color_continuous_scale='Viridis',
            text='Total Points'
        )
        
        # Update layout for responsiveness
        fig.update_layout(
            title='Wrestler Points Comparison',
            xaxis_title='Wrestler',
            yaxis_title='Total Points',
            xaxis={'categoryorder': 'total descending'},
            height=400 if not check_mobile_view() else 300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        # Display chart
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        # Silently fail if visualization can't be created
        pass

def check_mobile_view():
    """Check if current view is likely on a mobile device."""
    # This is a simple estimation based on screen width
    try:
        # For now we'll use a simple check based on CSS media queries
        return False  # Default to desktop for server-side rendering
    except:
        return False