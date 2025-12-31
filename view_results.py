#!/usr/bin/env python3
"""
Quick Results Viewer for Hughes Clues Intelligence Reports
Displays the latest intelligence report from MongoDB
"""

from pymongo import MongoClient
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint
import sys

console = Console()

def view_latest_report():
    """View the most recent intelligence report"""
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017')
        db = client['hughes_clues']
        reports_collection = db['reports']

        # Get the latest report
        latest = reports_collection.find_one(sort=[('timestamp', -1)])

        if not latest:
            console.print("[yellow]No reports found in database[/yellow]")
            return

        report = latest.get('report', {})

        # Display header
        console.print("\n")
        console.print(Panel.fit(
            f"[bold cyan]Intelligence Report Viewer[/bold cyan]\n"
            f"Report ID: {report.get('report_id', 'N/A')}\n"
            f"Generated: {latest.get('timestamp', 'N/A')}",
            border_style="cyan"
        ))

        # Target info
        console.print(f"\n[bold]Target:[/bold] {report.get('target', 'N/A')}")
        console.print(f"[bold]Timestamp:[/bold] {report.get('timestamp', 'N/A')}")

        # Summary statistics
        summary = report.get('summary', {})
        table = Table(title="Summary Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Operations Completed", str(summary.get('operations_completed', 0)))
        table.add_row("Total Operations", str(summary.get('total_operations', 0)))
        table.add_row("Success Rate", f"{summary.get('success_rate', 0):.1f}%")
        table.add_row("Risk Score", f"{summary.get('risk_score', 0)}/100")
        table.add_row("Confidence", f"{summary.get('confidence', 0):.1f}%")

        console.print(table)

        # Operation results
        operations = report.get('operations', {})
        if operations:
            console.print("\n[bold cyan]Operation Results:[/bold cyan]")
            for op_name, op_data in operations.items():
                status = op_data.get('status', 'unknown')
                status_color = 'green' if status == 'completed' else 'red'

                console.print(f"\n[bold]{op_name}:[/bold] [{status_color}]{status}[/{status_color}]")

                # Show data if available
                data = op_data.get('data', {})
                if data and isinstance(data, dict):
                    for key, value in list(data.items())[:5]:  # Show first 5 items
                        if isinstance(value, (str, int, float, bool)):
                            console.print(f"  • {key}: {value}")
                        elif isinstance(value, dict):
                            console.print(f"  • {key}: {len(value)} items")
                        elif isinstance(value, list):
                            console.print(f"  • {key}: {len(value)} entries")

        # Key findings
        findings = report.get('key_findings', [])
        if findings:
            console.print("\n[bold cyan]Key Findings:[/bold cyan]")
            for finding in findings[:10]:  # Show first 10
                console.print(f"  • {finding}")

        # Recommendations
        recommendations = report.get('recommendations', [])
        if recommendations:
            console.print("\n[bold yellow]Recommendations:[/bold yellow]")
            for rec in recommendations[:5]:  # Show first 5
                console.print(f"  • {rec}")

        # Export option
        console.print(f"\n[dim]Full report saved to: output/intel_{report.get('target', 'unknown').replace('.', '_')}_{report.get('timestamp', 'unknown')}.json[/dim]")

    except Exception as e:
        console.print(f"[red]Error viewing report: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
    finally:
        if 'client' in locals():
            client.close()

def list_all_reports():
    """List all reports in the database"""
    try:
        client = MongoClient('mongodb://localhost:27017')
        db = client['hughes_clues']
        reports_collection = db['reports']

        reports = list(reports_collection.find().sort('timestamp', -1).limit(10))

        if not reports:
            console.print("[yellow]No reports found[/yellow]")
            return

        table = Table(title="Recent Intelligence Reports")
        table.add_column("Report ID", style="cyan")
        table.add_column("Target", style="green")
        table.add_column("Timestamp", style="yellow")
        table.add_column("Operations", style="blue")
        table.add_column("Confidence", style="magenta")

        for report in reports:
            report_data = report.get('report', {})
            summary = report_data.get('summary', {})

            table.add_row(
                report_data.get('report_id', 'N/A')[:30],
                report_data.get('target', 'N/A'),
                report.get('timestamp', 'N/A'),
                f"{summary.get('operations_completed', 0)}/{summary.get('total_operations', 0)}",
                f"{summary.get('confidence', 0):.1f}%"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing reports: {str(e)}[/red]")
    finally:
        if 'client' in locals():
            client.close()

def main():
    console.print("[bold cyan]Hughes Clues - Intelligence Report Viewer[/bold cyan]\n")

    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        list_all_reports()
    else:
        view_latest_report()

    console.print("\n[dim]Use --list to see all reports[/dim]")

if __name__ == '__main__':
    main()
