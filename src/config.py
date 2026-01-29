"""
Module for configuration management.
Handles reading configuration files and managing settings.
"""

import configparser
import os
from typing import Any, Optional, Dict


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: str = "config.ini"):
        """
        Initialize configuration manager.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                self.config.read(self.config_file)
            else:
                self._create_default_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration."""
        self.config['API_KEYS'] = {
            'TWITTER_BEARER_TOKEN': 'YOUR_TWITTER_BEARER_TOKEN',
            'GEMINI_API_KEY': 'YOUR_GEMINI_API_KEY'
        }
        
        self.config['APP_SETTINGS'] = {
            'DEFAULT_HASHTAG': '#business',
            'POST_LIMIT': '10',
            'SENTIMENT_THRESHOLD': '0.3',
            'TIMEZONE': 'UTC',
            'ANALYSIS_DEPTH': 'standard'
        }
        
        self.config['FILE_SETTINGS'] = {
            'DATA_DIR': 'data',
            'LOG_RETENTION_DAYS': '30',
            'EXPORT_FORMAT': 'csv'
        }
        
        # Save default config
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, key: str, section: str = None, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key (str): Configuration key
            section (str): Optional section name
            default (Any): Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        try:
            if section:
                return self.config.get(section, key, fallback=default)
            else:
                for sec in self.config.sections():
                    if key in self.config[sec]:
                        return self.config[sec][key]
                return default
        except Exception:
            return default
    
    def set(self, key: str, value: Any, section: str = 'APP_SETTINGS'):
        """
        Set configuration value.
        
        Args:
            key (str): Configuration key
            value (Any): Value to set
            section (str): Section name
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section][key] = str(value)
        
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a specific service.
        
        Args:
            service (str): Service name (twitter, gemini)
            
        Returns:
            Optional[str]: API key or None
        """
        key_map = {
            'twitter': 'TWITTER_BEARER_TOKEN',
            'gemini': 'GEMINI_API_KEY'
        }
        
        if service.lower() in key_map:
            key = self.get(key_map[service.lower()], 'API_KEYS')
            if key and key != f'YOUR_{key_map[service.lower()]}':
                return key
        
        return None
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate configuration and return status."""
        validation = {
            'config_file_exists': os.path.exists(self.config_file),
            'twitter_api_configured': self.get_api_key('twitter') is not None,
            'gemini_api_configured': self.get_api_key('gemini') is not None,
            'data_dir_exists': os.path.exists(self.get('DATA_DIR', 'FILE_SETTINGS', 'data'))
        }
        
        return validation
