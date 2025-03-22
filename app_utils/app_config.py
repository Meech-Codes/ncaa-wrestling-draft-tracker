import os
import sys
import streamlit as st
from pathlib import Path

# Try to import your existing config
try:
    from ncaa_wrestling_tracker import config
    PACKAGE_AVAILABLE = True
except ImportError:
    PACKAGE_AVAILABLE = False

def setup_config_paths():
    """
    Set up configuration paths for the application.
    Handles both local and cloud deployment scenarios.
    """
    # If package is available, use its config
    if PACKAGE_AVAILABLE:
        # Just ensure the output directory exists
        if hasattr(config, 'OUTPUT_DIR') and config.OUTPUT_DIR:
            os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        return config
    
    # If package is not available, create a fallback config
    # that points to the GitHub repository structure
    class FallbackConfig:
        def __init__(self):
            # Base path is the repo root
            self.PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Data paths relative to repo root
            self.DATA_PATH = os.path.join(self.PROJECT_ROOT, "Data")
            self.RESULTS_FILE = os.path.join(self.DATA_PATH, "wrestling_results.txt")
            self.DRAFT_CSV = os.path.join(self.DATA_PATH, "ncaa_wrestling_draft.csv")
            
            # Output directory for results
            self.RESULTS_BASE = os.path.join(self.PROJECT_ROOT, "Results")
            self.OUTPUT_DIR = self.RESULTS_BASE
            
            # Ensure directories exist
            os.makedirs(self.DATA_PATH, exist_ok=True)
            os.makedirs(self.OUTPUT_DIR, exist_ok=True)
    
    return FallbackConfig()

# Additional configuration settings specific to the app
APP_CONFIG = {
    "version": "1.0.0",
    "cache_timeout": 3600,  # Cache timeout in seconds (1 hour)
    "weight_classes": ['125', '133', '141', '149', '157', '165', '174', '184', '197', '285', 'DH'],
    "mobile_breakpoint": 768,  # Pixel width to consider as mobile device
    "colors": {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "tertiary": "#2ca02c",
        "win": "#c6efce",
        "loss": "#ffc7ce",
        "win_text": "#006100",
        "loss_text": "#9c0006"
    }
}