import os
import sys
from ncaa_wrestling_tracker import config

def setup_config_paths():
    """
    Set up configuration paths for the application.
    Integrates with the existing ncaa_wrestling_tracker package config.
    """
    # Update config paths if needed
    # This uses the config from your existing package
    
    # Ensure the output directory exists
    if hasattr(config, 'OUTPUT_DIR') and config.OUTPUT_DIR:
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    
    # Return config for convenience
    return config

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

def get_app_path():
    """Returns the absolute path to the app directory."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_asset_path(filename):
    """Returns the path to an asset file."""
    return os.path.join(get_app_path(), 'app_assets', filename)