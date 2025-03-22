import streamlit as st
import os
import sys
import pandas as pd
import traceback

st.set_page_config(page_title="Debug NCAA Wrestling App", layout="wide")

st.title("NCAA Wrestling App Debugger")

st.write("This app helps debug issues with the NCAA Wrestling App deployment.")

st.subheader("1. System Information")
st.write(f"Python version: {sys.version}")
st.write(f"Current working directory: {os.getcwd()}")
st.write(f"Directory contents: {os.listdir()}")

st.subheader("2. Package Availability")
try:
    import ncaa_wrestling_tracker
    st.success("NCAA Wrestling Tracker package is available!")
    st.write(f"Package location: {ncaa_wrestling_tracker.__file__}")
    st.write(f"Package path: {ncaa_wrestling_tracker.__path__}")
except ImportError:
    st.error("NCAA Wrestling Tracker package is NOT available in this environment.")

st.subheader("3. Data Directory Structure")
try:
    data_dir = os.path.join(os.getcwd(), "Data")
    if os.path.exists(data_dir):
        st.success(f"Data directory exists: {data_dir}")
        st.write(f"Data directory contents: {os.listdir(data_dir)}")
        
        # Check for specific files
        results_file = os.path.join(data_dir, "wrestling_results.txt")
        draft_csv = os.path.join(data_dir, "ncaa_wrestling_draft.csv")
        
        if os.path.exists(results_file):
            st.success(f"Results file exists: {results_file}")
            # Show first few lines
            with open(results_file, 'r') as f:
                st.write("First 10 lines of results file:")
                st.code(''.join(f.readlines()[:10]))
        else:
            st.error(f"Results file NOT found: {results_file}")
            
        if os.path.exists(draft_csv):
            st.success(f"Draft CSV exists: {draft_csv}")
            # Show preview
            try:
                draft_df = pd.read_csv(draft_csv)
                st.write("Draft CSV preview:")
                st.dataframe(draft_df.head())
            except Exception as e:
                st.error(f"Error reading draft CSV: {e}")
        else:
            st.error(f"Draft CSV NOT found: {draft_csv}")
    else:
        st.error(f"Data directory NOT found: {data_dir}")
        
    # Check alternative locations
    app_dir = os.path.dirname(os.path.abspath(__file__))
    st.write(f"App directory: {app_dir}")
    
    potential_data_dirs = [
        os.path.join(app_dir, "Data"),
        os.path.join(os.path.dirname(app_dir), "Data"),
        "Data",
        "../Data"
    ]
    
    st.write("Checking potential data directories:")
    for potential_dir in potential_data_dirs:
        if os.path.exists(potential_dir):
            st.success(f"Potential data directory exists: {potential_dir}")
            st.write(f"Contents: {os.listdir(potential_dir)}")
        else:
            st.warning(f"Potential data directory NOT found: {potential_dir}")
            
except Exception as e:
    st.error(f"Error checking data directory: {e}")
    st.error(traceback.format_exc())

st.subheader("4. Config Testing")
try:
    from app_utils.app_config import setup_config_paths
    config = setup_config_paths()
    
    st.success("Successfully imported app_config and ran setup_config_paths()")
    
    # Display config attributes
    config_attrs = dir(config)
    important_attrs = [attr for attr in config_attrs if not attr.startswith('__')]
    
    st.write("Config attributes:")
    for attr in important_attrs:
        value = getattr(config, attr)
        if isinstance(value, str):
            exists = os.path.exists(value) if os.path.isabs(value) else "N/A"
            st.write(f"{attr}: {value} (Exists: {exists})")
        else:
            st.write(f"{attr}: {value}")
except Exception as e:
    st.error(f"Error importing or using app_config: {e}")
    st.error(traceback.format_exc())

st.subheader("5. Data Loading Test")
try:
    from app_utils.data_loader import fetch_tournament_data
    
    if st.button("Test Data Loading"):
        with st.spinner("Loading data..."):
            results_df, round_df, placements_df = fetch_tournament_data()
            
            if not results_df.empty:
                st.success(f"Successfully loaded results data: {len(results_df)} rows")
                st.write("Results DataFrame columns:", results_df.columns.tolist())
                st.write("Results DataFrame preview:")
                st.dataframe(results_df.head())
            else:
                st.error("Results DataFrame is empty")
                
            if not round_df.empty:
                st.success(f"Successfully loaded round data: {len(round_df)} rows")
            else:
                st.error("Round DataFrame is empty")
                
            if not placements_df.empty:
                st.success(f"Successfully loaded placements data: {len(placements_df)} rows")
            else:
                st.error("Placements DataFrame is empty")
except Exception as e:
    st.error(f"Error importing or using data_loader: {e}")
    st.error(traceback.format_exc())

st.markdown("---")
st.markdown("This debug app helps identify issues with your NCAA Wrestling App deployment.")