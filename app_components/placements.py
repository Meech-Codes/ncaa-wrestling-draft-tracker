import streamlit as st
import pandas as pd
import plotly.express as px

def render_placements():
    """
    Render the Placements tab with responsive layout.
    Shows tournament placements by weight class.
    """
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
        
        # Sort by placement and weight class
        if 'placement' in filtered_df.columns:
            filtered_df = filtered_df.sort_values(['weight', 'placement'])
        
        # Display the dataframe
        st.markdown("### Tournament Placements")
        st.markdown("Scroll horizontally if needed on mobile devices")
        
        # Format the dataframe for display
        display_df = format_placements_table(filtered_df)
        
        # Display the formatted table
        st.dataframe(display_df, use_container_width=True)
        
        # Add visualizations
        display_placement_visualizations(filtered_df)
        
    else:
        st.info("No placement data available. Please update results.")

def format_placements_table(df):
    """Format placements dataframe for better display."""
    # Rename columns for better display
    display_cols = ['weight', 'seed', 'Wrestler', 'owner', 'placement', 'placement_points']
    
    # Filter to columns that exist
    display_cols = [col for col in display_cols if col in df.columns]
    
    # Create a copy of the dataframe with selected columns
    display_df = df[display_cols].copy()
    
    # Rename columns
    column_renames = {
        'weight': 'Weight',
        'seed': 'Seed',
        'Wrestler': 'Wrestler',
        'owner': 'Team',
        'placement': 'Place',
        'placement_points': 'Points'
    }
    
    # Rename only columns that exist
    rename_dict = {col: column_renames[col] for col in display_cols if col in column_renames}
    display_df = display_df.rename(columns=rename_dict)
    
    return display_df

def display_placement_visualizations(df):
    """Display visualizations related to placements."""
    # Only display visualizations if we have enough data
    if len(df) < 3:
        return
    
    st.subheader("Placement Visualizations")
    
    # Check if mobile view
    is_mobile = check_mobile_view()
    
    # First visualization: Team placement distribution
    try:
        # Create a count of placements by team
        team_placements = df.groupby('owner')['placement'].count().reset_index()
        team_placements.columns = ['Team', 'Placements']
        
        # Sort by placement count (descending)
        team_placements = team_placements.sort_values('Placements', ascending=False)
        
        # Create the chart
        fig = px.bar(
            team_placements,
            x='Team',
            y='Placements',
            color='Placements',
            color_continuous_scale='Viridis',
            text='Placements',
            title='Number of Placements by Team'
        )
        
        # Update layout for responsiveness
        fig.update_layout(
            xaxis_title='Team',
            yaxis_title='Number of Placements',
            height=350 if not is_mobile else 300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        pass  # Silently fail if visualization cannot be created
    
    # Second visualization: Placement points by weight class
    try:
        if 'weight' in df.columns and 'placement_points' in df.columns:
            # Create a sum of placement points by weight class
            weight_points = df.groupby('weight')['placement_points'].sum().reset_index()
            weight_points.columns = ['Weight Class', 'Placement Points']
            
            # Sort by weight class (numerically)
            weight_points = weight_points.sort_values('Weight Class')
            
            # Create the chart
            fig = px.bar(
                weight_points,
                x='Weight Class',
                y='Placement Points',
                color='Placement Points',
                color_continuous_scale='Viridis',
                text='Placement Points',
                title='Placement Points by Weight Class'
            )
            
            # Update layout for responsiveness
            fig.update_layout(
                xaxis_title='Weight Class',
                yaxis_title='Placement Points',
                height=350 if not is_mobile else 300,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        pass  # Silently fail if visualization cannot be created

def check_mobile_view():
    """Check if current view is likely on a mobile device."""
    # This is a simple estimation
    try:
        # For now we'll use a simple check based on CSS media queries
        return False  # Default to desktop for server-side rendering
    except:
        return False