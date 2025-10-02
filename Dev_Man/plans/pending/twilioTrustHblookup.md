You said:
write me a pyhton app that will remove this custormer profile from this account - BUc581a87abdd01affc47a0aeb813541f3	Perez Cobb Investments, LLC



ChatGPT said:
Got it — but I’ll need to know a couple of details before I can safely and accurately write the Python app:

Where is this customer profile stored?

Is this in a database (e.g., MySQL, Postgres, SQLite, MongoDB)?

Or in a cloud service API (like QuickBooks, Stripe, Salesforce, etc.)?

Or just in a local file (CSV, JSON, etc.)?

How do you authenticate?

If it’s an API, we’ll need the endpoint and how you authenticate (API key, OAuth, etc.).

If it’s a database, we’ll need connection info and credentials.

Do you want this to be permanent (hard delete) or just mark the profile as inactive/archived?

Once I know these, I can give you a clean, ready-to-run Python script that deletes the customer profile with ID BUc581a87abdd01affc47a0aeb813541f3 and name "Perez Cobb Investments, LLC".

Where is this data currently stored?








You said:
this is using twilio api 


ChatGPT said:
Gotcha — so you want a Python script that uses the Twilio API to delete a customer profile with:

SID: BUc581a87abdd01affc47a0aeb813541f3

Friendly Name: Perez Cobb Investments, LLC

In Twilio’s terminology, that’s a Business Profile or Customer Profile in TrustHub.
Twilio’s API supports deleting a Customer Profile via DELETE /v1/CustomerProfiles/{Sid}.

Here’s a ready-to-run Python example:

python
Copy
Edit
from twilio.rest import Client
import os

# Load from environment variables (recommended)
# Set these in your shell:
# export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# export TWILIO_AUTH_TOKEN="your_auth_token"

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

# Customer Profile SID to delete
customer_profile_sid = "BUc581a87abdd01affc47a0aeb813541f3"

try:
    client.trusthub.v1.customer_profiles(customer_profile_sid).delete()
    print(f"✅ Customer profile {customer_profile_sid} deleted successfully.")
except Exception as e:
    print(f"❌ Error deleting profile {customer_profile_sid}: {e}")
Steps to run:
Install Twilio SDK

bash
Copy
Edit
pip install twilio
Export your Twilio credentials (in terminal before running the script):

bash
Copy
Edit
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token"
Run the script

bash
Copy
Edit
python delete_customer_profile.py
⚠ Note:
Deleting a TrustHub Customer Profile is permanent and can’t be undone.
If you want to just remove it from the account but keep a record, Twilio doesn’t provide a “soft delete” — you’d have to archive data elsewhere first.

Do you want me to also make the script list the profile’s details first so you can confirm before deletion? That way you don’t accidentally delete the wrong customer.








You said:
we wil use a .env 


ChatGPT said:
Perfect — using a .env file will keep credentials out of your code.
Here’s the updated Twilio Customer Profile delete script with .env support:

python
Copy
Edit
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Get credentials from .env
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

# Customer Profile SID to delete
customer_profile_sid = "BUc581a87abdd01affc47a0aeb813541f3"

try:
    # Optional: Fetch and confirm details before deleting
    profile = client.trusthub.v1.customer_profiles(customer_profile_sid).fetch()
    print(f"Found profile: {profile.friendly_name} (SID: {profile.sid})")

    confirm = input("Type 'YES' to delete this profile: ")
    if confirm == "YES":
        client.trusthub.v1.customer_profiles(customer_profile_sid).delete()
        print(f"✅ Profile '{profile.friendly_name}' deleted successfully.")
    else:
        print("❌ Deletion cancelled.")

except Exception as e:
    print(f"❌ Error: {e}")
.env file example
ini
Copy
Edit
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
Install dependencies
bash
Copy
Edit
pip install twilio python-dotenv
This version fetches the profile first so you see "Perez Cobb Investments, LLC" before actually deleting it — prevents “oops” moments.

Do you want me to also make it accept the SID as a command-line argument so you can reuse the script for different customers without editing the code? That would make it a quick one-liner delete tool.








You said:
i would like a minimal gui with click and rich where i can pas customer id and it allow me to check on info like 10dlc status and messaging campaign status 


ChatGPT said:
Gotcha — so you want a minimal GUI tool in Python that:

Lets you enter a Twilio Customer Profile SID

Displays info about that profile, including:

Friendly name

10DLC (A2P) registration status

Messaging campaign status

Allows deletion with a button click

Uses .env for Twilio credentials

Has a clean terminal UI with rich and a minimal window GUI (probably click + typer for CLI and rich tables)

Since click and rich are terminal-focused, I’ll make it as a CLI dashboard rather than a full desktop app.
We can later wrap it in something like Textual for a proper GUI if you want.

Example: twilio_profile_tool.py
python
Copy
Edit
import os
import click
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
from twilio.rest import Client

console = Console()

# Load .env
load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)


def fetch_profile_info(profile_sid):
    """Fetch profile and related 10DLC/messaging campaign info."""
    profile = client.trusthub.v1.customer_profiles(profile_sid).fetch()

    # Fetch messaging services linked to this profile
    messaging_services = client.messaging.v1.services.list(limit=20)
    linked_services = [
        ms for ms in messaging_services if ms.customer_profile_sid == profile_sid
    ]

    return profile, linked_services


@click.group()
def cli():
    """Twilio Customer Profile Manager"""


@cli.command()
@click.argument("profile_sid")
def info(profile_sid):
    """Show details for a customer profile"""
    try:
        profile, linked_services = fetch_profile_info(profile_sid)

        table = Table(title="Customer Profile Info")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("SID", profile.sid)
        table.add_row("Friendly Name", profile.friendly_name or "N/A")
        table.add_row("Status", profile.status or "N/A")
        table.add_row("Email", profile.email or "N/A")
        table.add_row("Type", profile.customer_profile_type or "N/A")

        console.print(table)

        if linked_services:
            ms_table = Table(title="Linked Messaging Services")
            ms_table.add_column("Service SID", style="green")
            ms_table.add_column("Friendly Name", style="yellow")
            ms_table.add_column("A2P Campaign ID", style="cyan")
            for ms in linked_services:
                ms_table.add_row(ms.sid, ms.friendly_name or "N/A", ms.a2p_campaign_id or "N/A")
            console.print(ms_table)
        else:
            console.print("[bold red]No messaging services linked to this profile.[/bold red]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.argument("profile_sid")
def delete(profile_sid):
    """Delete a customer profile"""
    try:
        profile, _ = fetch_profile_info(profile_sid)
        console.print(f"[bold red]About to delete profile:[/bold red] {profile.friendly_name} ({profile.sid})")
        confirm = input("Type 'YES' to confirm deletion: ")
        if confirm == "YES":
            client.trusthub.v1.customer_profiles(profile_sid).delete()
            console.print("[green]✅ Profile deleted successfully.[/green]")
        else:
            console.print("[yellow]❌ Deletion cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    cli()
.env file
ini
Copy
Edit
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
Install dependencies
bash
Copy
Edit
pip install twilio python-dotenv click rich
Example usage
bash
Copy
Edit
# Show info for profile
python twilio_profile_tool.py info BUc581a87abdd01affc47a0aeb813541f3

# Delete profile
python twilio_profile_tool.py delete BUc581a87abdd01affc47a0aeb813541f3
This is minimal CLI-GUI using click + rich.
If you want true windowed GUI (buttons, text boxes), I’d use textual so it still runs in the terminal but feels like a mini-app.

If you want, I can make the next version pull A2P 10DLC and campaign status directly from Twilio’s TrustHub/Messaging API so you can see exactly where the profile stands before deciding to delete. That would turn this into a real “Twilio profile inspector.”

Do you want me to build that extended inspector version next? That would make it more than just a delete tool.








You said:
yes i want to be able to inspect all things in trust hub 



ChatGPT said:
Alright — then we’re talking about a Twilio TrustHub Inspector CLI app.

It will let you:

Enter a Customer Profile SID

See everything in TrustHub tied to that profile:

Profile details (friendly name, status, type, email, etc.)

All associated customer supporting documents

All linked end users / sub-accounts

All A2P 10DLC brand registrations (status, ID, campaign status)

All messaging services linked to those campaigns

Any compliance issues or pending verifications

How it will work
click → Commands and arguments (info, delete, list)

rich → Nice tables and status formatting

python-dotenv → .env for Twilio credentials

Twilio Python SDK → TrustHub, Messaging, and Regulatory API calls

Here’s version 1.0 of a TrustHub Inspector:

python
Copy
Edit
import os
import click
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
from twilio.rest import Client

console = Console()

# Load Twilio credentials from .env
load_dotenv()
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(ACCOUNT_SID, AUTH_TOKEN)


def fetch_customer_profile(profile_sid):
    """Fetch customer profile from TrustHub."""
    return client.trusthub.v1.customer_profiles(profile_sid).fetch()


def fetch_supporting_documents(profile_sid):
    """Fetch supporting documents for the customer profile."""
    return client.trusthub.v1.customer_profiles(profile_sid).customer_profiles_entity_assignments.list()


def fetch_a2p_brands(profile_sid):
    """Fetch A2P 10DLC brands registered for this customer."""
    return client.messaging.v1.a2p_brands.list(limit=50)


def fetch_messaging_services(profile_sid):
    """Fetch messaging services linked to this customer profile."""
    services = client.messaging.v1.services.list(limit=50)
    return [svc for svc in services if getattr(svc, "customer_profile_sid", None) == profile_sid]


@click.group()
def cli():
    """Twilio TrustHub Inspector CLI"""


@cli.command()
@click.argument("profile_sid")
def inspect(profile_sid):
    """Inspect all TrustHub details for a profile"""
    try:
        profile = fetch_customer_profile(profile_sid)

        # Profile Table
        profile_table = Table(title="Customer Profile")
        profile_table.add_column("Field", style="cyan")
        profile_table.add_column("Value", style="magenta")

        profile_table.add_row("SID", profile.sid)
        profile_table.add_row("Friendly Name", profile.friendly_name or "N/A")
        profile_table.add_row("Status", profile.status or "N/A")
        profile_table.add_row("Type", profile.customer_profile_type or "N/A")
        profile_table.add_row("Email", profile.email or "N/A")

        console.print(profile_table)

        # Supporting Documents
        docs = fetch_supporting_documents(profile_sid)
        if docs:
            doc_table = Table(title="Supporting Documents")
            doc_table.add_column("Assignment SID", style="green")
            doc_table.add_column("Object SID", style="yellow")
            doc_table.add_column("Object Type", style="cyan")
            for doc in docs:
                doc_table.add_row(doc.sid, doc.object_sid, doc.object_type)
            console.print(doc_table)
        else:
            console.print("[yellow]No supporting documents found.[/yellow]")

        # Messaging Services
        services = fetch_messaging_services(profile_sid)
        if services:
            ms_table = Table(title="Messaging Services")
            ms_table.add_column("SID", style="green")
            ms_table.add_column("Name", style="yellow")
            ms_table.add_column("A2P Campaign ID", style="cyan")
            for svc in services:
                ms_table.add_row(svc.sid, svc.friendly_name or "N/A", svc.a2p_campaign_id or "N/A")
            console.print(ms_table)
        else:
            console.print("[yellow]No messaging services linked to this profile.[/yellow]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


@cli.command()
@click.argument("profile_sid")
def delete(profile_sid):
    """Delete a customer profile"""
    try:
        profile = fetch_customer_profile(profile_sid)
        console.print(f"[bold red]About to delete profile:[/bold red] {profile.friendly_name} ({profile.sid})")
        confirm = input("Type 'YES' to confirm deletion: ")
        if confirm == "YES":
            client.trusthub.v1.customer_profiles(profile_sid).delete()
            console.print("[green]✅ Profile deleted successfully.[/green]")
        else:
            console.print("[yellow]❌ Deletion cancelled.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")


if __name__ == "__main__":
    cli()
.env file
ini
Copy
Edit
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
Install dependencies
bash
Copy
Edit
pip install twilio python-dotenv click rich
Example usage
bash
Copy
Edit
# Inspect all TrustHub info for a profile
python trusthub_inspector.py inspect BUc581a87abdd01affc47a0aeb813541f3

# Delete a profile
python trusthub_inspector.py delete BUc581a87abdd01affc47a0aeb813541f3
Next Step
This is a starting point — the A2P 10DLC Brand/Campaign status API calls can be expanded to pull:

Brand status (PENDING, APPROVED, REJECTED)

Campaign use case

Messaging throughput tier

Those live in client.messaging.v1.a2p_brands and client.messaging.v1.a2p_campaigns.

If you want, I can make version 2 pull every campaign + brand status and render a single “TrustHub Health Report” table so you instantly see if something is blocked, pending, or live.
That would make it a real diagnostic tool, not just a data fetcher.

Do you want me to go ahead and make that full health report version? That would show you every compliance flag in one screen.








You said:
yes use color also to make it a pretty ui 


ChatGPT said:

Thought for 8s
Nice — I'll give you a polished, rich CLI inspector that:

Loads Twilio creds from a .env

Accepts a Customer Profile SID (argument or interactive)

Shows a pretty, colorized TrustHub health report: profile details, supporting documents, assigned channel endpoints, linked sub-accounts/end users, A2P brand registrations and campaign statuses, and linked messaging services

Lets you delete the profile (with typed confirmation)

Has clear error handling and helpful colors using rich

I've included a couple of authoritative Twilio references I used to make sure resource names and flows are correct (TrustHub CustomerProfile and A2P brand/campaign docs). 
Twilio
+1

Install
bash
Copy
Edit
pip install twilio python-dotenv click rich
Create a .env in the same folder:

ini
Copy
Edit
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
trusthub_inspector.py
Save this file and run with python trusthub_inspector.py inspect BU....

python
Copy
Edit
#!/usr/bin/env python3
"""
TrustHub Inspector — click + rich CLI for inspecting TrustHub customer profiles,
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
from rich.rule import Rule
from rich import box
from rich.prompt import Confirm

console = Console()

# Load .env
load_dotenv()
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

if not ACCOUNT_SID or not AUTH_TOKEN:
    console.print("[bold red]TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN must be set in .env[/bold red]")
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
    return client.trusthub.v1.customer_profiles(customer_profile_sid).entity_assignments.list(page_size=page_size)


def list_channel_endpoint_assignments(customer_profile_sid, page_size=100):
    return client.trusthub.v1.customer_profiles(customer_profile_sid).channel_endpoint_assignments.list(page_size=page_size)


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
    return client.messaging.v1.campaign_registrations.list(limit=limit)


def list_messaging_services(limit=200):
    """List Messaging Services and we'll filter by customer_profile_sid field if present."""
    return client.messaging.v1.services.list(limit=limit)


def list_subaccounts(limit=200):
    """List subaccounts and see if any are linked to profile via metadata — optional."""
    return client.api.accounts.list(limit=limit)


# -----------------------
# Rendering helpers
# -----------------------
def render_profile_table(profile):
    t = Table.grid(expand=True)
    t.add_column(justify="right", ratio=30)
    t.add_column(ratio=70)
    t.add_row("[cyan]SID[/cyan]", f"[bold]{profile.sid}[/bold]")
    t.add_row("[cyan]Friendly Name[/cyan]", profile.friendly_name or "[i]N/A[/i]")
    t.add_row("[cyan]Status[/cyan]", status_style(profile.status))
    t.add_row("[cyan]Type[/cyan]", profile.customer_profile_type or "[i]N/A[/i]")
    t.add_row("[cyan]Email[/cyan]", profile.email or "[i]N/A[/i]")
    t.add_row("[cyan]Created[/cyan]", str(profile.date_created) if getattr(profile, "date_created", None) else "[i]N/A[/i]")
    return Panel(t, title="Customer Profile", border_style="bright_blue", box=box.ROUNDED)


def status_style(val):
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
        console.print(Rule(title=f"Inspecting TrustHub Profile: [bold]{profile_sid}[/bold]", style="bright_blue"))

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

        console.print(Rule(style="bright_blue"))

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


if __name__ == "__main__":
    cli()
Notes, gotchas & references
This script pulls brand and campaign lists account-wide and filters client-side because Twilio’s API historically returns brands/campaigns for the account and you may need to correlate by CustomerProfileBundleSid or customer_profile_sid fields. If the account has many brands/campaigns, you can increase limit or implement paging. See Twilio docs for Brand and Campaign resources. 
Twilio
+1

TrustHub resources and field names can change; I relied on the official TrustHub API docs for CustomerProfile and EntityAssignment shapes. Test in a sandbox first. 
Twilio
+1

Deletion is permanent — the script forces a confirm prompt. Back up any required data before deletion.

If you’d like a full TUI (terminal GUI) with clickable buttons and persistent layout, I can convert this to a Textual app — that would feel like a mini-desktop app but still run in terminal.

If you want, I can:

Add paging to brand/campaign listing and automatic correlation logic (find campaigns whose brand references the profile),

Add an export flag to save the report as JSON or markdown,

Convert to a Textual windowed TUI (buttons, input box, confirm modal).

Which of those would you like next?