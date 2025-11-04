"""
Configuration Validation Module
Validates all configuration settings before runtime
"""

import logging
from pathlib import Path
from typing import Tuple, List
import yaml

logger = logging.getLogger(__name__)


class ConfigValidator:
    """Validate configuration before runtime"""

    @staticmethod
    def validate(config: dict) -> Tuple[List[str], List[str]]:
        """
        Validate configuration settings

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Validate database configuration
        mongodb_uri = config.get('mongodb_uri', 'mongodb://localhost:27017')
        if not mongodb_uri:
            errors.append("mongodb_uri is not configured")
        else:
            logger.info(f"[+] MongoDB URI: {mongodb_uri}")

        # Validate Redis configuration
        redis_url = config.get('redis_url', 'redis://localhost:6379')
        if not redis_url:
            errors.append("redis_url is not configured")
        else:
            logger.info(f"[+] Redis URL: {redis_url}")

        # Validate required directories
        directories = {
            'output_dir': config.get('output_dir', 'output'),
            'cache_dir': config.get('cache_dir', '.cache'),
            'log_dir': config.get('log_dir', 'logs'),
        }

        for dir_key, dir_path in directories.items():
            if dir_path:
                dir_obj = Path(dir_path)
                try:
                    dir_obj.mkdir(parents=True, exist_ok=True)
                    logger.info(f"[+] {dir_key}: {dir_path}")
                except Exception as e:
                    errors.append(f"Cannot create {dir_key} ({dir_path}): {str(e)}")
            else:
                warnings.append(f"{dir_key} not configured, using default: {dir_path}")

        # Validate API keys (warn if missing, don't error)
        api_keys = config.get('api_keys', {})
        critical_keys = {
            'shodan_key': 'Shodan intelligence disabled',
            'censys_id': 'Censys integration disabled',
            'hibp_key': 'HaveIBeenPwned integration disabled',
        }

        for key, reason in critical_keys.items():
            if not api_keys.get(key):
                warnings.append(f"API key '{key}' not configured - {reason}")

        # Validate optional integrations
        optional_keys = ['openai_key', 'anthropic_key', 'github_token']
        for key in optional_keys:
            if not api_keys.get(key):
                logger.debug(f"Optional API key not configured: {key}")

        # Validate worker configuration
        workers = config.get('workers', 4)
        if not isinstance(workers, int) or workers < 1:
            errors.append(f"workers must be a positive integer, got: {workers}")
        else:
            logger.info(f"[+] Workers: {workers}")

        # Validate timeouts
        timeouts = config.get('timeouts', {})
        if isinstance(timeouts, dict):
            for timeout_key, timeout_val in timeouts.items():
                if not isinstance(timeout_val, (int, float)) or timeout_val <= 0:
                    errors.append(f"Timeout '{timeout_key}' must be positive number, got: {timeout_val}")
        else:
            warnings.append("Timeouts configuration invalid, using defaults")

        return errors, warnings

    @staticmethod
    def validate_on_startup(config: dict) -> bool:
        """
        Validate and report on startup

        Returns:
            True if validation passes, False otherwise
        """
        logger.info("[*] Validating configuration...")

        errors, warnings = ConfigValidator.validate(config)

        # Report errors
        if errors:
            logger.error("[!] Configuration errors found:")
            for error in errors:
                logger.error(f"    ✗ {error}")
            return False

        # Report warnings
        if warnings:
            logger.warning("[!] Configuration warnings:")
            for warning in warnings:
                logger.warning(f"    ⚠ {warning}")
        else:
            logger.info("[+] No configuration warnings")

        logger.info("[+] Configuration validation passed ✓")
        return True

    @staticmethod
    def load_and_validate(config_file: str) -> Tuple[dict, bool]:
        """
        Load configuration file and validate it

        Args:
            config_file: Path to config.yaml file

        Returns:
            Tuple of (config_dict, validation_passed)
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.error(f"[!] Config file not found: {config_file}")
                return {}, False

            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}

            validation_passed = ConfigValidator.validate_on_startup(config)
            return config, validation_passed

        except Exception as e:
            logger.error(f"[!] Failed to load configuration: {str(e)}")
            return {}, False
