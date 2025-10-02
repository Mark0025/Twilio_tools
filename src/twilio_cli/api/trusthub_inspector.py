#!/usr/bin/env python3
"""
TrustHub Inspector — click + rich CLI for inspecting Twilio TrustHub customer profiles,
A2P brand/campaign status, supporting docs, endpoints, messaging services, and delete.
"""

import os
import sys
import click
from dotenv import load_dotenv
from twilio.rest import Client
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box
from rich.prompt import Confirm

console = Console()

# Load .env
load_dotenv()
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

if not ACCOUNT_SID or not AUTH_TOKEN:
    console.print("[bold red]TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in .env[/bold red]")
    console.print("[yellow]Please create a .env file in the project root with your Twilio credentials[/yellow]")
    sys.exit(1)

client = Client(ACCOUNT_SID, AUTH_TOKEN)


# -----------------------
# Fetch helper functions
# -----------------------
def fetch_customer_profile(sid):
    """Fetch TrustHub Customer Profile"""
    return client.trusthub.v1.customer_profiles(sid).fetch()


def list_customer_entity_assignments(customer_profile_sid, page_size=100):
    """
    Entity assignments include supporting documents, end users, etc.
    See Customer Profile Entity Assignment API.
    """
    try:
        return client.trusthub.v1.customer_profiles(customer_profile_sid).entity_assignments.list(page_size=page_size)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch entity assignments: {e}[/yellow]")
        return []


def list_channel_endpoint_assignments(customer_profile_sid, page_size=100):
    try:
        return client.trusthub.v1.customer_profiles(customer_profile_sid).channel_endpoint_assignments.list(page_size=page_size)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch channel endpoint assignments: {e}[/yellow]")
        return []


def list_supporting_documents(customer_profile_sid, page_size=100):
    # Supporting documents are accessible via entity assignments but the SDK may have direct resource.
    # We will use entity_assignments and filter.
    return [a for a in list_customer_entity_assignments(customer_profile_sid, page_size) if getattr(a, "object_type", "").lower().startswith("supportingdocument")]


def list_a2p_brands(limit=100):
    """List A2P 10DLC Brand registrations for the account (then filter client-side)."""
    # Brand registrations live under the Messaging API (brand registration resource).
    return client.messaging.v1.brand_registrations.list(limit=limit)


def list_a2p_campaigns(limit=200):
    """List A2P Campaigns (campaign registrations)."""
    try:
        # Try different possible endpoint names
        if hasattr(client.messaging.v1, 'campaign_registrations'):
            return client.messaging.v1.campaign_registrations.list(limit=limit)
        elif hasattr(client.messaging.v1, 'campaigns'):
            return client.messaging.v1.campaigns.list(limit=limit)
        else:
            console.print("[yellow]Warning: A2P campaigns endpoint not found[/yellow]")
            return []
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch A2P campaigns: {e}[/yellow]")
        return []


def list_messaging_services(limit=200):
    """List Messaging Services and we'll filter by customer_profile_sid field if present."""
    return client.messaging.v1.services.list(limit=limit)


def list_subaccounts(limit=200):
    """List subaccounts and see if any are linked to profile via metadata — optional."""
    try:
        return client.api.accounts.list(limit=limit)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch subaccounts: {e}[/yellow]")
        return []


def get_subaccount_trusthub_profiles(subaccount_sid):
    """Get TrustHub profiles for a specific subaccount."""
    try:
        # Create a client for the subaccount
        subaccount_client = Client(ACCOUNT_SID, AUTH_TOKEN)
        subaccount_client.account_sid = subaccount_sid
        
        # Try to fetch TrustHub profiles for the subaccount
        profiles = subaccount_client.trusthub.v1.customer_profiles.list(limit=100)
        return profiles
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch TrustHub profiles for subaccount {subaccount_sid}: {e}[/yellow]")
        return []


def render_subaccounts_table(subaccounts, main_profile_sid):
    """Render subaccounts table with TrustHub profile information."""
    if not subaccounts:
        return Panel("[i]No subaccounts found[/i]", title="Subaccounts", border_style="yellow")
    
    table = Table(title="Subaccounts & TrustHub Status", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Account SID", style="cyan", no_wrap=True)
    table.add_column("Friendly Name", style="bold")
    table.add_column("Status", style="white")
    table.add_column("TrustHub Profiles", style="magenta")
    table.add_column("Linked to Main Profile", style="green")
    
    for subaccount in subaccounts:
        if subaccount.sid == ACCOUNT_SID:
            continue  # Skip main account
        
        # Get TrustHub profiles for this subaccount
        sub_profiles = get_subaccount_trusthub_profiles(subaccount.sid)
        profile_count = len(sub_profiles) if sub_profiles else 0
        
        # Check if any profiles are linked to the main profile
        linked = "No"
        if sub_profiles:
            for profile in sub_profiles:
                if hasattr(profile, 'parent_profile_sid') and profile.parent_profile_sid == main_profile_sid:
                    linked = "Yes"
                    break
        
        table.add_row(
            subaccount.sid,
            subaccount.friendly_name or "[i]N/A[/i]",
            status_style(subaccount.status),
            str(profile_count),
            linked
        )
    
    return Panel(table, title="Subaccounts", border_style="bright_green")


def list_customer_profiles(limit=100):
    """List all customer profiles in the account."""
    return client.trusthub.v1.customer_profiles.list(limit=limit)


# -----------------------
# Rendering helpers
# -----------------------
def status_style(val):
    """Apply color coding to status values."""
    if not val:
        return "[yellow]unknown[/yellow]"
    v = str(val).upper()
    if v in ("APPROVED", "ACTIVE", "REGISTERED", "COMPLETED"):
        return f"[green]{v}[/green]"
    if v in ("PENDING", "IN_REVIEW", "SUBMITTED"):
        return f"[yellow]{v}[/yellow]"
    if v in ("FAILED", "REJECTED", "DENIED", "SUSPENDED"):
        return f"[red]{v}[/red]"
    return f"[white]{v}[/white]"


def render_profile_table(profile):
    """Render customer profile information in a rich table."""
    t = Table.grid(expand=True)
    t.add_column(justify="right", ratio=30)
    t.add_column(ratio=70)
    t.add_row("[cyan]SID[/cyan]", f"[bold]{profile.sid}[/bold]")
    t.add_row("[cyan]Friendly Name[/cyan]", getattr(profile, 'friendly_name', None) or "[i]N/A[/i]")
    t.add_row("[cyan]Status[/cyan]", status_style(getattr(profile, 'status', None)))
    t.add_row("[cyan]Type[/cyan]", getattr(profile, 'customer_profile_type', None) or "[i]N/A[/i]")
    t.add_row("[cyan]Email[/cyan]", getattr(profile, 'email', None) or "[i]N/A[/i]")
    t.add_row("[cyan]Created[/cyan]", str(getattr(profile, 'date_created', None)) if getattr(profile, 'date_created', None) else "[i]N/A[/i]")
    return Panel(t, title="Customer Profile", border_style="bright_blue", box=box.ROUNDED)


def render_entity_assignments(assignments, title="Entity Assignments"):
    if not assignments:
        return Panel("[i]None found[/i]", title=title, border_style="yellow", box=box.MINIMAL)
    table = Table(title=title, box=box.SIMPLE_HEAVY)
    table.add_column("Sid", style="dim", no_wrap=True)
    table.add_column("Object SID/ID", style="cyan")
    table.add_column("Object Type", style="magenta")
    table.add_column("Status/Note", style="white")
    for a in assignments:
        obj_sid = getattr(a, "object_sid", "") or getattr(a, "object_id", "") or ""
        obj_type = getattr(a, "object_type", "") or ""
        note = getattr(a, "status", "") or getattr(a, "note", "") or ""
        table.add_row(a.sid or "-", obj_sid or "-", obj_type or "-", note or "-")
    return table


def render_brand_table(brands, profile_sid):
    if not brands:
        return Panel("[i]No brands found[/i]", title="A2P Brands", border_style="yellow")
    table = Table(title="A2P Brands (filtered by profile)", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Brand SID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Status", style="white")
    table.add_column("CustomerProfileBundleSid", style="magenta")
    found = False
    for b in brands:
        # Brand resource fields vary; try multiple names that Twilio docs reference
        cust_sid = getattr(b, "customer_profile_bundle_sid", None) or getattr(b, "customer_profile_sid", None) or getattr(b, "customer_profile_bundle_sid", None)
        # If no filtering field exists, show all but mark which ones appear to reference the profile
        if cust_sid and cust_sid == profile_sid:
            found = True
        status = getattr(b, "status", None) or getattr(b, "registration_status", None) or "unknown"
        table.add_row(
            getattr(b, "sid", getattr(b, "brand_registration_sid", "-")),
            getattr(b, "brand_name", getattr(b, "brand", "[i]N/A[/i]")),
            status_style(status),
            str(cust_sid or "-"),
        )
    # If API doesn't expose a direct link, show a note.
    note = "[i]Note: filtering uses CustomerProfileBundleSid/CustomerProfileSid if present.[/i]"
    return Panel(Align(table, align="center"), title="A2P Brand Registrations", subtitle=note, border_style="bright_magenta")


def render_campaign_table(campaigns, profile_sid):
    if not campaigns:
        return Panel("[i]No campaigns found[/i]", title="A2P Campaigns", border_style="yellow")
    table = Table(title="A2P Campaign Registrations", box=box.MINIMAL)
    table.add_column("Campaign SID", style="cyan")
    table.add_column("Brand SID", style="magenta")
    table.add_column("Use Case", style="green")
    table.add_column("Status", style="white")
    matched = False
    for c in campaigns:
        brand_sid = getattr(c, "brand_registration_sid", None) or getattr(c, "brand_sid", None) or "-"
        status = getattr(c, "status", None) or "unknown"
        use_case = getattr(c, "use_case", None) or getattr(c, "campaign_use_case", None) or "-"
        table.add_row(getattr(c, "sid", "-"), brand_sid, use_case, status_style(status))
        # If campaign contains profile link via brand details (not always present), we can't reliably match; user should visually verify.
    return table


def render_messaging_services_table(services, profile_sid):
    if not services:
        return Panel("[i]No messaging services[/i]", title="Messaging Services", border_style="yellow")
    table = Table(title="Messaging Services (linked)", box=box.SIMPLE)
    table.add_column("Service SID", style="cyan")
    table.add_column("Name", style="bold")
    table.add_column("Customer Profile SID", style="magenta")
    table.add_column("A2P Campaign SID", style="green")
    for s in services:
        cust = getattr(s, "customer_profile_sid", None) or getattr(s, "customer_profile_bundle_sid", None) or "-"
        campaign = getattr(s, "a2p_campaign_id", None) or getattr(s, "a2p_campaign_sid", None) or "-"
        table.add_row(getattr(s, "sid", "-"), getattr(s, "friendly_name", getattr(s, "friendlyName", "-")), str(cust), str(campaign))
    return table


# -----------------------
# CLI commands
# -----------------------
@click.group()
def cli():
    """TrustHub Inspector — inspect Twilio TrustHub customer profiles and related compliance objects"""
    pass


@cli.command()
@click.argument("profile_sid", required=False)
def inspect(profile_sid):
    """
    Inspect a TrustHub customer profile. If PROFILE_SID is not provided, you'll be prompted.
    """
    try:
        if not profile_sid:
            profile_sid = console.input("[bold cyan]Enter Customer Profile SID > [/bold cyan]").strip()
            if not profile_sid:
                console.print("[red]No SID provided. Exiting.[/red]")
                return

        # Header
        console.print(f"Inspecting TrustHub Profile: [bold]{profile_sid}[/bold]")

        # Profile
        profile = fetch_customer_profile(profile_sid)
        console.print(render_profile_table(profile))

        # Entity assignments (supporting docs, end users)
        assignments = list_customer_entity_assignments(profile_sid)
        docs = [a for a in assignments if getattr(a, "object_type", "").lower().startswith("supportingdocument")]
        end_users = [a for a in assignments if getattr(a, "object_type", "").lower().startswith("enduser")]
        console.print(render_entity_assignments(docs, title="Supporting Documents"))
        console.print(render_entity_assignments(end_users, title="End Users / Assigned Entities"))

        # Channel endpoint assignments (phone numbers, SIP endpoints, etc)
        channel_assignments = list_channel_endpoint_assignments(profile_sid)
        console.print(render_entity_assignments(channel_assignments, title="Channel Endpoint Assignments"))

        # Messaging services
        services = [s for s in list_messaging_services() if (getattr(s, "customer_profile_sid", None) == profile_sid or getattr(s, "customer_profile_bundle_sid", None) == profile_sid)]
        console.print(render_messaging_services_table(services, profile_sid))

        # A2P Brands and Campaigns - we pull all and show ones that reference the profile (if the API returns that field)
        brands = list_a2p_brands(limit=200)
        console.print(render_brand_table(brands, profile_sid))

        campaigns = list_a2p_campaigns(limit=300)
        console.print(render_campaign_table(campaigns, profile_sid))

        # Subaccounts and their TrustHub status
        subaccounts = list_subaccounts(limit=200)
        console.print(render_subaccounts_table(subaccounts, profile_sid))

        console.print("-" * 50)

    except Exception as exc:
        console.print(f"[bold red]Error fetching profile or related resources:[/bold red] {exc}")


@cli.command()
@click.argument("profile_sid", required=False)
def delete(profile_sid):
    """
    Delete the customer profile permanently (irreversible).
    """
    try:
        if not profile_sid:
            profile_sid = console.input("[bold cyan]Enter Customer Profile SID to delete > [/bold cyan]").strip()
            if not profile_sid:
                console.print("[red]No SID provided. Exiting.[/red]")
                return

        # Fetch to display name
        profile = fetch_customer_profile(profile_sid)
        console.print(Panel(f"[bold]{profile.friendly_name}[/bold]\nSID: {profile.sid}\nStatus: {status_style(profile.status)}",
                            title="[red]Delete Confirmation[/red]", border_style="red"))

        confirm = Confirm.ask("[red]This action is permanent. Type 'yes' to confirm deletion[/red]", default=False)
        if confirm:
            client.trusthub.v1.customer_profiles(profile_sid).delete()
            console.print(f"[green]✅ Profile {profile_sid} deleted.[/green]")
        else:
            console.print("[yellow]Cancelled.[/yellow]")

    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")


@cli.command()
def list_profiles():
    """
    List all available customer profiles in your Twilio account.
    """
    try:
        console.print(f"Available TrustHub Customer Profiles:")
        
        profiles = list_customer_profiles(limit=100)
        
        if not profiles:
            console.print("[yellow]No customer profiles found in your account.[/yellow]")
            return
        
        table = Table(title="Customer Profiles", box=box.ROUNDED)
        table.add_column("SID", style="cyan", no_wrap=True)
        table.add_column("Friendly Name", style="bold")
        table.add_column("Status", style="white")
        table.add_column("Type", style="magenta")
        table.add_column("Email", style="yellow")
        
        for profile in profiles:
            # Debug: print available attributes
            if len(profiles) == 1:  # Only debug for first profile
                console.print(f"[dim]Debug - Available attributes: {dir(profile)}[/dim]")
                console.print(f"[dim]Debug - Profile data: {profile.__dict__}[/dim]")
            
            table.add_row(
                profile.sid,
                getattr(profile, 'friendly_name', '[i]N/A[/i]') or "[i]N/A[/i]",
                status_style(getattr(profile, 'status', None)),
                getattr(profile, 'customer_profile_type', '[i]N/A[/i]') or "[i]N/A[/i]",
                getattr(profile, 'email', '[i]N/A[/i]') or "[i]N/A[/i]"
            )
        
        console.print(table)
        console.print(f"[green]Found {len(profiles)} customer profile(s)[/green]")
        
    except Exception as exc:
        console.print(f"[bold red]Error listing customer profiles:[/bold red] {exc}")


@cli.command()
def subaccounts():
    """
    List all subaccounts and their TrustHub profile status.
    """
    try:
        console.print(f"Subaccounts & TrustHub Status:")
        
        subaccounts_list = list_subaccounts(limit=200)
        
        if not subaccounts_list:
            console.print("[yellow]No subaccounts found in your account.[/yellow]")
            return
        
        # Group by main account vs subaccounts
        main_account = None
        subaccounts_only = []
        
        for account in subaccounts_list:
            if account.sid == ACCOUNT_SID:
                main_account = account
            else:
                subaccounts_only.append(account)
        
        # Show main account info
        if main_account:
            main_table = Table(title="Main Account", box=box.ROUNDED)
            main_table.add_column("Field", style="cyan")
            main_table.add_column("Value", style="magenta")
            main_table.add_row("Account SID", main_account.sid)
            main_table.add_row("Friendly Name", main_account.friendly_name or "[i]N/A[/i]")
            main_table.add_row("Status", status_style(main_account.status))
            main_table.add_row("Type", "Main Account")
            console.print(main_table)
            console.print("")
        
        # Show subaccounts
        if subaccounts_only:
            console.print(f"[bold]Found {len(subaccounts_only)} subaccount(s):[/bold]")
            
            for subaccount in subaccounts_only:
                console.print(f"\n[bold cyan]Subaccount: {subaccount.friendly_name or subaccount.sid}[/bold cyan]")
                
                # Get TrustHub profiles for this subaccount
                sub_profiles = get_subaccount_trusthub_profiles(subaccount.sid)
                
                if sub_profiles:
                    sub_table = Table(title=f"TrustHub Profiles for {subaccount.friendly_name or subaccount.sid}", box=box.SIMPLE)
                    sub_table.add_column("SID", style="cyan")
                    sub_table.add_column("Friendly Name", style="bold")
                    sub_table.add_column("Status", style="white")
                    sub_table.add_column("Email", style="yellow")
                    
                    for profile in sub_profiles:
                        sub_table.add_row(
                            profile.sid,
                            getattr(profile, 'friendly_name', None) or "[i]N/A[/i]",
                            status_style(getattr(profile, 'status', None)),
                            getattr(profile, 'email', None) or "[i]N/A[/i]"
                        )
                    
                    console.print(sub_table)
                else:
                    console.print("[yellow]No TrustHub profiles found for this subaccount[/yellow]")
        else:
            console.print("[yellow]No subaccounts found[/yellow]")
        
        console.print("-" * 50)
        
    except Exception as exc:
        console.print(f"[bold red]Error listing subaccounts:[/bold red] {exc}")


def search_subaccount_by_number(account_number):
    """
    Search for a subaccount by its number (e.g., '239' from 'dev-company-239').
    Returns all subaccounts that contain that number.
    """
    try:
        subaccounts_list = list_subaccounts(limit=200)
        matching_subaccounts = []
        
        for subaccount in subaccounts_list:
            if subaccount.sid == ACCOUNT_SID:
                continue  # Skip main account
            
            # Extract number from friendly name (e.g., 'dev-company-239' -> '239')
            friendly_name = subaccount.friendly_name or ""
            if account_number in friendly_name:
                matching_subaccounts.append(subaccount)
        
        return matching_subaccounts
    except Exception as e:
        console.print(f"[yellow]Warning: Could not search subaccounts: {e}[/yellow]")
        return []


def render_subaccount_search_results(subaccounts, search_number):
    """Render search results for subaccount number search."""
    if not subaccounts:
        return Panel(f"[i]No subaccounts found containing number '{search_number}'[/i]", 
                    title=f"Search Results for '{search_number}'", border_style="yellow")
    
    table = Table(title=f"Subaccounts Containing '{search_number}'", box=box.ROUNDED)
    table.add_column("Account SID", style="cyan", no_wrap=True)
    table.add_column("Friendly Name", style="bold")
    table.add_column("Status", style="white")
    table.add_column("TrustHub Profiles", style="magenta")
    
    for subaccount in subaccounts:
        # Get TrustHub profiles for this subaccount
        sub_profiles = get_subaccount_trusthub_profiles(subaccount.sid)
        profile_count = len(sub_profiles) if sub_profiles else 0
        
        table.add_row(
            str(subaccount.sid),
            str(subaccount.friendly_name or "[i]N/A[/i]"),
            status_style(subaccount.status),
            str(profile_count)
        )
    
    return Panel(table, title=f"Search Results for '{search_number}'", border_style="bright_green")


@cli.command()
@click.argument("account_number")
def search_subaccount(account_number):
    """
    Search for subaccounts by account number (e.g., '239' from 'dev-company-239').
    
    ACCOUNT_NUMBER: The number to search for in subaccount names
    """
    try:
        console.print(f"Searching Subaccounts for Number: {account_number}")
        
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
                summary_table = Table(title="TrustHub Profile Status Summary", box=box.SIMPLE)
                summary_table.add_column("Status", style="white")
                summary_table.add_column("Count", style="magenta")
                
                for status, count in status_counts.items():
                    summary_table.add_row(status_style(status), str(count))
                
                console.print(summary_table)
                
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
        
        console.print("-" * 50)
        
    except Exception as exc:
        console.print(f"[bold red]Error searching subaccounts:[/bold red] {exc}")


if __name__ == "__main__":
    cli()
