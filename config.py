import os
import yaml
from rich.theme import Theme

# Path to the configuration file
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.yaml")

# Default configuration values
DEFAULT_CONFIG = {
    "openai": {
        "model": "qwen2.5-7b-instruct-1m",
        "temperature": 0.7,
        "api_key": "lm-studio",
        "base_url": "http://10.16.17.42:1234/v1",
        "max_tokens": 4000,
        "timeout": 60
    },
    "paths": {
        "default_output_dir": "output",
        "temp_dir": "temp",
        "log_dir": "logs"
    },
    "processing": {
        "srt2txt": {
            "extract_text_only": True,
            "remove_timestamps": True,
            "combine_sentences": True
        },
        "txt2md": {
            "include_timestamps": False,
            "include_summary": True,
            "include_key_points": True
        },
        "md2docx": {
            "add_table_of_contents": True,
            "add_page_numbers": True,
            "template_file": ""
        }
    },
    "logging": {
        "level": "info",
        "log_to_file": True,
        "log_to_console": True
    },
    "ui": {
        "color_theme": "default",
        "show_progress_bars": True,
        "show_spinners": True
    }
}

# Load configuration from file
def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
                user_config = yaml.safe_load(config_file)
                # Merge with default config
                return merge_config(DEFAULT_CONFIG, user_config)
        else:
            print(f"Warning: Configuration file not found at {CONFIG_FILE}. Using default configuration.")
            return DEFAULT_CONFIG
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG

# Helper function to recursively merge dictionaries
def merge_config(default, user):
    if not user:
        return default
    
    result = default.copy()
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value
    return result

# Load the configuration once at import time
config = load_config()

# Extract commonly used configuration sections
openai_config = config.get("openai", {})
paths_config = config.get("paths", {})
processing_config = config.get("processing", {})
logging_config = config.get("logging", {})
ui_config = config.get("ui", {})

# Setup UI theme based on configuration
def get_ui_theme():
    theme_name = ui_config.get("color_theme", "default")
    
    if theme_name == "dark":
        return Theme({
            "info": "dark_cyan",
            "warning": "yellow",
            "error": "bold red",
            "success": "bold green",
            "highlight": "dark_magenta",
        })
    elif theme_name == "light":
        return Theme({
            "info": "blue",
            "warning": "orange3",
            "error": "red",
            "success": "green",
            "highlight": "purple",
        })
    elif theme_name == "monochrome":
        return Theme({
            "info": "white",
            "warning": "white",
            "error": "bold white",
            "success": "bold white",
            "highlight": "white",
        })
    else:  # default theme
        return Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "bold red",
            "success": "bold green",
            "highlight": "magenta",
        })

# Convenience function to get specific configuration sections
def get_config(section=None, subsection=None, key=None, default=None):
    try:
        if section is None:
            return config
        if section not in config:
            return default
        
        section_config = config[section]
        
        if subsection is None:
            return section_config
        if subsection not in section_config:
            return default
        
        subsection_config = section_config[subsection]
        
        if key is None:
            return subsection_config
        if key not in subsection_config:
            return default
        
        return subsection_config[key]
    except:
        return default

# Function to save configuration changes back to the file
def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
            yaml.safe_dump(config, config_file, default_flow_style=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# Function to update a specific configuration value
def update_config(section, subsection=None, key=None, value=None):
    try:
        if section not in config:
            config[section] = {}
        
        if subsection is not None:
            if subsection not in config[section]:
                config[section][subsection] = {}
            
            if key is not None:
                config[section][subsection][key] = value
        elif key is not None:
            config[section][key] = value
        
        return save_config()
    except Exception as e:
        print(f"Error updating config: {e}")
        return False