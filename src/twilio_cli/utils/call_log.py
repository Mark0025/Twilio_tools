import csv
import json
from typing import List, Dict, Optional
from rich.table import Table
from rich.console import Console
from difflib import get_close_matches
from datetime import datetime

console = Console()

class CallLogEntry:
    """
    Represents a single Twilio call log entry with dunder methods for pretty output and validation.
    """
    def __init__(self, data: Dict):
        self.data = data
        self.call_sid = data.get("Call Sid")
        self.account_sid = data.get("Account Sid")
        self.start_time = data.get("Start Time")
        self.end_time = data.get("End Time")
        self.duration = int(data.get("Duration", 0))
        self.from_number = data.get("From")
        self.to = data.get("To")
        self.direction = data.get("Direction")
        self.status = data.get("Status")
        self.error_code = data.get("Error Code", "")
        self.date_created = data.get("Date Created")
        # Add more fields as needed

    def __str__(self):
        return f"Call {self.call_sid} from {self.from_number} to {self.to} ({self.status})"

    def __repr__(self):
        return json.dumps(self.data, indent=2)

    def to_dict(self):
        return self.data

    def to_json(self):
        return json.dumps(self.data)

class CallLogBook:
    """
    Manages a collection of CallLogEntry objects, supports loading from CSV, exporting to JSON,
    pretty-printing, fuzzy finding, and command history.
    """
    def __init__(self):
        self.entries: List[CallLogEntry] = []
        self.history: List[str] = []  # Command history

    def load_from_csv(self, csv_path: str):
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.entries = [CallLogEntry(row) for row in reader]
        console.print(f"[green]Loaded {len(self.entries)} call log entries from {csv_path}[/green]")

    def export_to_json(self, json_path: str):
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump([e.to_dict() for e in self.entries], f, indent=2)
        console.print(f"[cyan]Exported call log data to {json_path}[/cyan]")

    def pretty_print(self, limit: Optional[int] = 10):
        table = Table(title="Twilio Call Logs")
        table.add_column("#", style="dim")
        table.add_column("From")
        table.add_column("To")
        table.add_column("Status")
        table.add_column("Duration (s)")
        table.add_column("Date Created")
        for idx, entry in enumerate(self.entries[:limit]):
            table.add_row(
                str(idx+1),
                entry.from_number or "",
                entry.to or "",
                entry.status or "",
                str(entry.duration),
                entry.date_created or ""
            )
        console.print(table)

    def fuzzy_find(self, query: str, field: str = "To", n: int = 3):
        values = [getattr(e, field, "") for e in self.entries]
        matches = get_close_matches(query, values, n=n)
        return [e for e in self.entries if getattr(e, field, "") in matches]

    def add_history(self, command: str):
        self.history.append(command)

    def show_history(self):
        for idx, cmd in enumerate(self.history, 1):
            console.print(f"[yellow]{idx}.[/yellow] {cmd}")

    # --- API Endpoint Mapping Utility (for future FastAPI integration) ---
    # def map_to_api(self):
    #     """
    #     For every CLI report/action, define a corresponding FastAPI endpoint signature.
    #     Example:
    #     @app.get("/call-logs/{call_sid}")
    #     def get_call_log(call_sid: str):
    #         ...
    #     """
    #     pass

# Example usage (to be used in CLI or tests):
# logbook = CallLogBook()
# logbook.load_from_csv('src/uploads/call-log-....csv')
# logbook.pretty_print()
# logbook.export_to_json('tests/call_logs.json')
# matches = logbook.fuzzy_find('+1816')
# logbook.add_history('show summary')
# logbook.show_history() 