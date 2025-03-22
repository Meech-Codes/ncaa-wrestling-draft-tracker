import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app_utils.app_config import APP_CONFIG

def render_points_breakdown():
    """
    Render the Points Breakdown section of the Analytics Dashboard.
    Shows detailed breakdown of team points by category.
    """
    st.subheader("Team Points Breakdown")
    
    try:
        # Prepare data
        team_df = st.session_state['team_summary'].copy()
        
        # Ensure all columns exist, with defaults if missing
        if 'total_advancement' not in team_df.columns:
            team_df['total_advancement'] = 0
        if 'total_bonus' not in team_df.columns:
            team_df['total_bonus'] = 0
        if 'placement_points' not in team_df.columns:
            team_df['placement_points'] = 0
        
        # Sort by total points
        team_df = team_df.sort_values('total_points', ascending=False)
        
        # Create a plotly stacked bar chart
        render_stacked_points_chart(team_df)
        
        # Create more detailed analysis for desktop or simplified for mobile
        is_mobile = check_mobile_view()
        
        if is_mobile:
            # Simplified view for mobile
            render_simplified_analysis(team_df)
        else:
            # Full analysis for desktop
            render_full_analysis(team_df)
        
    except Exception as e:
        st.error(f"Error creating Points Breakdown visualization: {e}")
        import traceback
        st.error(traceback.format_exc())

def render_stacked_points_chart(team_df):
    """Render a stacked bar chart of team points by category."""
    fig = go.Figure()
    
    # Colors from config
    colors = APP_CONFIG['colors']
    
    # Add advancement points
    fig.add_trace(go.Bar(
        name='Advancement',
        x=team_df['owner'],
        y=team_df['total_advancement'],
        marker_color=colors['primary'],
        text=team_df['total_advancement'].round(1),
        textposition='auto'
    ))
    
    # Add bonus points
    fig.add_trace(go.Bar(
        name='Bonus',
        x=team_df['owner'],
        y=team_df['total_bonus'],
        marker_color=colors['secondary'],
        text=team_df['total_bonus'].round(1),
        textposition='auto'
    ))
    
    # Add placement points
    fig.add_trace(go.Bar(
        name='Placement',
        x=team_df['owner'],
        y=team_df['placement_points'],
        marker_color=colors['tertiary'],
        text=team_df['placement_points'].round(1),
        textposition='auto'
    ))
    
    # Update layout - responsive height
    height = 500 if not check_mobile_view() else 400
    
    # Update layout
    fig.update_layout(
        barmode='stack',
        title='Team Points by Category',
        xaxis_title='Team',
        yaxis_title='Points',
        legend_title='Point Category',
        height=height,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def render_simplified_analysis(team_df):
    """Render a simplified analysis view for mobile devices."""
    st.subheader("Team Performance Analysis")
    
    # Calculate point source breakdown as percentages
    normalized_df = team_df.copy()
    for _, row in normalized_df.iterrows():
        total = row['total_points']
        if total > 0:  # Avoid division by zero
            normalized_df.at[_, 'total_advancement'] = row['total_advancement'] / total * 100
            normalized_df.at[_, 'total_bonus'] = row['total_bonus'] / total * 100
            normalized_df.at[_, 'placement_points'] = row['placement_points'] / total * 100
    
    # Create horizontal stacked bar chart
    fig = go.Figure()
    
    # Add advancement points percentage
    fig.add_trace(go.Bar(
        name='Advancement',
        y=normalized_df['owner'],
        x=normalized_df['total_advancement'],
        marker_color=APP_CONFIG['colors']['primary'],
        orientation='h',
        text=[f"{x:.1f}%" for x in normalized_df['total_advancement']],
        textposition='auto'
    ))
    
    # Add bonus points percentage
    fig.add_trace(go.Bar(
        name='Bonus',
        y=normalized_df['owner'],
        x=normalized_df['total_bonus'],
        marker_color=APP_CONFIG['colors']['secondary'],
        orientation='h',
        text=[f"{x:.1f}%" for x in normalized_df['total_bonus']],
        textposition='auto'
    ))
    
    # Add placement points percentage
    fig.add_trace(go.Bar(
        name='Placement',
        y=normalized_df['owner'],
        x=normalized_df['placement_points'],
        marker_color=APP_CONFIG['colors']['tertiary'],
        orientation='h',
        text=[f"{x:.1f}%" for x in normalized_df['placement_points']],
        textposition='auto'
    ))
    
    # Update layout
    fig.update_layout(
        barmode='stack',
        title='Points Composition (%)',
        xaxis_title='Percentage of Total Points',
        yaxis_title='Team',
        legend_title='Point Source',
        yaxis={'categoryorder': 'total ascending'},
        height=400
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def render_full_analysis(team_df):
    """Render the full analysis view for desktop devices."""
    st.subheader("Team Performance Analysis")
    
    # Create two columns for different metrics
    col1, col2 = st.columns(2)
    
    with col1:
        # Point Source Distribution - Horizontal Stacked Bar (% instead of raw values)
        normalized_df = team_df.copy()
        for _, row in normalized_df.iterrows():
            total = row['total_points']
            if total > 0:  # Avoid division by zero
                normalized_df.at[_, 'total_advancement'] = row['total_advancement'] / total * 100
                normalized_df.at[_, 'total_bonus'] = row['total_bonus'] / total * 100
                normalized_df.at[_, 'placement_points'] = row['placement_points'] / total * 100
        
        fig = go.Figure()
        
        # Add advancement points percentage
        fig.add_trace(go.Bar(
            name='Advancement',
            y=normalized_df['owner'],
            x=normalized_df['total_advancement'],
            marker_color=APP_CONFIG['colors']['primary'],
            orientation='h',
            text=[f"{x:.1f}%" for x in normalized_df['total_advancement']],
            textposition='auto'
        ))
        
        # Add bonus points percentage
        fig.add_trace(go.Bar(
            name='Bonus',
            y=normalized_df['owner'],
            x=normalized_df['total_bonus'],
            marker_color=APP_CONFIG['colors']['secondary'],
            orientation='h',
            text=[f"{x:.1f}%" for x in normalized_df['total_bonus']],
            textposition='auto'
        ))
        
        # Add placement points percentage
        fig.add_trace(go.Bar(
            name='Placement',
            y=normalized_df['owner'],
            x=normalized_df['placement_points'],
            marker_color=APP_CONFIG['colors']['tertiary'],
            orientation='h',
            text=[f"{x:.1f}%" for x in normalized_df['placement_points']],
            textposition='auto'
        ))
        
        # Update layout
        fig.update_layout(
            barmode='stack',
            title='Points Composition (%)',
            xaxis_title='Percentage of Total Points',
            yaxis_title='Team',
            legend_title='Point Source',
            yaxis={'categoryorder': 'total ascending'},
            height=400
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Calculate team efficiency metrics
        efficiency_df = pd.DataFrame({
            'Team': team_df['owner'],
            'Total Points': team_df['total_points'],
            'Avg Points per Win': team_df['total_points'] / (team_df['champ_wins'] + team_df['cons_wins']).replace(0, np.nan),
            'Bonus Point Ratio': team_df['total_bonus'] / (team_df['champ_wins'] + team_df['cons_wins']).replace(0, np.nan)
        }).dropna()
        
        # Round the metrics
        efficiency_df['Avg Points per Win'] = efficiency_df['Avg Points per Win'].round(2)
        efficiency_df['Bonus Point Ratio'] = efficiency_df['Bonus Point Ratio'].round(2)
        
        fig = px.scatter(
            efficiency_df,
            x='Avg Points per Win',
            y='Bonus Point Ratio',
            size='Total Points',
            color='Team',
            text='Team',
            title='Team Efficiency Metrics',
            labels={'Avg Points per Win': 'Average Points per Win', 
                    'Bonus Point Ratio': 'Bonus Points per Win'}
        )
        
        fig.update_traces(
            textposition='top center',
            marker=dict(sizemin=5)
        )
        
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Add a third visualization - Advancement Success Rate
    st.subheader("Advancement Success Analysis")
    
    # Calculate advancement percentage (championship success vs consolation success)
    success_df = pd.DataFrame()
    success_df['Team'] = team_df['owner']
    success_df['Championship Pts'] = team_df['champ_advancement'] + team_df['champ_bonus']
    success_df['Consolation Pts'] = team_df['cons_advancement'] + team_df['cons_bonus']
    success_df['Placement Pts'] = team_df['placement_points']
    success_df['Total Pts'] = team_df['total_points']
    
    # Sort by total points
    success_df = success_df.sort_values('Total Pts', ascending=False)
    
    # Create a grouped bar chart comparing championship vs consolation points
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Championship',
        x=success_df['Team'],
        y=success_df['Championship Pts'],
        marker_color='blue',
        text=success_df['Championship Pts'].round(1),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Consolation',
        x=success_df['Team'],
        y=success_df['Consolation Pts'],
        marker_color='orange',
        text=success_df['Consolation Pts'].round(1),
        textposition='auto'
    ))
    
    fig.add_trace(go.Bar(
        name='Placement',
        x=success_df['Team'],
        y=success_df['Placement Pts'],
        marker_color='green',
        text=success_df['Placement Pts'].round(1),
        textposition='auto'
    ))
    
    fig.update_layout(
        barmode='group',
        title='Points by Bracket Type',
        xaxis_title='Team',
        yaxis_title='Points',
        legend_title='Bracket',
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