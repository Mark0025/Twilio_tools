#!/usr/bin/env python3
"""
Twilio CLI Tools - Comprehensive Index-Based CLI

This CLI provides access to all Twilio tools through a simple index system.
Use: python -m twilio_cli.cli <index> [args...]
Example: python -m twilio_cli.cli 9 239 (search subaccount for '239')
"""

import os
import sys
import click
import json
import time
import glob
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from loguru import logger

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from twilio_cli.utils.call_log import CallLogBook
from twilio_cli.api.trusthub_inspector import (
    fetch_customer_profile, list_customer_profiles, list_subaccounts,
    get_subaccount_trusthub_profiles, search_subaccount_by_number,
    render_profile_table, render_entity_assignments, render_brand_table,
    render_campaign_table, render_messaging_services_table,
    render_subaccounts_table, render_subaccount_search_results,
    status_style, list_a2p_brands, list_a2p_campaigns, list_messaging_services
)

# Initialize console and logging
console = Console()

# Get absolute paths
BASE_DIR = Path(__file__).parent.parent.parent
APPLOGS_DIR = BASE_DIR / "applogs"
TESTLOGS_DIR = BASE_DIR / "tests" / "logs"
UPLOADS_DIR = BASE_DIR / "uploads"
CLI_COMMANDS_PATH = Path(__file__).parent / "cli_commands" / "cli_commands.json"
PHONE_INFOGA_DIR = BASE_DIR / "tools" / "PhoneInfoga"

# Create directories
APPLOGS_DIR.mkdir(exist_ok=True)
TESTLOGS_DIR.mkdir(exist_ok=True)

APP_LOG_PATH = APPLOGS_DIR / "app.log"
TEST_LOG_PATH = TESTLOGS_DIR / "test.log"

# Configure loguru
logger.add(str(APP_LOG_PATH), rotation="1 MB", retention="10 days", level="INFO")
logger.add(str(TEST_LOG_PATH), rotation="1 MB", retention="10 days", level="INFO")

def load_cli_commands():
    """Load CLI commands from JSON file."""
    if not CLI_COMMANDS_PATH.exists():
        logger.warning(f"CLI commands file not found: {CLI_COMMANDS_PATH}")
        return {}
    try:
        with open(CLI_COMMANDS_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading CLI commands: {e}")
        return {}

def load_error_map():
    """Load Twilio error map."""
    error_map_path = Path(__file__).parent / "utils" / "twilio_error_map.json"
    if not error_map_path.exists():
        return {}
    try:
        with open(error_map_path, "r") as f:
            data = json.load(f)

        return {int(e.get("code", i)): e for i, e in enumerate(data)}
    except Exception as e:
        logger.warning(f"Could not load error map: {e}")
        return {}

def check_phone_infoga_available():
    """Check if PhoneInfoga tools are available."""
    return PHONE_INFOGA_DIR.exists() and (PHONE_INFOGA_DIR / "main.go").exists()

def run_phone_infoga_command(command, args=None):
    """Run a PhoneInfoga command."""
    if not check_phone_infoga_available():
        console.print("[red]PhoneInfoga tools not available[/red]")
        return False
    
    try:
        # Change to PhoneInfoga directory and run command
        cmd = ["go", "run", "main.go", command]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(
            cmd, 
            cwd=str(PHONE_INFOGA_DIR),
            capture_output=True, 
            text=True, 
            check=True
        )
        
        console.print(f"[green]PhoneInfoga {command} output:[/green]")
        console.print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        console.print(f"[red]PhoneInfoga {command} failed:[/red] {e.stderr}")
        return False
    except Exception as e:
        console.print(f"[red]Error running PhoneInfoga:[/red] {e}")
        return False

def show_main_menu():
    """Display the main interactive menu."""
    console.print("\n[bold cyan]Twilio CLI Tools - Main Menu[/bold cyan]")
    console.print("=" * 60)
    console.print("[yellow]0.[/yellow]  Interactive menu")
    console.print("[yellow]1.[/yellow]  Call Logs & Analysis")
    console.print("[yellow]2.[/yellow]  TrustHub Inspector")
    console.print("[yellow]3.[/yellow]  PhoneInfoga Tools")
    console.print("[yellow]4.[/yellow]  Error Code Lookup")
    console.print("[yellow]5.[/yellow]  Quick Actions")
    console.print("[yellow]6.[/yellow]  Show all commands")
    console.print("[yellow]7.[/yellow]  Exit")
    console.print("=" * 60)

def show_call_logs_menu():
    """Display the call logs submenu."""
    while True:
        console.print("\n[bold green]Call Logs & Analysis[/bold green]")
        console.print("-" * 40)
        console.print("[yellow]1.[/yellow] Analyze call logs")
        console.print("[yellow]2.[/yellow] Show call summary")
        console.print("[yellow]3.[/yellow] Visualize call volume")
        console.print("[yellow]0.[/yellow] Back to main menu")
        
        choice = input("\nSelect option (0-3): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            analyze_logs_command()
            input("\nPress Enter to continue...")
        elif choice == "2":
            show_summary_command()
            input("\nPress Enter to continue...")
        elif choice == "3":
            visualize_calls_command()
            input("\nPress Enter to continue...")
        else:
            console.print("[red]Invalid option. Please select 0-3.[/red]")

def show_trusthub_menu():
    """Display the TrustHub Inspector submenu."""
    while True:
        console.print("\n[bold green]TrustHub Inspector[/bold green]")
        console.print("-" * 40)
        console.print("[yellow]1.[/yellow] List all customer profiles")
        console.print("[yellow]2.[/yellow] Inspect specific profile")
        console.print("[yellow]3.[/yellow] List all subaccounts")
        console.print("[yellow]4.[/yellow] Search subaccounts by number")
        console.print("[yellow]5.[/yellow] Delete customer profile")
        console.print("[yellow]6.[/yellow] Profile health check")
        console.print("[yellow]7.[/yellow] Subaccount overview")
        console.print("[yellow]8.[/yellow] Export profiles")
        console.print("[yellow]9.[/yellow] Production accounts overview")
        console.print("[yellow]0.[/yellow] Back to main menu")
        
        choice = input("\nSelect TrustHub option (0-9): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            list_profiles_command()
            input("\nPress Enter to continue...")
        elif choice == "2":
            profile_sid = input("Enter Customer Profile SID: ").strip()
            if profile_sid:
                inspect_profile_command(profile_sid)
                input("\nPress Enter to continue...")
        elif choice == "3":
            subaccounts_command()
            input("\nPress Enter to continue...")
        elif choice == "4":
            account_number = input("Enter account number to search (e.g., '239'): ").strip()
            if account_number:
                search_subaccount_command(account_number)
                input("\nPress Enter to continue...")
        elif choice == "5":
            profile_sid = input("Enter Customer Profile SID to delete: ").strip()
            if profile_sid:
                delete_profile_command(profile_sid)
                input("\nPress Enter to continue...")
        elif choice == "6":
            profile_health_check_command()
            input("\nPress Enter to continue...")
        elif choice == "7":
            subaccount_overview_command()
            input("\nPress Enter to continue...")
        elif choice == "8":
            export_profiles_command()
            input("\nPress Enter to continue...")
        elif choice == "9":
            production_accounts_overview_command()
            input("\nPress Enter to continue...")
        else:
            console.print("[red]Invalid option. Please select 0-9.[/red]")

def show_phone_infoga_menu():
    """Display the PhoneInfoga tools submenu."""
    if not check_phone_infoga_available():
        console.print("[red]PhoneInfoga tools not available[/red]")
        return
    
    while True:
        console.print("\n[bold green]PhoneInfoga Tools[/bold green]")
        console.print("-" * 40)
        console.print("[yellow]1.[/yellow] Scan phone number")
        console.print("[yellow]2.[/yellow] Start web server")
        console.print("[yellow]3.[/yellow] Show version")
        console.print("[yellow]4.[/yellow] List available scanners")
        console.print("[yellow]0.[/yellow] Back to main menu")
        
        choice = input("\nSelect PhoneInfoga option (0-4): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            phone_number = input("Enter phone number to scan: ").strip()
            if phone_number:
                run_phone_infoga_command("scan", [phone_number])
                input("\nPress Enter to continue...")
        elif choice == "2":
            run_phone_infoga_command("serve")
            input("\nPress Enter to continue...")
        elif choice == "3":
            run_phone_infoga_command("version")
            input("\nPress Enter to continue...")
        elif choice == "4":
            run_phone_infoga_command("scanners")
            input("\nPress Enter to continue...")
        else:
            console.print("[red]Invalid option. Please select 0-4.[/red]")

def show_quick_actions_menu():
    """Display the quick actions submenu."""
    while True:
        console.print("\n[bold green]Quick Actions[/bold green]")
        console.print("-" * 40)
        console.print("[yellow]1.[/yellow] Quick search for subaccount '239'")
        console.print("[yellow]0.[/yellow] Back to main menu")
        
        choice = input("\nSelect quick action (0-1): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            search_subaccount_command("239")
            input("\nPress Enter to continue...")
        else:
            console.print("[red]Invalid option. Please select 0-1.[/red]")

def show_command_index():
    """Display all available commands with their numbers."""
    commands = load_cli_commands()
    if not commands:
        console.print("[red]No commands available[/red]")
        return
    
    console.print("\n[bold cyan]Available CLI Commands:[/bold cyan]")
    console.print("Use: python -m twilio_cli.cli <number> [args...]")
    console.print("Example: python -m twilio_cli.cli 9 239 (search subaccount for '239')\n")
    
    # Group by category
    categories = {}
    for num, cmd in commands["commands"].items():
        cat = cmd["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((num, cmd))
    
    for category, cmds in categories.items():
        console.print(f"[bold green]{category}:[/bold green]")
        for num, cmd in sorted(cmds, key=lambda x: int(x[0])):
            args_str = " ".join(cmd["args"]) if cmd["args"] else ""
            console.print(f"  [yellow]{num:>2}[/yellow] {cmd['name']:<25} - {cmd['description']}")
            if args_str:
                console.print(f"      Args: {args_str}")
        console.print()

def execute_number_command(command_num, args=None):
    """Execute a command by its number."""
    commands = load_cli_commands()
    if not commands:
        console.print("[red]No commands available[/red]")
        return False
    
    if command_num not in commands["commands"]:
        console.print(f"[red]Command number '{command_num}' not found.[/red]")
        return False
    
    command_info = commands["commands"][command_num]
    command_name = command_info["command"]
    expected_args = command_info["args"]
    
    # Check if we have the right number of arguments
    if args and len(args) != len(expected_args):
        console.print(f"[red]Command '{command_info['name']}' expects {len(expected_args)} argument(s): {expected_args}[/red]")
        return False
    
    console.print(f"[bold green]🚀 Executing: {command_info['name']}[/bold green]")
    console.print(f"[dim]{command_info['description']}[/dim]")
    if args:
        console.print(f"[dim]Arguments: {' '.join(args)}[/dim]")
    console.print()
    
    # Execute the command
    try:
        if command_name == "menu":
            menu()
        elif command_name == "phone-infoga-scan":
            if args:
                run_phone_infoga_command("scan", args)
            else:
                console.print("[red]Phone number required[/red]")
        elif command_name == "phone-infoga-serve":
            run_phone_infoga_command("serve")
        elif command_name == "phone-infoga-version":
            run_phone_infoga_command("version")
        elif command_name == "phone-infoga-scanners":
            run_phone_infoga_command("scanners")
        elif command_name == "lookup-error":
            if args:
                try:
                    lookup_error_command(int(args[0]))
                except ValueError:
                    console.print("[red]Error code must be a valid number[/red]")
            else:
                console.print("[red]Error code required[/red]")
        elif command_name == "trusthub-menu":
            show_trusthub_menu()
        elif command_name == "list-profiles":
            list_profiles_command()
        elif command_name == "inspect-profile":
            if args:
                inspect_profile_command(args[0])
            else:
                console.print("[red]Profile SID required[/red]")
        elif command_name == "list-subaccounts":
            subaccounts_command()
        elif command_name == "search-subaccount":
            if args:
                search_subaccount_command(args[0])
            else:
                console.print("[red]Account number required[/red]")
        elif command_name == "delete-profile":
            if args:
                delete_profile_command(args[0])
            else:
                console.print("[red]Profile SID required[/red]")
        elif command_name == "quick-search-239":
            search_subaccount_command("239")
        elif command_name == "profile-health-check":
            profile_health_check_command()
        elif command_name == "subaccount-overview":
            subaccount_overview_command()
        elif command_name == "export-profiles":
            export_profiles_command()
        elif command_name == "analyze-logs":
            analyze_logs_command()
        elif command_name == "show-summary":
            show_summary_command()
        elif command_name == "visualize-calls":
            visualize_calls_command()
        elif command_name == "production-accounts-overview":
            production_accounts_overview_command()
        else:
            console.print(f"[yellow]Command '{command_name}' not yet implemented for direct execution.[/yellow]")
        
        return True
    except Exception as e:
        console.print(f"[bold red]Error executing command:[/bold red] {e}")
        return False

@click.group()
def cli():
    """Twilio CLI Tools - Comprehensive Twilio management and analysis toolkit."""
    pass

@click.command()
def index():
    """Show all available commands with their numbers."""
    show_command_index()

@click.command()
@click.argument("command_number", type=int)
@click.argument("args", nargs=-1)
def number(command_number, args):
    """Execute a command by its number."""
    execute_number_command(str(command_number), list(args))

@click.command()
def menu():
    """Interactive menu for Twilio CLI Tools."""
    logbook = CallLogBook()
    error_map = load_error_map()
    
    while True:
        show_main_menu()
        choice = input("\nSelect option (0-7): ").strip()
        
        if choice == "0":
            # Interactive menu (recursive call)
            continue
        elif choice == "1":
            show_call_logs_menu()
        elif choice == "2":
            show_trusthub_menu()
        elif choice == "3":
            show_phone_infoga_menu()
        elif choice == "4":
            # Error Code Lookup - Fixed to work properly
            while True:
                console.print("\n[bold green]Error Code Lookup[/bold green]")
                console.print("-" * 40)
                error_code = input("Enter Twilio error code (or '0' to go back): ").strip()
                
                if error_code == "0":
                    break
                elif error_code and error_code.isdigit():
                    lookup_error(int(error_code))
                    input("\nPress Enter to continue...")
                else:
                    console.print("[red]Please enter a valid error code[/red]")
        elif choice == "5":
            show_quick_actions_menu()
        elif choice == "6":
            show_command_index()
            input("\nPress Enter to continue...")
        elif choice == "7":
            logger.info("Exiting CLI tool.")
            logbook.add_history("exit")
            console.print("[bold green]Goodbye![/bold green]")
            break
        else:
            console.print("[red]Invalid option. Please select 0-7.[/red]")

# TrustHub Inspector Commands
@cli.command()
def list_profiles():
    """List all available customer profiles in your Twilio account."""
    list_profiles_command()

def list_profiles_command():
    """Implementation of list profiles command."""
    try:
        console.print("\n[bold cyan]Available TrustHub Customer Profiles[/bold cyan]")
        console.print("=" * 60)
        
        profiles = list_customer_profiles(limit=100)
        
        if not profiles:
            console.print("[yellow]No customer profiles found in your account.[/yellow]")
            return
        
        # Beautiful rich table
        table = Table(title="Customer Profiles", box=box.ROUNDED)
        table.add_column("SID", style="cyan", no_wrap=True)
        table.add_column("Friendly Name", style="bold")
        table.add_column("Status", style="white")
        table.add_column("Email", style="yellow")
        
        for profile in profiles:
            table.add_row(
                profile.sid,
                getattr(profile, 'friendly_name', '[i]N/A[/i]') or "[i]N/A[/i]",
                status_style(getattr(profile, 'status', None)),
                getattr(profile, 'email', '[i]N/A[/i]') or "[i]N/A[/i]"
            )
        
        console.print(table)
        console.print(f"[green]Found {len(profiles)} customer profile(s)[/green]")
        
    except Exception as exc:
        console.print(f"[bold red]Error listing customer profiles:[/bold red] {exc}")

@cli.command()
@click.argument("profile_sid")
def inspect_profile(profile_sid):
    """Inspect a TrustHub customer profile."""
    inspect_profile_command(profile_sid)

def inspect_profile_command(profile_sid):
    """Implementation of inspect profile command."""
    try:
        console.print(f"\n[bold cyan]Inspecting TrustHub Profile: {profile_sid}[/bold cyan]")
        console.print("=" * 60)
        
        profile = fetch_customer_profile(profile_sid)
        console.print(render_profile_table(profile))
        
        # Show additional info
        console.print("=" * 60)
        
    except Exception as exc:
        console.print(f"[bold red]Error fetching profile:[/bold red] {exc}")
        console.print("\n[dim]This could mean:[/dim]")
        console.print("[dim]• The profile SID doesn't exist[/dim]")
        console.print("[dim]• You don't have access to this profile[/dim]")
        console.print("[dim]• The profile was deleted[/dim]")
        console.print("[dim]• There's an API authentication issue[/dim]")

@cli.command()
def subaccounts():
    """List all subaccounts and their TrustHub profile status."""
    subaccounts_command()

def subaccounts_command():
    """Implementation of subaccounts command."""
    try:
        console.print("\n[bold green]Subaccounts & TrustHub Status[/bold green]")
        console.print("=" * 60)
        
        subaccounts_list = list_subaccounts(limit=200)
        
        if not subaccounts_list:
            console.print("[yellow]No subaccounts found in your account.[/yellow]")
            return
        
        # Group by main account vs subaccounts
        main_account = None
        subaccounts_only = []
        
        for account in subaccounts_list:
            if account.sid == os.getenv("TWILIO_ACCOUNT_SID"):
                main_account = account
            else:
                subaccounts_only.append(account)
        
        # Show main account info
        if main_account:
            console.print(f"\nMain Account: {main_account.friendly_name or main_account.sid}")
            console.print(f"Account SID: {main_account.sid}")
            console.print(f"Status: {status_style(main_account.status)}")
            console.print(f"Type: Main Account")
        else:
            console.print("\nNo main account found.")
        
        # Show subaccounts
        if subaccounts_only:
            console.print(f"\nFound {len(subaccounts_only)} subaccount(s):")
            
            for subaccount in subaccounts_only:
                console.print(f"\nSubaccount: {subaccount.friendly_name or subaccount.sid}")
                
                # Get TrustHub profiles for this subaccount
                sub_profiles = get_subaccount_trusthub_profiles(subaccount.sid)
                
                if sub_profiles:
                    console.print("\nTrustHub Profiles:")
                    console.print("-" * 60)
                    console.print(f"{'SID':<20} {'Name':<30} {'Status':<20} {'Email':<30}")
                    console.print("-" * 100)
                    
                    for profile in sub_profiles:
                        sid = profile.sid
                        name = getattr(profile, 'friendly_name', 'N/A') or 'N/A'
                        status = getattr(profile, 'status', 'N/A')
                        email = getattr(profile, 'email', 'N/A') or 'N/A'
                        
                        console.print(f"{sid:<20} {name[:29]:<30} {status[:19]:<20} {email[:29]:<30}")
                else:
                    console.print("No TrustHub profiles found for this subaccount")
        else:
            console.print("No subaccounts found")
        
        console.print("=" * 60)
        
    except Exception as exc:
        console.print(f"[bold red]Error listing subaccounts:[/bold red] {exc}")

@cli.command()
@click.argument("account_number")
def search_subaccount(account_number):
    """Search for subaccounts by account number (e.g., '239' from 'dev-company-239')."""
    search_subaccount_command(account_number)

def search_subaccount_command(account_number):
    """Implementation of search subaccount command."""
    try:
        console.print(f"\n[bold green]Searching Subaccounts for Number: {account_number}[/bold green]")
        console.print("=" * 60)
        
        matching_subaccounts = search_subaccount_by_number(account_number)
        
        if not matching_subaccounts:
            console.print(f"[yellow]No subaccounts found containing number '{account_number}'[/yellow]")
            return
        
        # Show search results
        console.print(render_subaccount_search_results(matching_subaccounts, account_number))
        
        # Show detailed TrustHub info for each matching subaccount
        for subaccount in matching_subaccounts:
            console.print(f"\n[bold cyan]Detailed TrustHub Status for: {subaccount.friendly_name}[/bold cyan]")
            
            # Get TrustHub profiles for this subaccount
            sub_profiles = get_subaccount_trusthub_profiles(subaccount.sid)
            
            if sub_profiles:
                # Count by status
                status_counts = {}
                for profile in sub_profiles:
                    status = getattr(profile, 'status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Show status summary
                console.print("\nTrustHub Profile Status Summary:")
                console.print("-" * 60)
                console.print(f"{'Status':<20} {'Count':<10}")
                console.print("-" * 30)
                
                for status, count in status_counts.items():
                    console.print(f"{status_style(status):<20} {count:<10}")
                
                # Show approved profiles if any
                approved_profiles = [p for p in sub_profiles if getattr(p, 'status', '') == 'TWILIO-APPROVED']
                if approved_profiles:
                    console.print(f"\n[green]✅ {len(approved_profiles)} Approved Profile(s):[/green]")
                    for profile in approved_profiles:
                        console.print(f"  • {getattr(profile, 'friendly_name', 'N/A')} ({profile.sid})")
                
                # Show rejected profiles if any
                rejected_profiles = [p for p in sub_profiles if 'REJECTED' in str(getattr(p, 'status', ''))]
                if rejected_profiles:
                    console.print(f"\n[red]❌ {len(rejected_profiles)} Rejected Profile(s):[/red]")
                    for profile in rejected_profiles[:5]:  # Show first 5
                        console.print(f"  • {getattr(profile, 'friendly_name', 'N/A')} ({profile.sid})")
                    if len(rejected_profiles) > 5:
                        console.print(f"  ... and {len(rejected_profiles) - 5} more")
            else:
                console.print("[yellow]No TrustHub profiles found for this subaccount[/yellow]")
        
        console.print("=" * 60)
        
    except Exception as exc:
        console.print(f"[bold red]Error searching subaccounts:[/bold red] {exc}")

@cli.command()
@click.argument("profile_sid")
def delete_profile(profile_sid):
    """Delete a customer profile permanently (irreversible)."""
    delete_profile_command(profile_sid)

def delete_profile_command(profile_sid):
    """Implementation of delete profile command."""
    try:
        from rich.prompt import Confirm
        
        # Fetch to display name
        profile = fetch_customer_profile(profile_sid)
        console.print(Panel(f"[bold]{profile.friendly_name}[/bold]\nSID: {profile.sid}\nStatus: {status_style(profile.status)}",
                            title="[red]Delete Confirmation[/red]", border_style="red"))

        confirm = Confirm.ask("[red]This action is permanent. Type 'yes' to confirm deletion[/red]", default=False)
        if confirm:
            from twilio.rest import Client
            client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
            client.trusthub.v1.customer_profiles(profile_sid).delete()
            console.print(f"[green]✅ Profile {profile_sid} deleted.[/green]")
        else:
            console.print("[yellow]Cancelled.[/yellow]")

    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")

# New commands for enhanced functionality
@cli.command()
def profile_health_check():
    """Check health of all TrustHub profiles."""
    profile_health_check_command()

def profile_health_check_command():
    """Implementation of profile health check command."""
    try:
        console.print("\n[bold blue]TrustHub Profile Health Check[/bold blue]")
        console.print("=" * 60)
        
        profiles = list_customer_profiles(limit=100)
        
        if not profiles:
            console.print("No customer profiles found in your account.")
            return
        
        # Count by status
        status_counts = {}
        for profile in profiles:
            status = getattr(profile, 'status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Health summary
        console.print("\nProfile Health Summary:")
        console.print("-" * 60)
        console.print(f"{'Status':<20} {'Count':<10} {'Health':<20}")
        console.print("-" * 50)
        
        total_profiles = len(profiles)
        approved_count = status_counts.get('TWILIO-APPROVED', 0)
        pending_count = status_counts.get('PENDING_REVIEW', 0)
        rejected_count = sum(count for status, count in status_counts.items() if 'REJECTED' in str(status))
        
        for status, count in status_counts.items():
            if status == 'TWILIO-APPROVED':
                health = "✅ Healthy"
            elif 'REJECTED' in str(status):
                health = "❌ Needs Attention"
            else:
                health = "⚠️  Pending"
            
            console.print(f"{status_style(status):<20} {count:<10} {health:<20}")
        
        # Overall health score
        health_score = (approved_count / total_profiles * 100) if total_profiles > 0 else 0
        console.print(f"\n[bold]Overall Health Score: {health_score:.1f}%[/bold]")
        
        if health_score >= 80:
            console.print("[green]🎉 Excellent profile health![/green]")
        elif health_score >= 60:
            console.print("[yellow]⚠️  Good profile health, some attention needed[/yellow]")
        else:
            console.print("[red]🚨 Profile health needs immediate attention[/red]")
        
        console.print("=" * 60)
        
    except Exception as exc:
        console.print(f"[bold red]Error checking profile health:[/bold red] {exc}")

@cli.command()
def subaccount_overview():
    """Overview of all subaccounts with TrustHub status."""
    subaccount_overview_command()

def subaccount_overview_command():
    """Implementation of subaccount overview command."""
    try:
        console.print("\n[bold green]Subaccount TrustHub Overview[/bold green]")
        console.print("=" * 60)
        
        subaccounts_list = list_subaccounts(limit=200)
        
        if not subaccounts_list:
            console.print("[yellow]No subaccounts found in your account.[/yellow]")
            return
        
        # Get TrustHub profiles from the main account (all subaccounts share these)
        main_profiles = list_customer_profiles(limit=100)
        
        if not main_profiles:
            console.print("[yellow]No TrustHub profiles found in your account.[/yellow]")
            return
        
        # Count profiles by status
        status_counts = {}
        for profile in main_profiles:
            status = getattr(profile, 'status', 'unknown')
            # Normalize status to uppercase for consistent counting
            status_upper = str(status).upper()
            status_counts[status_upper] = status_counts.get(status_upper, 0) + 1
        
        # Show summary statistics
        console.print(f"\n[bold cyan]Overall TrustHub Health Summary[/bold cyan]")
        console.print("-" * 50)
        console.print(f"Total Accounts: {len(subaccounts_list)}")
        console.print(f"Total TrustHub Profiles: {len(main_profiles)}")
        console.print(f"Approved: [green]{status_counts.get('TWILIO-APPROVED', 0)}[/green]")
        console.print(f"Draft: [yellow]{status_counts.get('DRAFT', 0)}[/yellow]")
        console.print(f"Rejected: [red]{status_counts.get('TWILIO-REJECTED', 0)}[/red]")
        console.print(f"Other: [white]{sum(count for status, count in status_counts.items() if status not in ['TWILIO-APPROVED', 'DRAFT', 'TWILIO-REJECTED'])}[/white]")
        
        overall_health = (status_counts.get('TWILIO-APPROVED', 0) / len(main_profiles) * 100) if main_profiles else 0
        if overall_health >= 80:
            health_status = "[green]🎉 Excellent[/green]"
        elif overall_health >= 60:
            health_status = "[yellow]⚠️  Good[/yellow]"
        elif overall_health >= 40:
            health_status = "[orange]🚨 Fair[/orange]"
        else:
            health_status = "[red]💀 Poor[/red]"
        
        console.print(f"Overall Health: {health_status} ({overall_health:.1f}%)")
        
        # Show profiles that need attention
        console.print(f"\n[bold red]🚨 Profiles Needing Attention[/bold red]")
        console.print("-" * 50)
        
        rejected_profiles = [p for p in main_profiles if str(getattr(p, 'status', '')).upper() == 'TWILIO-REJECTED']
        if rejected_profiles:
            for profile in rejected_profiles[:10]:  # Show top 10
                console.print(f"[red]❌ {getattr(profile, 'friendly_name', 'N/A')}[/red] - {profile.sid}")
            if len(rejected_profiles) > 10:
                console.print(f"[dim]... and {len(rejected_profiles) - 10} more rejected profiles[/dim]")
        else:
            console.print("[green]✅ No rejected profiles found[/green]")
        
        # Show approved profiles
        console.print(f"\n[bold green]🏆 Approved Profiles[/bold green]")
        console.print("-" * 50)
        
        approved_profiles = [p for p in main_profiles if str(getattr(p, 'status', '')).upper() == 'TWILIO-APPROVED']
        if approved_profiles:
            for profile in approved_profiles[:10]:  # Show top 10
                console.print(f"[green]✅ {getattr(profile, 'friendly_name', 'N/A')}[/green] - {profile.sid}")
            if len(approved_profiles) > 10:
                console.print(f"[dim]... and {len(approved_profiles) - 10} more approved profiles[/dim]")
        else:
            console.print("[yellow]No approved profiles found[/yellow]")
        
        # Show account structure
        console.print(f"\n[bold blue]Account Structure[/bold blue]")
        console.print("-" * 50)
        
        main_account = None
        subaccounts_only = []
        
        for account in subaccounts_list:
            if account.sid == os.getenv("TWILIO_ACCOUNT_SID"):
                main_account = account
            else:
                subaccounts_only.append(account)
        
        if main_account:
            console.print(f"[bold]Main Account:[/bold] {main_account.friendly_name or main_account.sid}")
            console.print(f"[bold]Account SID:[/bold] {main_account.sid}")
            console.print(f"[bold]Status:[/bold] {status_style(main_account.status)}")
            console.print(f"[bold]TrustHub Profiles:[/bold] {len(main_profiles)}")
        
        if subaccounts_only:
            console.print(f"\n[bold]Subaccounts:[/bold] {len(subaccounts_only)}")
            console.print("[dim]Note: All subaccounts share the same TrustHub profiles from the main account[/dim]")
            
            # Show subaccount names grouped by prefix
            prefixes = {}
            for subaccount in subaccounts_only:
                name = subaccount.friendly_name or subaccount.sid
                if name.startswith('-company-'):
                    prefix = '-company-'
                elif name.startswith('prod-company-'):
                    prefix = 'prod-company-'
                elif name.startswith('dev-company-'):
                    prefix = 'dev-company-'
                else:
                    prefix = 'other'
                
                if prefix not in prefixes:
                    prefixes[prefix] = []
                prefixes[prefix].append(name)
            
            for prefix, names in prefixes.items():
                if prefix == 'other':
                    console.print(f"\n[bold]{prefix.title()}:[/bold] {len(names)} accounts")
                else:
                    console.print(f"\n[bold]{prefix.replace('-', ' ').title()}:[/bold] {len(names)} accounts")
                    # Show first few names
                    for name in names[:5]:
                        console.print(f"  [dim]• {name}[/dim]")
                    if len(names) > 5:
                        console.print(f"  [dim]... and {len(names) - 5} more[/dim]")
        
        console.print("=" * 60)
        
    except Exception as exc:
        console.print(f"[bold red]Error getting subaccount overview:[/bold red] {exc}")

@cli.command()
def export_profiles():
    """Export TrustHub profiles to JSON."""
    export_profiles_command()

def export_profiles_command():
    """Implementation of export profiles command."""
    try:
        console.print("\n[bold blue]Exporting TrustHub Profiles[/bold blue]")
        console.print("=" * 60)
        
        profiles = list_customer_profiles(limit=100)
        
        if not profiles:
            console.print("[yellow]No customer profiles found to export.[/yellow]")
            return
        
        # Convert profiles to exportable format
        export_data = []
        for profile in profiles:
            export_data.append({
                "sid": profile.sid,
                "friendly_name": getattr(profile, 'friendly_name', None),
                "status": getattr(profile, 'status', None),
                "email": getattr(profile, 'email', None),
                "phone_number": getattr(profile, 'phone_number', None),
                "business_name": getattr(profile, 'business_name', None),
                "business_type": getattr(profile, 'customer_profile_type', None),
                "date_created": str(getattr(profile, 'date_created', None)),
                "date_updated": str(getattr(profile, 'date_updated', None))
            })
        
        # Export to file
        export_path = TESTLOGS_DIR / f"trusthub_profiles_export_{int(time.time())}.json"
        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        console.print(f"[green]✅ Exported {len(export_data)} profiles to: {export_path}[/green]")
        console.print("=" * 60)
        
    except Exception as exc:
        console.print(f"[bold red]Error exporting profiles:[/bold red] {exc}")

# Call Log Analysis Commands
@cli.command()
def analyze_logs():
    """Analyze call logs from CSV files."""
    analyze_logs_command()

def analyze_logs_command():
    """Implementation of analyze logs command."""
    try:
        logbook = CallLogBook()
        error_map = load_error_map()
        
        # Analyze logs: load first CSV, pretty print, export to JSON with error enrichment
        csv_files = glob.glob(str(UPLOADS_DIR / "*.csv"))
        if not csv_files:
            console.print("[red]No CSV files found in uploads directory.[/red]")
            logger.error("No CSV files found in uploads directory.")
            return
        
        csv_path = csv_files[0]
        logbook.load_from_csv(csv_path)
        
        # Enrich each entry with error info
        enriched = []
        for entry in logbook.entries:
            code = None
            try:
                code = int(getattr(entry, 'error_code', None) or getattr(entry, 'status', None) or 0)
            except Exception:
                pass
            error_info = error_map.get(code, {})
            enriched.append({
                **entry.to_dict(),
                "developer_message": error_info.get("developer_message", ""),
                "human_message": error_info.get("human_message", ""),
                "support_action": error_info.get("support_action", "")
            })
        
        logbook.pretty_print(limit=10)
        json_path = TESTLOGS_DIR / "call_logs.json"
        with open(json_path, "w") as f:
            json.dump(enriched, f, indent=2)
        
        logbook.add_history("analyze logs")
        logger.info(f"Analyzed logs from {csv_path} and exported to {json_path}")
        
    except Exception as exc:
        console.print(f"[bold red]Error analyzing logs:[/bold red] {exc}")

@cli.command()
def show_summary():
    """Show call summary statistics."""
    show_summary_command()

def show_summary_command():
    """Implementation of show summary command."""
    try:
        logbook = CallLogBook()
        
        # Load logs if available
        csv_files = glob.glob(str(UPLOADS_DIR / "*.csv"))
        if csv_files:
            csv_path = csv_files[0]
            logbook.load_from_csv(csv_path)
        
        table = Table(title="Call Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("Total Calls", str(len(logbook.entries)))
        table.add_row("Completed Calls", str(len([e for e in logbook.entries if getattr(e, 'status', '') == 'Completed'])))
        table.add_row("No Answer Calls", str(len([e for e in logbook.entries if getattr(e, 'status', '') == 'No Answer'])))
        console.print(table)
        logbook.add_history("show summary")
        logger.info("Displayed summary table.")
        
    except Exception as exc:
        console.print(f"[bold red]Error showing summary:[/bold red] {exc}")

@cli.command()
def visualize_calls():
    """Visualize call volume (stub)."""
    visualize_calls_command()

def visualize_calls_command():
    """Implementation of visualize calls command."""
    try:
        console.print("[blue]Visualizing call volume... (stub)[/blue]")
        # TODO: Implement actual visualization
        logger.info("Visualized call volume (stub).")
        
    except Exception as exc:
        console.print(f"[bold red]Error visualizing calls:[/bold red] {exc}")

def lookup_error_command(error_code):
    """Implementation of lookup error command."""
    error_map = load_error_map()
    info = error_map.get(error_code)
    if not info:
        console.print(f"[red]No info found for error code {error_code}.[/red]")
        logger.warning(f"No info found for error code {error_code}")
        return
    
    table = Table(title=f"Twilio Error Code {error_code}", box=box.ROUNDED)
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Message", info.get("message", ""))
    table.add_row("Description", info.get("description", ""))
    table.add_row("Product", info.get("product", ""))
    table.add_row("Log Level", info.get("log_level", ""))
    if info.get("causes"):
        table.add_row("Causes", info.get("causes", ""))
    if info.get("solutions"):
        table.add_row("Solutions", info.get("solutions", ""))
    console.print(table)
    logger.info(f"Looked up error code {error_code}")

@cli.command()
@click.argument("error_code", type=int)
def lookup_error(error_code):
    """Lookup and explain a Twilio error code."""
    lookup_error_command(error_code)

# Quick action commands
@cli.command()
def quick_search_239():
    """Quick search for subaccount containing '239'."""
    search_subaccount_command("239")

def production_accounts_overview_command():
    """Implementation of production accounts overview command."""
    production_accounts_overview()

@cli.command()
def production_accounts_overview():
    """Overview of production accounts with messaging campaigns and 10DLC status."""
    try:
        console.print("\n[bold green]Production Accounts Overview[/bold green]")
        console.print("=" * 60)
        
        # Get all subaccounts and filter for production ones
        subaccounts_list = list_subaccounts(limit=200)
        prod_accounts = [acc for acc in subaccounts_list if acc.friendly_name and acc.friendly_name.startswith('prod-company-')]
        
        if not prod_accounts:
            console.print("[yellow]No production accounts found.[/yellow]")
            return
        
        console.print(f"Found [bold]{len(prod_accounts)}[/bold] production accounts")
        
        # Get TrustHub profiles, A2P brands, and campaigns from main account
        main_profiles = list_customer_profiles(limit=100)
        a2p_brands = list_a2p_brands(limit=100)
        a2p_campaigns = list_a2p_campaigns(limit=200)
        messaging_services = list_messaging_services(limit=200)
        
        # Group production accounts by company number for easier management
        company_groups = {}
        for account in prod_accounts:
            name = account.friendly_name
            # Extract company number from "prod-company-XXX"
            if name.startswith('prod-company-'):
                company_num = name.replace('prod-company-', '')
                if company_num not in company_groups:
                    company_groups[company_num] = []
                company_groups[company_num].append(account)
        
        # Show summary by company number
        console.print(f"\n[bold cyan]Production Companies Summary[/bold cyan]")
        console.print("-" * 50)
        console.print(f"Total Production Companies: {len(company_groups)}")
        console.print(f"Total Production Accounts: {len(prod_accounts)}")
        
        # Show TrustHub and 10DLC status
        approved_profiles = [p for p in main_profiles if str(getattr(p, 'status', '')).upper() == 'TWILIO-APPROVED']
        approved_brands = [b for b in a2p_brands if getattr(b, 'status', '').upper() in ['APPROVED', 'ACTIVE']]
        approved_campaigns = [c for c in a2p_campaigns if getattr(c, 'status', '').upper() in ['APPROVED', 'ACTIVE']]
        
        console.print(f"\n[bold]TrustHub & 10DLC Status:[/bold]")
        console.print(f"  • Approved TrustHub Profiles: [green]{len(approved_profiles)}[/green]")
        console.print(f"  • Approved A2P Brands: [green]{len(approved_brands)}[/green]")
        console.print(f"  • Approved A2P Campaigns: [green]{len(approved_campaigns)}[/green]")
        
        # Show each production company with their status
        console.print(f"\n[bold blue]Production Companies Status[/bold blue]")
        console.print("-" * 80)
        console.print(f"{'Company':<15} {'Accounts':<10} {'TrustHub':<10} {'10DLC':<10} {'Campaigns':<12} {'Status':<15}")
        console.print("-" * 80)
        
        for company_num in sorted(company_groups.keys(), key=int):
            accounts = company_groups[company_num]
            
            # Check if this company has any approved TrustHub profiles
            company_trusthub_status = "❌"
            company_10dlc_status = "❌"
            company_campaigns_status = "❌"
            
            # For now, we'll show basic status - in a real implementation you'd check
            # which specific profiles/brands/campaigns are linked to which company
            if approved_profiles:
                company_trusthub_status = "✅"
            if approved_brands:
                company_10dlc_status = "✅"
            if approved_campaigns:
                company_campaigns_status = "✅"
            
            overall_status = "🟢 Good" if company_trusthub_status == "✅" and company_10dlc_status == "✅" else "🟡 Partial" if company_trusthub_status == "✅" or company_10dlc_status == "✅" else "🔴 Issues"
            
            console.print(f"{company_num:<15} {len(accounts):<10} {company_trusthub_status:<10} {company_10dlc_status:<10} {company_campaigns_status:<12} {overall_status:<15}")
        
        # Show detailed breakdown for specific companies
        console.print(f"\n[bold yellow]Quick Company Lookup[/bold yellow]")
        console.print("-" * 50)
        console.print("Use these commands to get detailed info for specific companies:")
        console.print("  • [cyan]python twilio_cli.py 4 [company_number][/cyan] - Search by company number")
        console.print("  • [cyan]python twilio_cli.py 2[/cyan] - TrustHub Inspector for detailed profile info")
        console.print("  • [cyan]python twilio_cli.py 6[/cyan] - List all TrustHub profiles")
        
        # Show top 10 production accounts with most activity
        console.print(f"\n[bold green]Top Production Accounts[/bold green]")
        console.print("-" * 50)
        for i, account in enumerate(prod_accounts[:10], 1):
            status_color = "green" if account.status == "ACTIVE" else "yellow" if account.status == "SUSPENDED" else "red"
            console.print(f"{i:2}. [{status_color}]{account.friendly_name}[/{status_color}] - {account.sid[:12]}...")
        
        if len(prod_accounts) > 10:
            console.print(f"[dim]... and {len(prod_accounts) - 10} more production accounts[/dim]")
        
        console.print("=" * 60)
        
    except Exception as exc:
        console.print(f"[bold red]Error getting production accounts overview:[/bold red] {exc}")

if __name__ == "__main__":
    # Check if first argument is a number (for number-based commands)
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        command_num = sys.argv[1]
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        execute_number_command(command_num, args)
    else:
        # Run interactive menu automatically when no arguments
        menu()
