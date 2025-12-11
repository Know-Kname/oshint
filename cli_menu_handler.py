#!/usr/bin/env python3
"""
Enhanced CLI Menu Handler - Connects all menu options to their implementations
Improves UX/UI with better error handling, validation, and user feedback
"""

import asyncio
import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedCLIHandler:
    """Enhanced CLI menu handler with complete implementations"""

    def __init__(self, cli_instance):
        """
        Initialize enhanced handler

        Args:
            cli_instance: HughesCLI instance
        """
        self.cli = cli_instance
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            if os.path.exists(self.cli.config_file):
                with open(self.cli.config_file) as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            return {}

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.cli.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            self.cli.show_status("Configuration saved successfully", "success")
        except Exception as e:
            self.cli.show_status(f"Error saving config: {str(e)}", "error")

    # ==================== MAIN MENU HANDLERS ====================

    async def handle_reconnaissance(self):
        """Handle reconnaissance menu option [1]"""
        target = self.cli.get_target()
        if not target:
            return

        choice = self.cli.show_recon_menu()

        if choice == "0":
            return
        elif choice == "9":
            # Full reconnaissance
            await self.cli.execute_recon(target)
        else:
            # Specific recon modules
            self.cli.show_status(f"Executing reconnaissance module {choice} for {target}", "info")
            await self.cli.execute_recon(target)

    async def handle_credential_harvest(self):
        """Handle credential harvesting menu option [2]"""
        self.cli.show_status("⚠ WARNING: Credential harvesting requires authorization", "warning")

        if HAS_RICH:
            authorized = Confirm.ask("Do you have authorization to test credentials?")
        else:
            authorized = input("Do you have authorization? (yes/no): ").strip().lower() == 'yes'

        if not authorized:
            self.cli.show_status("Operation cancelled - authorization required", "warning")
            return

        target = self.cli.get_target()
        if not target:
            return

        choice = self.cli.show_cred_harvest_menu()

        if choice == "0":
            return
        elif choice == "7":
            # Full credential harvest
            await self.cli.execute_credential_harvest(target)
        else:
            self.cli.show_status(f"Executing credential module {choice} for {target}", "info")
            await self.cli.execute_credential_harvest(target)

    async def handle_dark_web_monitor(self):
        """Handle dark web monitoring menu option [3]"""
        self.cli.show_status("Dark Web Monitoring Module", "info")

        target = self.cli.get_target()
        if not target:
            return

        try:
            from elite_darkweb_monitor import EliteDarkWebMonitor

            self.cli.show_status(f"Starting dark web monitoring for {target}", "info")
            self.cli.show_status("⚠ Connecting to Tor network...", "warning")

            monitor = EliteDarkWebMonitor(self.config.get('api_keys', {}))
            await monitor.initialize()

            results = await monitor.monitor_target(target)

            self.cli.show_status("Dark web monitoring complete", "success")
            self.cli.show_status(f"Found {len(results.get('mentions', []))} mentions", "info")

            await monitor.cleanup()

        except Exception as e:
            self.cli.show_status(f"Error: {str(e)}", "error")

    async def handle_web_scraping(self):
        """Handle web scraping menu option [4]"""
        target = self.cli.get_target()
        if not target:
            return

        try:
            from elite_web_scraper import EliteWebScraper

            self.cli.show_status(f"Starting web scraping for {target}", "info")

            scraper = EliteWebScraper()
            results = await scraper.scrape_target(target)

            self.cli.show_status("Web scraping complete", "success")
            self.cli.show_status(f"Scraped {len(results.get('pages', []))} pages", "info")

        except Exception as e:
            self.cli.show_status(f"Error: {str(e)}", "error")

    async def handle_geolocation(self):
        """Handle geolocation intelligence menu option [5]"""
        target = self.cli.get_target()
        if not target:
            return

        try:
            from elite_geolocation_intel import EliteGeolocationIntel

            self.cli.show_status(f"Starting geolocation analysis for {target}", "info")

            geo = EliteGeolocationIntel(self.config.get('api_keys', {}))
            results = await geo.full_geolocation_analysis(target)

            self.cli.show_status("Geolocation analysis complete", "success")

            # Display results
            if results.get('location'):
                loc = results['location']
                self.cli.show_status(f"Location: {loc.get('city', 'Unknown')}, {loc.get('country', 'Unknown')}", "info")
            if results.get('asn'):
                self.cli.show_status(f"ASN: {results['asn']}", "info")

        except Exception as e:
            self.cli.show_status(f"Error: {str(e)}", "error")

    async def handle_analysis(self):
        """Handle analysis engine menu option [6]"""
        try:
            from elite_analysis_engine import AdvancedAnalyzer

            self.cli.show_status("Analysis Engine", "info")

            if not self.cli.results:
                self.cli.show_status("No results to analyze. Run reconnaissance first.", "warning")
                return

            analyzer = AdvancedAnalyzer()

            # Analyze all stored results
            data = list(self.cli.results.values())

            self.cli.show_status("Analyzing patterns...", "info")
            patterns = analyzer.analyze_patterns(data)

            self.cli.show_status("Detecting anomalies...", "info")
            anomalies, scores = analyzer.detect_anomalies(data)

            self.cli.show_status("Analysis complete", "success")
            self.cli.show_status(f"Found {len(patterns)} patterns", "info")
            self.cli.show_status(f"Detected {len(anomalies)} anomalies", "info")

        except Exception as e:
            self.cli.show_status(f"Error: {str(e)}", "error")

    async def handle_people_intelligence(self):
        """Handle people intelligence menu option [7] - NEW"""
        self.cli.show_status("👤 People Intelligence (PEOPLEINT)", "info")
        self.cli.show_status("⚠ AUTHORIZATION REQUIRED - Legal use only", "warning")

        if HAS_RICH:
            authorized = Confirm.ask("Do you have authorization for people intelligence gathering?")
        else:
            authorized = input("Authorized use? (yes/no): ").strip().lower() == 'yes'

        if not authorized:
            self.cli.show_status("Operation cancelled - authorization required", "warning")
            return

        # Show search method menu
        if HAS_RICH:
            console.print("\n[cyan]Select Search Method[/cyan]")
            console.print("[1] Search by Name")
            console.print("[2] Search by Phone Number")
            console.print("[3] Search by Email")
            console.print("[4] Search by Username")
            console.print("[5] Comprehensive Search (All Methods)")
            console.print("[0] Back")
            choice = Prompt.ask("Select method", choices=["0", "1", "2", "3", "4", "5"])
        else:
            print("\n=== Select Search Method ===")
            print("[1] Search by Name")
            print("[2] Search by Phone Number")
            print("[3] Search by Email")
            print("[4] Search by Username")
            print("[5] Comprehensive Search")
            print("[0] Back")
            choice = input("Select (0-5): ").strip()

        if choice == "0":
            return

        try:
            from elite_people_intel import PeopleIntelligence

            intel = PeopleIntelligence(self.config)

            if choice == "1":
                # Search by name
                if HAS_RICH:
                    name = Prompt.ask("Enter full name")
                    city = Prompt.ask("Enter city (optional)", default="")
                    state = Prompt.ask("Enter state (optional)", default="")
                else:
                    name = input("Enter full name: ").strip()
                    city = input("Enter city (optional): ").strip()
                    state = input("Enter state (optional): ").strip()

                self.cli.show_status(f"Searching for: {name}", "info")
                profile = await intel.search_by_name(name, city or None, state or None)

            elif choice == "2":
                # Search by phone
                if HAS_RICH:
                    phone = Prompt.ask("Enter phone number")
                else:
                    phone = input("Enter phone number: ").strip()

                self.cli.show_status(f"Searching phone: {phone}", "info")
                profile = await intel.search_by_phone(phone)

            elif choice == "3":
                # Search by email
                if HAS_RICH:
                    email = Prompt.ask("Enter email address")
                else:
                    email = input("Enter email address: ").strip()

                self.cli.show_status(f"Searching email: {email}", "info")
                profile = await intel.search_by_email(email)

            elif choice == "4":
                # Search by username
                if HAS_RICH:
                    username = Prompt.ask("Enter username")
                else:
                    username = input("Enter username: ").strip()

                self.cli.show_status(f"Searching username: {username}", "info")
                profile = await intel.search_by_username(username)

            elif choice == "5":
                # Comprehensive search
                if HAS_RICH:
                    name = Prompt.ask("Enter full name (optional)", default="")
                    phone = Prompt.ask("Enter phone (optional)", default="")
                    email = Prompt.ask("Enter email (optional)", default="")
                    username = Prompt.ask("Enter username (optional)", default="")
                    city = Prompt.ask("Enter city (optional)", default="")
                    state = Prompt.ask("Enter state (optional)", default="")
                else:
                    name = input("Enter full name (optional): ").strip()
                    phone = input("Enter phone (optional): ").strip()
                    email = input("Enter email (optional): ").strip()
                    username = input("Enter username (optional): ").strip()
                    city = input("Enter city (optional): ").strip()
                    state = input("Enter state (optional): ").strip()

                self.cli.show_status("Running comprehensive search...", "info")
                profile = await intel.search_comprehensive(
                    name=name or None,
                    phone=phone or None,
                    email=email or None,
                    username=username or None,
                    city=city or None,
                    state=state or None
                )

            await intel.close_session()

            # Display results
            self.cli.show_status("Search complete", "success")
            self.cli.show_status(f"Confidence Score: {profile.confidence_score:.1f}/100", "info")

            # Generate and display report
            report = intel.generate_report(profile, format='text')
            if HAS_RICH:
                console.print(Panel(report, title="People Intelligence Report", border_style="green"))
            else:
                print("\n" + report)

            # Ask to export
            if HAS_RICH:
                export = Confirm.ask("Export results to JSON?")
            else:
                export = input("Export to JSON? (yes/no): ").strip().lower() == 'yes'

            if export:
                from datetime import datetime
                filename = f"person_{profile.full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w') as f:
                    f.write(intel.generate_report(profile, format='json'))
                self.cli.show_status(f"Exported to: {filename}", "success")

        except Exception as e:
            self.cli.show_status(f"Error: {str(e)}", "error")

    async def handle_full_pipeline(self):
        """Handle full intelligence pipeline menu option [8]"""
        target = self.cli.get_target()
        if not target:
            return

        self.cli.show_status(f"⚡ Running FULL intelligence pipeline for {target}", "info")
        self.cli.show_status("This will execute all intelligence gathering modules", "warning")

        if HAS_RICH:
            confirm = Confirm.ask("Continue with full pipeline?")
        else:
            confirm = input("Continue? (yes/no): ").strip().lower() == 'yes'

        if not confirm:
            return

        await self.cli.execute_orchestrator(target, operations=None)

    def handle_view_results(self):
        """Handle view results menu option [9]"""
        choice = self.cli.show_results_menu()

        if choice == "0":
            return
        elif choice == "1":
            # View latest report
            if not self.cli.results:
                self.cli.show_status("No results available", "warning")
                return

            latest_target = list(self.cli.results.keys())[-1]
            latest_result = self.cli.results[latest_target]

            if HAS_RICH:
                console.print(Panel(f"Latest Result: {latest_target}", border_style="cyan"))
            else:
                print(f"\n=== Latest Result: {latest_target} ===")

            self.cli.display_intelligence_report(latest_result)

        elif choice == "2":
            # View by target
            if not self.cli.results:
                self.cli.show_status("No results available", "warning")
                return

            if HAS_RICH:
                console.print("[cyan]Available Targets:[/cyan]")
                for idx, target in enumerate(self.cli.results.keys(), 1):
                    console.print(f"[{idx}] {target}")
                target_choice = Prompt.ask("Select target number")
            else:
                print("\nAvailable Targets:")
                for idx, target in enumerate(self.cli.results.keys(), 1):
                    print(f"[{idx}] {target}")
                target_choice = input("Select target number: ").strip()

            try:
                target_idx = int(target_choice) - 1
                target = list(self.cli.results.keys())[target_idx]
                self.cli.display_intelligence_report(self.cli.results[target])
            except (ValueError, IndexError):
                self.cli.show_status("Invalid target selection", "error")

        elif choice == "3":
            # Export results
            self._export_results()

        elif choice == "4":
            # View history
            self._view_history()

        elif choice == "5":
            # Clear results
            if HAS_RICH:
                confirm = Confirm.ask("Clear all results?")
            else:
                confirm = input("Clear all results? (yes/no): ").strip().lower() == 'yes'

            if confirm:
                self.cli.results.clear()
                self.cli.history.clear()
                self.cli.show_status("Results cleared", "success")

    def handle_settings(self):
        """Handle settings menu option [10]"""
        choice = self.cli.show_settings_menu()

        if choice == "0":
            return
        elif choice == "1":
            # Show config file location
            self.cli.show_status(f"Config file: {self.cli.config_file}", "info")
        elif choice == "2":
            # View configuration
            self._view_config()
        elif choice == "3":
            # Set custom config
            self._set_custom_config()
        elif choice == "4":
            # API key management
            self._manage_api_keys()
        elif choice == "5":
            # Test database connection
            asyncio.run(self._test_database_connection())

    # ==================== HELPER METHODS ====================

    def _export_results(self):
        """Export results to file"""
        import json
        from datetime import datetime

        if not self.cli.results:
            self.cli.show_status("No results to export", "warning")
            return

        filename = f"hughes_clues_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, 'w') as f:
                json.dump({
                    'results': {k: str(v) for k, v in self.cli.results.items()},
                    'history': self.cli.history
                }, f, indent=2, default=str)

            self.cli.show_status(f"Results exported to: {filename}", "success")
        except Exception as e:
            self.cli.show_status(f"Export failed: {str(e)}", "error")

    def _view_history(self):
        """View operation history"""
        if not self.cli.history:
            self.cli.show_status("No operation history", "warning")
            return

        headers = ["Target", "Timestamp", "Risk Score"]
        rows = [
            [h['target'], h['timestamp'], str(h.get('risk_score', 'N/A'))]
            for h in self.cli.history
        ]

        self.cli.display_table("Operation History", headers, rows)

    def _view_config(self):
        """View current configuration"""
        if HAS_RICH:
            console.print(Panel(yaml.dump(self.config, default_flow_style=False), title="Configuration", border_style="cyan"))
        else:
            print("\n=== Configuration ===")
            print(yaml.dump(self.config, default_flow_style=False))

    def _set_custom_config(self):
        """Set custom configuration file"""
        if HAS_RICH:
            new_path = Prompt.ask("Enter config file path")
        else:
            new_path = input("Enter config file path: ").strip()

        if os.path.exists(new_path):
            self.cli.config_file = new_path
            self.config = self._load_config()
            self.cli.show_status(f"Config file updated to: {new_path}", "success")
        else:
            self.cli.show_status("File not found", "error")

    def _manage_api_keys(self):
        """Manage API keys"""
        if HAS_RICH:
            console.print("\n[cyan]API Key Management[/cyan]")
            console.print("[1] View API Keys (masked)")
            console.print("[2] Add/Update API Key")
            console.print("[3] Remove API Key")
            console.print("[4] Validate API Keys")
            console.print("[0] Back")
            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4"])
        else:
            print("\n=== API Key Management ===")
            print("[1] View API Keys (masked)")
            print("[2] Add/Update API Key")
            print("[3] Remove API Key")
            print("[4] Validate API Keys")
            print("[0] Back")
            choice = input("Select (0-4): ").strip()

        if choice == "0":
            return
        elif choice == "1":
            self._view_api_keys()
        elif choice == "2":
            self._add_api_key()
        elif choice == "3":
            self._remove_api_key()
        elif choice == "4":
            self._validate_api_keys()

    def _view_api_keys(self):
        """View API keys (masked)"""
        api_keys = self.config.get('api_keys', {})

        if not api_keys:
            self.cli.show_status("No API keys configured", "warning")
            return

        headers = ["Service", "Status"]
        rows = []

        for service, key in api_keys.items():
            if key:
                masked = key[:4] + "*" * (len(key) - 8) + key[-4:] if len(key) > 8 else "***"
                rows.append([service, f"✓ {masked}"])
            else:
                rows.append([service, "✗ Not configured"])

        self.cli.display_table("API Keys", headers, rows)

    def _add_api_key(self):
        """Add or update API key"""
        services = [
            "shodan_key", "censys_id", "censys_secret", "virustotal_key",
            "securitytrails_key", "urlscan_key", "hibp_key", "numverify_key",
            "truecaller_key", "pipl_key", "clearbit_key"
        ]

        if HAS_RICH:
            console.print("[cyan]Available Services:[/cyan]")
            for idx, service in enumerate(services, 1):
                console.print(f"[{idx}] {service}")
            service_choice = Prompt.ask("Select service number")
        else:
            print("\nAvailable Services:")
            for idx, service in enumerate(services, 1):
                print(f"[{idx}] {service}")
            service_choice = input("Select service number: ").strip()

        try:
            service_idx = int(service_choice) - 1
            service = services[service_idx]

            if HAS_RICH:
                api_key = Prompt.ask(f"Enter API key for {service}")
            else:
                api_key = input(f"Enter API key for {service}: ").strip()

            if 'api_keys' not in self.config:
                self.config['api_keys'] = {}

            self.config['api_keys'][service] = api_key
            self._save_config()

            self.cli.show_status(f"API key for {service} updated", "success")

        except (ValueError, IndexError):
            self.cli.show_status("Invalid selection", "error")

    def _remove_api_key(self):
        """Remove API key"""
        api_keys = self.config.get('api_keys', {})

        if not api_keys:
            self.cli.show_status("No API keys to remove", "warning")
            return

        services = list(api_keys.keys())

        if HAS_RICH:
            console.print("[cyan]Configured Services:[/cyan]")
            for idx, service in enumerate(services, 1):
                console.print(f"[{idx}] {service}")
            service_choice = Prompt.ask("Select service to remove")
        else:
            print("\nConfigured Services:")
            for idx, service in enumerate(services, 1):
                print(f"[{idx}] {service}")
            service_choice = input("Select service to remove: ").strip()

        try:
            service_idx = int(service_choice) - 1
            service = services[service_idx]

            del self.config['api_keys'][service]
            self._save_config()

            self.cli.show_status(f"API key for {service} removed", "success")

        except (ValueError, IndexError, KeyError):
            self.cli.show_status("Invalid selection", "error")

    def _validate_api_keys(self):
        """Validate configured API keys"""
        self.cli.show_status("Validating API keys...", "info")

        api_keys = self.config.get('api_keys', {})
        validations = {}

        for service, key in api_keys.items():
            if key:
                validations[service] = "✓ Configured"
            else:
                validations[service] = "✗ Missing"

        headers = ["Service", "Status"]
        rows = [[service, status] for service, status in validations.items()]

        self.cli.display_table("API Key Validation", headers, rows)

    async def _test_database_connection(self):
        """Test database connections"""
        self.cli.show_status("Testing database connections...", "info")

        # Test MongoDB
        try:
            from pymongo import MongoClient
            uri = self.config.get('mongodb_uri', 'mongodb://localhost:27017')
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            client.server_info()
            self.cli.show_status("MongoDB: Connected ✓", "success")
            client.close()
        except Exception as e:
            self.cli.show_status(f"MongoDB: Failed ✗ ({str(e)})", "error")

        # Test Redis
        try:
            import redis
            host = self.config.get('redis_host', 'localhost')
            port = self.config.get('redis_port', 6379)
            r = redis.Redis(host=host, port=port, socket_timeout=2)
            r.ping()
            self.cli.show_status("Redis: Connected ✓", "success")
        except Exception as e:
            self.cli.show_status(f"Redis: Failed ✗ ({str(e)})", "error")
