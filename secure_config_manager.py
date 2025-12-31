#!/usr/bin/env python3
"""
Secure Configuration Manager for Hughes Clues OSINT Toolkit
Handles environment variables, validation, and secure key management
"""

import os
import yaml
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration with secure defaults"""
    mongodb_uri: str = "mongodb://localhost:27017"
    redis_uri: str = "redis://localhost:6379"
    elasticsearch_uri: str = "http://localhost:9200"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""


@dataclass
class APIKeys:
    """External API keys loaded from environment"""
    shodan: Optional[str] = None
    censys_id: Optional[str] = None
    censys_secret: Optional[str] = None
    virustotal: Optional[str] = None
    securitytrails: Optional[str] = None
    urlscan: Optional[str] = None
    hibp: Optional[str] = None
    anthropic: Optional[str] = None
    openai: Optional[str] = None
    numverify: Optional[str] = None
    truecaller: Optional[str] = None


@dataclass
class AppConfig:
    """Application configuration"""
    debug: bool = False
    workers: int = 4
    timeout: int = 30
    cache_ttl: int = 3600
    max_retries: int = 3
    log_level: str = "INFO"
    output_dir: Path = field(default_factory=lambda: Path("output"))
    cache_dir: Path = field(default_factory=lambda: Path(".cache"))
    log_dir: Path = field(default_factory=lambda: Path("logs"))


class SecureConfigManager:
    """
    Centralized configuration manager with security best practices

    Features:
    - Environment variable loading with validation
    - API key format checking
    - No hardcoded secrets
    - Comprehensive logging
    - Type-safe configuration access
    """

    def __init__(self, config_file: Optional[Path] = None, env_file: Optional[Path] = None):
        """
        Initialize secure configuration manager

        Args:
            config_file: Path to YAML config file (default: config.yaml)
            env_file: Path to .env file (default: .env)
        """
        self.config_file = config_file or Path("config.yaml")
        self.env_file = env_file or Path(".env")

        # Load environment variables
        self._load_environment()

        # Initialize configurations
        self.database = DatabaseConfig()
        self.api_keys = APIKeys()
        self.app = AppConfig()

        # Load from YAML file
        self._load_yaml_config()

        # Override with environment variables
        self._load_api_keys()
        self._load_database_config()
        self._load_app_config()

        # Validate and create directories
        self._setup_directories()

        # Log configuration status
        self._log_config_status()

    def _load_environment(self):
        """Load environment variables from .env file"""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logger.info(f"✓ Loaded environment from {self.env_file}")
        else:
            logger.warning(f"⚠ .env file not found at {self.env_file}")
            logger.info("  Using system environment variables only")

    def _load_yaml_config(self):
        """Load base configuration from YAML file"""
        if not self.config_file.exists():
            logger.warning(f"⚠ Config file not found: {self.config_file}")
            logger.info("  Using default configuration")
            return

        try:
            with open(self.config_file) as f:
                config_data = yaml.safe_load(f) or {}

            # Load app settings from YAML
            if 'max_workers' in config_data:
                self.app.workers = config_data['max_workers']
            if 'cache_ttl' in config_data:
                self.app.cache_ttl = config_data['cache_ttl']

            # Load logging config
            if 'logging' in config_data:
                self.app.log_level = config_data['logging'].get('level', 'INFO')

            logger.info(f"✓ Loaded configuration from {self.config_file}")
        except yaml.YAMLError as e:
            logger.error(f"✗ Failed to parse config file: {e}")
        except Exception as e:
            logger.error(f"✗ Error loading config: {e}")

    def _load_api_keys(self):
        """Load API keys from environment variables with validation"""
        key_mapping = {
            'SHODAN_API_KEY': 'shodan',
            'CENSYS_ID': 'censys_id',
            'CENSYS_SECRET': 'censys_secret',
            'VIRUSTOTAL_API_KEY': 'virustotal',
            'SECURITYTRAILS_API_KEY': 'securitytrails',
            'URLSCAN_API_KEY': 'urlscan',
            'HIBP_API_KEY': 'hibp',
            'ANTHROPIC_API_KEY': 'anthropic',
            'OPENAI_API_KEY': 'openai',
            'NUMVERIFY_API_KEY': 'numverify',
            'TRUECALLER_API_KEY': 'truecaller',
        }

        for env_var, attr_name in key_mapping.items():
            key_value = os.getenv(env_var)

            if key_value and self._validate_api_key(env_var, key_value):
                setattr(self.api_keys, attr_name, key_value)
            elif key_value:
                logger.warning(f"⚠ Invalid format for {env_var}")

    def _validate_api_key(self, name: str, key: str) -> bool:
        """
        Validate API key format

        Args:
            name: API key name (for logging)
            key: API key value

        Returns:
            True if key format is valid
        """
        if not key or not isinstance(key, str):
            return False

        # Remove whitespace
        key = key.strip()

        # Basic validation: must be at least 16 characters
        if len(key) < 16:
            logger.warning(f"⚠ {name} too short (minimum 16 characters)")
            return False

        # Check for placeholder values
        placeholder_patterns = [
            'your_', 'YOUR_', 'xxx', 'XXX', 'test', 'TEST',
            'example', 'EXAMPLE', 'placeholder', 'PLACEHOLDER'
        ]

        if any(pattern in key for pattern in placeholder_patterns):
            logger.debug(f"  {name} appears to be a placeholder")
            return False

        return True

    def _load_database_config(self):
        """Load database configuration from environment"""
        self.database.mongodb_uri = os.getenv("MONGODB_URI", self.database.mongodb_uri)
        self.database.redis_uri = os.getenv("REDIS_URI", self.database.redis_uri)
        self.database.elasticsearch_uri = os.getenv("ELASTICSEARCH_URI", self.database.elasticsearch_uri)
        self.database.neo4j_uri = os.getenv("NEO4J_URI", self.database.neo4j_uri)
        self.database.neo4j_user = os.getenv("NEO4J_USER", self.database.neo4j_user)
        self.database.neo4j_password = os.getenv("NEO4J_PASSWORD", self.database.neo4j_password)

    def _load_app_config(self):
        """Load application configuration from environment"""
        self.app.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.app.log_level = os.getenv("LOG_LEVEL", self.app.log_level)

        # Workers
        workers_env = os.getenv("MAX_WORKERS")
        if workers_env and workers_env.isdigit():
            self.app.workers = int(workers_env)

        # Cache TTL
        cache_ttl_env = os.getenv("CACHE_TTL")
        if cache_ttl_env and cache_ttl_env.isdigit():
            self.app.cache_ttl = int(cache_ttl_env)

        # Directories
        output_dir = os.getenv("OUTPUT_DIR")
        if output_dir:
            self.app.output_dir = Path(output_dir)

        cache_dir = os.getenv("CACHE_DIR")
        if cache_dir:
            self.app.cache_dir = Path(cache_dir)

        log_dir = os.getenv("LOG_DIR")
        if log_dir:
            self.app.log_dir = Path(log_dir)

    def _setup_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.app.output_dir,
            self.app.cache_dir,
            self.app.log_dir,
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"✓ Directory ready: {directory}")
            except Exception as e:
                logger.error(f"✗ Failed to create directory {directory}: {e}")

    def _log_config_status(self):
        """Log configuration status (API keys loaded, etc.)"""
        logger.info("\n╔══════════════════════════════════════════════════════════╗")
        logger.info("║  Configuration Status                                    ║")
        logger.info("╚══════════════════════════════════════════════════════════╝")

        # Database connections
        logger.info(f"  MongoDB:       {self.database.mongodb_uri}")
        logger.info(f"  Redis:         {self.database.redis_uri}")
        logger.info(f"  Elasticsearch: {self.database.elasticsearch_uri}")
        logger.info(f"  Neo4j:         {self.database.neo4j_uri}")

        # API keys status
        logger.info("\n  API Keys Configured:")
        api_keys_status = {
            'Shodan': bool(self.api_keys.shodan),
            'Censys': bool(self.api_keys.censys_id and self.api_keys.censys_secret),
            'VirusTotal': bool(self.api_keys.virustotal),
            'SecurityTrails': bool(self.api_keys.securitytrails),
            'URLScan': bool(self.api_keys.urlscan),
            'HaveIBeenPwned': bool(self.api_keys.hibp),
            'Anthropic': bool(self.api_keys.anthropic),
            'OpenAI': bool(self.api_keys.openai),
        }

        for service, configured in api_keys_status.items():
            status = "✓ Configured" if configured else "✗ Not configured"
            logger.info(f"    {service:20s} {status}")

        # App settings
        logger.info(f"\n  Workers:       {self.app.workers}")
        logger.info(f"  Cache TTL:     {self.app.cache_ttl}s")
        logger.info(f"  Log Level:     {self.app.log_level}")
        logger.info(f"  Debug Mode:    {self.app.debug}")
        logger.info("╚══════════════════════════════════════════════════════════╝\n")

    def get_api_key(self, service: str) -> Optional[str]:
        """
        Get API key for a service

        Args:
            service: Service name (shodan, censys, virustotal, etc.)

        Returns:
            API key if configured, None otherwise
        """
        service_lower = service.lower().replace('_', '')
        key = getattr(self.api_keys, service_lower, None)

        if not key:
            logger.debug(f"API key for {service} not configured")

        return key

    def is_service_enabled(self, service: str) -> bool:
        """
        Check if a service is enabled (has API key)

        Args:
            service: Service name

        Returns:
            True if service has API key configured
        """
        return self.get_api_key(service) is not None

    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary (without secrets)

        Returns:
            Configuration dictionary with API keys masked
        """
        return {
            'database': {
                'mongodb_uri': self._mask_uri(self.database.mongodb_uri),
                'redis_uri': self._mask_uri(self.database.redis_uri),
                'elasticsearch_uri': self.database.elasticsearch_uri,
                'neo4j_uri': self._mask_uri(self.database.neo4j_uri),
            },
            'api_keys': {
                'shodan': '***' if self.api_keys.shodan else None,
                'censys': '***' if self.api_keys.censys_id else None,
                'virustotal': '***' if self.api_keys.virustotal else None,
                'securitytrails': '***' if self.api_keys.securitytrails else None,
                'urlscan': '***' if self.api_keys.urlscan else None,
                'hibp': '***' if self.api_keys.hibp else None,
                'anthropic': '***' if self.api_keys.anthropic else None,
                'openai': '***' if self.api_keys.openai else None,
            },
            'app': {
                'debug': self.app.debug,
                'workers': self.app.workers,
                'cache_ttl': self.app.cache_ttl,
                'log_level': self.app.log_level,
                'output_dir': str(self.app.output_dir),
                'cache_dir': str(self.app.cache_dir),
                'log_dir': str(self.app.log_dir),
            }
        }

    @staticmethod
    def _mask_uri(uri: str) -> str:
        """Mask passwords in URI strings"""
        if '@' in uri and '://' in uri:
            # URI format: scheme://user:password@host:port/database
            parts = uri.split('@')
            if ':' in parts[0]:
                prefix = parts[0].rsplit(':', 1)[0]
                return f"{prefix}:***@{parts[1]}"
        return uri


# Global configuration instance
_config_instance: Optional[SecureConfigManager] = None

def get_config() -> SecureConfigManager:
    """
    Get global configuration instance (singleton)

    Returns:
        SecureConfigManager instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = SecureConfigManager()
    return _config_instance


if __name__ == '__main__':
    # Test configuration loading
    print("Testing Secure Configuration Manager\n")

    config = SecureConfigManager()

    print("\n Configuration Dictionary:")
    import json
    print(json.dumps(config.to_dict(), indent=2))

    print("\n✓ Configuration manager tested successfully!")
