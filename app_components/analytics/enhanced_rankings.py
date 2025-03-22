import streamlit as st
import pandas as pd
import plotly.express as px
from app_utils.app_config import APP_CONFIG

def render_enhanced_rankings():
    """
    Render the Enhanced Rankings section of the Analytics Dashboard.
    Provides advanced metrics and visualizations for team rankings.
    """
    st.subheader("Enhanced Team Rankings")
    
    try:
        # Prepare data
        team_df = st.session_state['team_summary'].copy()
        results_df = st.session_state['results_df'].copy()
        
        # Calculate additional metrics
        team_df = calculate_enhanced_metrics(team_df, results_df)
        
        # Sort by total points
        team_df = team_df.sort_values('total_points', ascending=False)
        
        # Prepare dataframe for display
        display_df = prepare_display_dataframe(team_df)
        
        # Check if mobile view
        is_mobile = check_mobile_view()
        
        if is_mobile:
            # Mobile view - stack visualizations and table
            render_rankings_bar_chart(display_df)
            st.dataframe(display_df, use_container_width=True)
            render_efficiency_bubble_chart(display_df)
        else:
            # Desktop view - side by side
            col1, col2 = st.columns([1, 1])
            
            with col1:
                render_rankings_bar_chart(display_df)
            
            with col2:
                st.dataframe(display_df, use_container_width=True, height=400)
            
            # Efficiency metrics below
            render_efficiency_bubble_chart(display_df)
            
            # Additional advanced metrics
            render_advanced_metrics(team_df, results_df)
            
    except Exception as e:
        st.error(f"Error creating Enhanced Rankings visualization: {e}")
        import traceback
        st.error(traceback.format_exc())

def calculate_enhanced_metrics(team_df, results_df):
    """Calculate enhanced metrics for team rankings."""
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
    
    # 4. Championship efficiency (points in championship bracket vs consolation)
    if 'champ_advancement' in team_df.columns and 'champ_bonus' in team_df.columns:
        team_df['Champ Points'] = team_df['champ_advancement'] + team_df['champ_bonus']
        team_df['Cons Points'] = team_df['cons_advancement'] + team_df['cons_bonus']
        team_df['Champ Efficiency'] = (team_df['Champ Points'] / 
                                      (team_df['Champ Points'] + team_df['Cons Points']) * 100).fillna(0).round(1)
    
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
    
    # Add championship efficiency if available
    if 'Champ Efficiency' in team_df.columns:
        cols_to_display.append('Champ Efficiency')
    
    # Filter to columns that exist
    cols_to_display = [col for col in cols_to_display if col in team_df.columns]
    
    display_df = display_df[cols_to_display].rename(columns={
        'owner': 'Team',
        'total_points': 'Total Points',
        'total_advancement': 'Adv Points',
        'total_bonus': 'Bonus Points',
        'placement_points': 'Place Points'
    })
    
    return display_df

def render_rankings_bar_chart(display_df):
    """Render horizontal bar chart of team rankings."""
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
    
    # Update layout - responsive height
    height = 400 if not check_mobile_view() else 300
    
    bar_fig.update_layout(
        title='Team Rankings by Total Points',
        yaxis={'categoryorder': 'total ascending'},
        height=height,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    # Display the chart
    st.plotly_chart(bar_fig, use_container_width=True)

def render_efficiency_bubble_chart(display_df):
    """Render bubble chart of team efficiency metrics."""
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
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(bubble_fig, use_container_width=True)

def render_advanced_metrics(team_df, results_df):
    """Render additional advanced metrics (desktop only)."""
    st.subheader("Advanced Performance Metrics")
    
    # Create championship vs consolation points chart if data available
    if 'Champ Points' in team_df.columns and 'Cons Points' in team_df.columns:
        # Prepare data
        perf_df = pd.DataFrame({
            'Team': team_df.index,
            'Championship Points': team_df['Champ Points'],
            'Consolation Points': team_df['Cons Points'],
            'Placement Points': team_df['placement_points'],
            'Total Points': team_df['total_points']
        })
        
        # Sort by total points
        perf_df = perf_df.sort_values('Total Points', ascending=False)
        
        # Create stacked bar chart
        fig = px.bar(
            perf_df,
            x='Team',
            y=['Championship Points', 'Consolation Points', 'Placement Points'],
            title='Points Distribution by Bracket Type',
            labels={'value': 'Points', 'variable': 'Point Source'},
            color_discrete_sequence=[APP_CONFIG['colors']['primary'], 
                                    APP_CONFIG['colors']['secondary'], 
                                    APP_CONFIG['colors']['tertiary']]
        )
        
        fig.update_layout(
            xaxis_title='Team',
            yaxis_title='Points',
            legend_title='Point Source',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Create a visualization of All-Americans by team if data available
    if 'All-Americans' in team_df.columns:
        # Create a dataframe with team and All-Americans
        aa_df = pd.DataFrame({
            'Team': team_df.index,
            'All-Americans': team_df['All-Americans'],
            'Total Points': team_df['total_points']
        })
        
        # Sort by All-Americans count (descending)
        aa_df = aa_df.sort_values('All-Americans', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            aa_df,
            x='Team',
            y='All-Americans',
            color='Total Points',
            title='All-Americans by Team',
            color_continuous_scale='Viridis',
            text='All-Americans'
        )
        
        fig.update_layout(
            xaxis_title='Team',
            yaxis_title='Number of All-Americans',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def check_mobile_view():
    """Check if current view is likely on a mobile device."""
    # This is a simple estimation based on screen width
    try:
        # For now we'll use a simple check based on CSS media queries
        return False  # Default to desktop for server-side rendering
    except:
        return False