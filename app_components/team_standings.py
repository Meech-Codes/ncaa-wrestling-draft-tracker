import streamlit as st
import pandas as pd
import plotly.express as px
from app_utils.app_config import APP_CONFIG

def render_team_standings():
    """Render the Team Standings tab with responsive layout."""
    st.header("Team Standings")
    
    if 'team_summary' in st.session_state and not st.session_state['team_summary'].empty:
        try:
            # Prepare data
            team_df = st.session_state['team_summary'].copy()
            results_df = st.session_state['results_df'].copy()
            
            # Calculate additional metrics
            team_df = calculate_team_metrics(team_df, results_df)
            
            # Sort by total points
            team_df = team_df.sort_values('total_points', ascending=False)
            
            # Prepare display dataframe
            display_df = prepare_display_dataframe(team_df)
            
            # Create responsive layout
            is_mobile = check_mobile_view()
            
            if is_mobile:
                # Mobile view - stack visualizations
                render_team_bar_chart(display_df)
                st.dataframe(display_df, use_container_width=True, height=400)
                render_efficiency_chart(display_df)
            else:
                # Desktop view - side by side
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    render_team_bar_chart(display_df)
                
                with col2:
                    st.dataframe(display_df, use_container_width=True, height=400)
                
                # Efficiency metrics below
                render_efficiency_chart(display_df)
                
        except Exception as e:
            st.error(f"Error displaying team standings: {e}")
            import traceback
            st.error(traceback.format_exc())
    else:
        st.info("No team standings data available. Please update results.")

def calculate_team_metrics(team_df, results_df):
    """Calculate additional team metrics."""
    # 1. Points per wrestler
    team_df['Wrestlers with Points'] = team_df.get('Wrestlers with Points', pd.Series([0] * len(team_df)))
    team_df['Pts per Wrestler'] = (team_df['total_points'] / team_df['Wrestlers with Points']).fillna(0).round(2)
    
    # 2. Bonus point efficiency (% of points from bonus)
    team_df['Bonus %'] = (team_df['total_bonus'] / team_df['total_points'] * 100).fillna(0).round(1)
    
    # 3. Calculate All-Americans (wrestlers who placed in top 8)
    if 'placement' in results_df.columns:
        all_americans = results_df[results_df['placement'].notna()].groupby('owner').size()
        team_df['All-Americans'] = team_df.index.map(
            lambda x: all_americans.get(x, 0) if x in all_americans.index else 0
        )
    else:
        team_df['All-Americans'] = 0
        
    return team_df

def prepare_display_dataframe(team_df):
    """Prepare dataframe for display."""
    # Reset index for display
    display_df = team_df.reset_index(drop=True)
    display_df.index = display_df.index + 1  # Start at 1 for ranking
    
    # Select columns for display and rename
    cols_to_display = [
        'owner', 'total_points', 'total_advancement', 'total_bonus', 
        'placement_points', 'Pts per Wrestler', 'Bonus %', 'All-Americans'
    ]
    cols_to_display = [col for col in cols_to_display if col in display_df.columns]
    
    display_df = display_df[cols_to_display].rename(columns={
        'owner': 'Team',
        'total_points': 'Total Points',
        'total_advancement': 'Adv Points',
        'total_bonus': 'Bonus Points',
        'placement_points': 'Place Points'
    })
    
    return display_df

def render_team_bar_chart(display_df):
    """Render horizontal bar chart of team points."""
    # Create horizontal bar chart of total points
    bar_fig = px.bar(
        display_df, 
        y='Team', 
        x='Total Points',
        orientation='h',
        color='Total Points',
        color_continuous_scale='Viridis',
        text='Total Points'
    )
    
    bar_fig.update_layout(
        title='Team Rankings by Total Points',
        yaxis={'categoryorder': 'total ascending'},
        height=400,
        margin=dict(l=0, r=10, t=30, b=0)  # Adjusted margins for mobile
    )
    
    # Auto-sizing for better mobile experience
    st.plotly_chart(bar_fig, use_container_width=True)

def render_efficiency_chart(display_df):
    """Render the efficiency metrics chart."""
    st.subheader("Efficiency Metrics")
    
    # Create bubble chart: x=Pts per Wrestler, y=Bonus %, size=Total Points
    if 'Pts per Wrestler' in display_df.columns and 'Bonus %' in display_df.columns:
        bubble_fig = px.scatter(
            display_df,
            x='Pts per Wrestler',
            y='Bonus %',
            size='Total Points',
            color='Team',
            hover_name='Team',
            text='Team',
            size_max=50,
            title='Team Efficiency: Points per Wrestler vs Bonus Point %'
        )
        
        bubble_fig.update_traces(
            textposition='top center',
            marker=dict(sizemin=5)
        )
        
        # Adjust height for mobile
        height = 500 if not check_mobile_view() else 350
        
        bubble_fig.update_layout(
            xaxis_title='Points per Wrestler',
            yaxis_title='Bonus Point Percentage',
            height=height,
            margin=dict(l=0, r=0, t=30, b=0)  # Adjusted margins for mobile
        )
        
        st.plotly_chart(bubble_fig, use_container_width=True)

def check_mobile_view():
    """Check if current view is likely on a mobile device."""
    # This is a simple estimation based on screen width,
    # you may need to adjust the threshold based on your users
    try:
        # Try to get screen width via session state or other methods
        # For now we'll use a simple check based on CSS media queries
        # which will be applied on the client side
        return False  # Default to desktop for server-side rendering
    except:
        return False