import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app_utils.app_config import APP_CONFIG

def render_weight_analysis():
    """
    Render the Weight Class Analysis section of the Analytics Dashboard.
    Shows team performance across different weight classes.
    """
    st.subheader("Performance by Weight Class")
    
    try:
        # Prepare data
        results_df = st.session_state['results_df'].copy()
        
        # Create pivot table of points by team and weight class
        pivot_data = results_df.pivot_table(
            values='total_points',
            index='owner',
            columns='weight',
            aggfunc='sum',
            fill_value=0
        )
        
        # Ensure weight classes are in correct order
        weight_order = APP_CONFIG['weight_classes']
        available_weights = [w for w in weight_order if w in pivot_data.columns]
        pivot_data = pivot_data[available_weights]
        
        # Sort teams by total points
        team_order = st.session_state['team_summary'].sort_values('total_points', ascending=False)['owner'].tolist()
        pivot_data = pivot_data.reindex(team_order)
        
        # Check if mobile view
        is_mobile = check_mobile_view()
        
        # Render heatmap
        render_weight_class_heatmap(pivot_data)
        
        # Render team comparison - more interactive on desktop, simpler on mobile
        if is_mobile:
            render_simplified_weight_comparison(pivot_data)
        else:
            render_radar_chart(pivot_data)
        
    except Exception as e:
        st.error(f"Error creating Weight Class Analysis visualization: {e}")
        import traceback
        st.error(traceback.format_exc())

def render_weight_class_heatmap(pivot_data):
    """Render a heatmap of points by team and weight class."""
    # Create heatmap using plotly
    fig = px.imshow(
        pivot_data, 
        labels=dict(x="Weight Class", y="Team", color="Points"),
        x=pivot_data.columns,
        y=pivot_data.index,
        color_continuous_scale='YlGnBu',
        aspect="auto"
    )
    
    # Add annotations with point values
    for i in range(len(pivot_data.index)):
        for j in range(len(pivot_data.columns)):
            value = pivot_data.iloc[i, j]
            fig.add_annotation(
                x=j, y=i, 
                text=str(value) if value > 0 else "",
                showarrow=False,
                font=dict(color="black" if value < 15 else "white")
            )
    
    # Update layout - responsive height
    height = 500 if not check_mobile_view() else 400
    
    # Update layout
    fig.update_layout(
        title='Points by Team and Weight Class',
        height=height,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    # Display the heatmap
    st.plotly_chart(fig, use_container_width=True)

def render_radar_chart(pivot_data):
    """Render a radar chart for selected teams to compare weight class performance."""
    st.subheader("Weight Class Distribution by Team")
    
    # Team selection for radar chart with smart defaults
    default_teams = pivot_data.index.tolist()[:min(3, len(pivot_data.index))]
    
    selected_teams = st.multiselect(
        "Select teams to compare:",
        options=pivot_data.index.tolist(),
        default=default_teams
    )
    
    if selected_teams:
        # Create radar chart
        fig = go.Figure()
        
        for team in selected_teams:
            fig.add_trace(go.Scatterpolar(
                r=pivot_data.loc[team].values,
                theta=pivot_data.columns,
                fill='toself',
                name=team
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True
                )
            ),
            showlegend=True,
            title="Points Distribution Across Weight Classes",
            height=450,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select teams to compare their weight class distribution.")

def render_simplified_weight_comparison(pivot_data):
    """Render a simplified weight class comparison for mobile devices."""
    st.subheader("Weight Class Performance")
    
    # Select just one team for analysis
    team = st.selectbox(
        "Select a team to analyze:",
        options=pivot_data.index.tolist()
    )
    
    if team:
        # Create a bar chart of points by weight class for the selected team
        team_data = pivot_data.loc[team].reset_index()
        team_data.columns = ['Weight Class', 'Points']
        
        # Sort by weight class
        team_data = team_data.sort_values('Weight Class')
        
        # Create bar chart
        fig = px.bar(
            team_data,
            x='Weight Class',
            y='Points',
            color='Points',
            color_continuous_scale='YlGnBu',
            title=f"{team} - Points by Weight Class"
        )
        
        fig.update_layout(
            xaxis_title='Weight Class',
            yaxis_title='Points',
            height=350,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add summary statistics
        st.markdown("### Weight Class Summary")
        
        # Calculate summary statistics
        top_weight = team_data.loc[team_data['Points'].idxmax()]
        total_points = team_data['Points'].sum()
        weights_with_points = len(team_data[team_data['Points'] > 0])
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Top Weight Class", top_weight['Weight Class'])
        col2.metric("Total Points", total_points)
        col3.metric("Weight Classes with Points", weights_with_points)

def check_mobile_view():
    """Check if current view is likely on a mobile device."""
    # This is a simple estimation based on screen width
    try:
        # For now we'll use a simple check based on CSS media queries
        return False  # Default to desktop for server-side rendering
    except:
        return False