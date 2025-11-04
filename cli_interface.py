#!/usr/bin/env python3
"""
Hughes Clues - Interactive CLI Interface
Provides user-friendly menu-driven access to all modules
"""

import os
import sys
import asyncio
import json
from typing import Dict, List, Optional, Callable
from enum import Enum
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Initialize console
console = Console() if HAS_RICH else None


class MenuOption(Enum):
    """Menu navigation options"""
    RECONNAISSANCE = "1"
    CREDENTIAL_HARVEST = "2"
    DARK_WEB_MONITOR = "3"
    WEB_SCRAPING = "4"
    GEOLOCATION = "5"
    ANALYSIS = "6"
    FULL_PIPELINE = "7"
    VIEW_RESULTS = "8"
    SETTINGS = "9"
    EXIT = "0"


class HughesCLI:
    """Interactive CLI for Hughes Clues"""

    def __init__(self):
        self.config_file = self._find_config()
        self.target = None
        self.results = {}
        self.history = []

    def _find_config(self) -> str:
        """Find configuration file"""
        candidates = [
            os.getenv('CONFIG_FILE'),
            os.path.join(os.getenv('APP_DIR', '/app'), 'config.yaml'),
            os.path.join(os.getcwd(), 'config.yaml'),
            '/opt/hughes_clues/config.yaml'
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return 'config.yaml'

    def print_banner(self):
        """Print application banner"""
        if HAS_RICH:
            banner = """
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

OSINT Intelligence Gathering Framework
            """
            console.print(Panel(banner, border_style="cyan", expand=False))
        else:
            print("""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝
            """)

    def show_main_menu(self) -> str:
        """Display main menu and get selection"""
        if HAS_RICH:
            table = Table(title="Hughes Clues - Main Menu", show_header=False, box=None)
            table.add_column(style="cyan")
            table.add_column(style="white")

            table.add_row("[1]", "🔍  Reconnaissance")
            table.add_row("[2]", "🔐  Credential Harvesting")
            table.add_row("[3]", "🌐  Dark Web Monitoring")
            table.add_row("[4]", "🕷️   Web Scraping")
            table.add_row("[5]", "📍  Geolocation Intelligence")
            table.add_row("[6]", "📊  Analysis Engine")
            table.add_row("[7]", "⚡  Full Intelligence Pipeline")
            table.add_row("[8]", "📈  View Results")
            table.add_row("[9]", "⚙️   Settings")
            table.add_row("[0]", "❌  Exit")

            console.print(table)
            console.print()
        else:
            print("\n=== Hughes Clues - Main Menu ===")
            print("[1] Reconnaissance")
            print("[2] Credential Harvesting")
            print("[3] Dark Web Monitoring")
            print("[4] Web Scraping")
            print("[5] Geolocation Intelligence")
            print("[6] Analysis Engine")
            print("[7] Full Intelligence Pipeline")
            print("[8] View Results")
            print("[9] Settings")
            print("[0] Exit")
            print()

        if HAS_RICH:
            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        else:
            choice = input("Select option (0-9): ").strip()

        return choice

    def get_target(self) -> str:
        """Get target for reconnaissance"""
        if HAS_RICH:
            target = Prompt.ask("Enter target domain or IP")
        else:
            target = input("Enter target domain or IP: ").strip()

        if not target:
            console.print("[red]Error: Target cannot be empty[/red]") if HAS_RICH else print("Error: Target cannot be empty")
            return self.get_target()

        self.target = target
        return target

    def show_recon_menu(self):
        """Reconnaissance options menu"""
        if HAS_RICH:
            console.print("\n[cyan]Reconnaissance Module[/cyan]")
            table = Table(show_header=False, box=None)
            table.add_column(style="cyan")
            table.add_column(style="white")

            table.add_row("[1]", "DNS Enumeration")
            table.add_row("[2]", "WHOIS Lookup")
            table.add_row("[3]", "SSL Certificate Analysis")
            table.add_row("[4]", "Technology Fingerprinting")
            table.add_row("[5]", "Shodan Intelligence")
            table.add_row("[6]", "GitHub Exposure Check")
            table.add_row("[7]", "Breach Database Query")
            table.add_row("[8]", "Cloud Asset Discovery")
            table.add_row("[9]", "Full Reconnaissance")
            table.add_row("[0]", "Back")

            console.print(table)
        else:
            print("\n=== Reconnaissance Module ===")
            print("[1] DNS Enumeration")
            print("[2] WHOIS Lookup")
            print("[3] SSL Certificate Analysis")
            print("[4] Technology Fingerprinting")
            print("[5] Shodan Intelligence")
            print("[6] GitHub Exposure Check")
            print("[7] Breach Database Query")
            print("[8] Cloud Asset Discovery")
            print("[9] Full Reconnaissance")
            print("[0] Back")

        if HAS_RICH:
            choice = Prompt.ask("Select reconnaissance module", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        else:
            choice = input("Select module (0-9): ").strip()

        return choice

    def show_cred_harvest_menu(self):
        """Credential harvesting options menu"""
        if HAS_RICH:
            console.print("\n[cyan]Credential Harvesting Module[/cyan]")
            table = Table(show_header=False, box=None)
            table.add_column(style="cyan")
            table.add_column(style="white")

            table.add_row("[1]", "Query Breach Databases")
            table.add_row("[2]", "Password Analysis")
            table.add_row("[3]", "SSH Credential Testing")
            table.add_row("[4]", "FTP Credential Testing")
            table.add_row("[5]", "HTTP Form Testing")
            table.add_row("[6]", "Hash Cracking")
            table.add_row("[7]", "Full Credential Harvest")
            table.add_row("[0]", "Back")

            console.print(table)
        else:
            print("\n=== Credential Harvesting Module ===")
            print("[1] Query Breach Databases")
            print("[2] Password Analysis")
            print("[3] SSH Credential Testing")
            print("[4] FTP Credential Testing")
            print("[5] HTTP Form Testing")
            print("[6] Hash Cracking")
            print("[7] Full Credential Harvest")
            print("[0] Back")

        if HAS_RICH:
            choice = Prompt.ask("Select credential module", choices=["0", "1", "2", "3", "4", "5", "6", "7"])
        else:
            choice = input("Select module (0-7): ").strip()

        return choice

    def show_settings_menu(self):
        """Settings menu"""
        if HAS_RICH:
            console.print("\n[cyan]Settings[/cyan]")
            table = Table(show_header=False, box=None)
            table.add_column(style="cyan")
            table.add_column(style="white")

            table.add_row("[1]", f"Config File: {self.config_file}")
            table.add_row("[2]", "View Configuration")
            table.add_row("[3]", "Set Custom Config")
            table.add_row("[4]", "API Key Management")
            table.add_row("[5]", "Database Connection Test")
            table.add_row("[0]", "Back")

            console.print(table)
        else:
            print("\n=== Settings ===")
            print(f"[1] Config File: {self.config_file}")
            print("[2] View Configuration")
            print("[3] Set Custom Config")
            print("[4] API Key Management")
            print("[5] Database Connection Test")
            print("[0] Back")

        if HAS_RICH:
            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"])
        else:
            choice = input("Select option (0-5): ").strip()

        return choice

    def show_results_menu(self):
        """Results viewing menu"""
        if HAS_RICH:
            console.print("\n[cyan]View Results[/cyan]")
            table = Table(show_header=False, box=None)
            table.add_column(style="cyan")
            table.add_column(style="white")

            table.add_row("[1]", "View Latest Report")
            table.add_row("[2]", "View Report by Target")
            table.add_row("[3]", "Export Results")
            table.add_row("[4]", "View Operation History")
            table.add_row("[5]", "Clear Results")
            table.add_row("[0]", "Back")

            console.print(table)
        else:
            print("\n=== View Results ===")
            print("[1] View Latest Report")
            print("[2] View Report by Target")
            print("[3] Export Results")
            print("[4] View Operation History")
            print("[5] Clear Results")
            print("[0] Back")

        if HAS_RICH:
            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5"])
        else:
            choice = input("Select option (0-5): ").strip()

        return choice

    def display_table(self, title: str, headers: List[str], rows: List[List[str]]):
        """Display formatted table"""
        if HAS_RICH:
            table = Table(title=title)
            for header in headers:
                table.add_column(header, style="cyan")
            for row in rows:
                table.add_row(*row)
            console.print(table)
        else:
            print(f"\n=== {title} ===")
            print(" | ".join(headers))
            print("-" * 80)
            for row in rows:
                print(" | ".join(row))

    def show_status(self, message: str, status: str = "info"):
        """Display status message"""
        if HAS_RICH:
            if status == "success":
                console.print(f"[green]✓ {message}[/green]")
            elif status == "error":
                console.print(f"[red]✗ {message}[/red]")
            elif status == "warning":
                console.print(f"[yellow]⚠ {message}[/yellow]")
            else:
                console.print(f"[blue]ℹ {message}[/blue]")
        else:
            prefix = "✓" if status == "success" else "✗" if status == "error" else "⚠" if status == "warning" else "ℹ"
            print(f"{prefix} {message}")

    def run_with_spinner(self, task_name: str, func: Callable) -> any:
        """Run function with progress spinner"""
        if HAS_RICH:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                progress.add_task(f"[cyan]{task_name}...", total=None)
                return func()
        else:
            print(f"Running: {task_name}...")
            return func()

    async def execute_orchestrator(self, target: str, operations: List[str] = None):
        """Execute master orchestrator"""
        try:
            from master_orchestrator import MasterOrchestrator, OperationType

            self.show_status(f"Initializing orchestrator for {target}", "info")

            orchestrator = MasterOrchestrator(self.config_file)
            orchestrator.start_workers()

            try:
                if operations:
                    op_map = {
                        '1': OperationType.RECONNAISSANCE,
                        '2': OperationType.WEB_SCRAPING,
                        '3': OperationType.CREDENTIAL_HARVEST,
                        '4': OperationType.GEOLOCATION,
                        '5': OperationType.DARK_WEB,
                    }
                    ops = [op_map.get(op) for op in operations if op in op_map]
                else:
                    ops = None

                report = await orchestrator.run_full_intelligence_pipeline(target, ops)

                self.show_status(f"Intelligence gathering complete for {target}", "success")
                self.show_status(f"Risk Score: {report.risk_score}/100", "info")
                self.show_status(f"Confidence: {report.confidence:.2%}", "info")

                self.results[target] = report
                self.history.append({
                    'target': target,
                    'timestamp': datetime.now().isoformat(),
                    'operations': operations,
                    'risk_score': report.risk_score
                })

                return report

            finally:
                orchestrator.shutdown()

        except Exception as e:
            self.show_status(f"Error: {str(e)}", "error")
            return None

    async def execute_recon(self, target: str):
        """Execute reconnaissance"""
        try:
            from elite_recon_module import AdvancedReconModule, APIConfig

            self.show_status(f"Starting reconnaissance on {target}", "info")

            config = APIConfig.from_file(self.config_file)
            recon = AdvancedReconModule(target, config=config)

            results = await recon.run_full_recon_async()

            self.show_status(f"Reconnaissance complete", "success")
            self.show_status(f"Risk Score: {results['risk_score']}/100", "info")

            self.results[f"{target}_recon"] = results
            return results

        except Exception as e:
            self.show_status(f"Error: {str(e)}", "error")
            return None

    async def execute_credential_harvest(self, target: str):
        """Execute credential harvesting"""
        try:
            from elite_credential_harvester import EliteCredentialHarvester
            import yaml

            self.show_status(f"Starting credential harvest for {target}", "info")

            with open(self.config_file) as f:
                config = yaml.safe_load(f)
                api_keys = config.get('api_keys', {})

            harvester = EliteCredentialHarvester(api_keys)

            if '@' in target:
                results = await harvester.harvest_email(target)
            else:
                results = await harvester.harvest_domain(target)

            await harvester.cleanup()

            self.show_status(f"Credential harvest complete", "success")
            if 'statistics' in results:
                self.show_status(f"Found {results['statistics']['total_credentials']} credentials", "info")

            self.results[f"{target}_creds"] = results
            return results

        except Exception as e:
            self.show_status(f"Error: {str(e)}", "error")
            return None

    def main_loop(self):
        """Main CLI loop"""
        self.print_banner()

        while True:
            choice = self.show_main_menu()

            if choice == "0":  # Exit
                self.show_status("Goodbye!", "info")
                break

            elif choice == "1":  # Reconnaissance
                target = self.get_target()
                asyncio.run(self.execute_recon(target))

            elif choice == "2":  # Credential Harvest
                target = self.get_target()
                asyncio.run(self.execute_credential_harvest(target))

            elif choice == "7":  # Full Pipeline
                target = self.get_target()
                operations = ['1', '2', '3', '4']  # All operations
                asyncio.run(self.execute_orchestrator(target, operations))

            elif choice == "8":  # View Results
                self.show_results_menu()

            elif choice == "9":  # Settings
                self.show_settings_menu()

            else:
                self.show_status("Invalid option. Please try again.", "warning")

            print()  # Blank line for spacing


def main():
    """Entry point"""
    try:
        cli = HughesCLI()
        cli.main_loop()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
