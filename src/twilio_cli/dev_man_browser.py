#!/usr/bin/env python3
"""
Dev_Man Browser - Interactive interface for viewing project plans, diagrams, and stats
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.tree import Tree
from rich import box
from rich.layout import Layout
from rich.columns import Columns

console = Console()

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
DEV_MAN_DIR = BASE_DIR / "Dev_Man"
PLANS_DIR = DEV_MAN_DIR / "plans"


class DevManBrowser:
    """Browser for Dev_Man documentation and project stats."""

    def __init__(self):
        self.plans = {
            "completed": [],
            "current": [],
            "pending": []
        }
        self.stats = {}
        self._load_plans()
        self._calculate_stats()

    def _load_plans(self):
        """Load all plan files from Dev_Man directory."""
        for category in ["completed", "current", "pending"]:
            plan_dir = PLANS_DIR / category
            if plan_dir.exists():
                self.plans[category] = list(plan_dir.glob("*.md"))

    def _calculate_stats(self):
        """Calculate project statistics."""
        src_dir = BASE_DIR / "src" / "twilio_cli"

        # Count Python files
        py_files = list(src_dir.rglob("*.py"))

        # Count lines of code
        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r') as f:
                    total_lines += len(f.readlines())
            except:
                pass

        # Count commands
        cli_commands_file = src_dir / "cli_commands" / "cli_commands.json"
        total_commands = 0
        if cli_commands_file.exists():
            with open(cli_commands_file, 'r') as f:
                commands_data = json.load(f)
                total_commands = len(commands_data.get("commands", {}))

        self.stats = {
            "py_files": len(py_files),
            "total_lines": total_lines,
            "total_commands": total_commands,
            "completed_plans": len(self.plans["completed"]),
            "current_plans": len(self.plans["current"]),
            "pending_plans": len(self.plans["pending"]),
            "completion_rate": self._calculate_completion_rate()
        }

    def _calculate_completion_rate(self) -> float:
        """Calculate project completion rate."""
        total_plans = sum(len(plans) for plans in self.plans.values())
        if total_plans == 0:
            return 0.0
        return (len(self.plans["completed"]) / total_plans) * 100

    def show_dashboard(self):
        """Show main Dev_Man dashboard with stats and overview."""
        console.clear()

        # Header
        header = Panel(
            "[bold cyan]Dev_Man Dashboard[/bold cyan]\n"
            "[dim]Project Planning & Development Overview[/dim]",
            border_style="bright_blue",
            box=box.DOUBLE
        )
        console.print(header)
        console.print()

        # Stats Panel
        stats_table = Table.grid(expand=True)
        stats_table.add_column(justify="right", ratio=40)
        stats_table.add_column(justify="left", ratio=60)

        stats_table.add_row("[cyan]Python Files[/cyan]", f"[bold]{self.stats['py_files']}[/bold]")
        stats_table.add_row("[cyan]Lines of Code[/cyan]", f"[bold]{self.stats['total_lines']:,}[/bold]")
        stats_table.add_row("[cyan]CLI Commands[/cyan]", f"[bold]{self.stats['total_commands']}[/bold]")
        stats_table.add_row()
        stats_table.add_row("[cyan]Completed Plans[/cyan]", f"[green]{self.stats['completed_plans']}[/green]")
        stats_table.add_row("[cyan]Current Plans[/cyan]", f"[yellow]{self.stats['current_plans']}[/yellow]")
        stats_table.add_row("[cyan]Pending Plans[/cyan]", f"[dim]{self.stats['pending_plans']}[/dim]")
        stats_table.add_row()
        stats_table.add_row(
            "[cyan]Completion Rate[/cyan]",
            f"[bold green]{self.stats['completion_rate']:.1f}%[/bold green]"
        )

        stats_panel = Panel(
            stats_table,
            title="[bold]Project Statistics[/bold]",
            border_style="green",
            box=box.ROUNDED
        )
        console.print(stats_panel)
        console.print()

        # Plans Overview
        self._show_plans_tree()

    def _show_plans_tree(self):
        """Show plans organized in a tree structure."""
        tree = Tree(
            "[bold]📋 Development Plans[/bold]",
            guide_style="bright_blue"
        )

        # Completed
        completed_branch = tree.add("[green]✅ Completed[/green]")
        for plan in self.plans["completed"]:
            completed_branch.add(f"[dim]{plan.stem}[/dim]")

        # Current
        current_branch = tree.add("[yellow]🚧 In Progress[/yellow]")
        for plan in self.plans["current"]:
            current_branch.add(f"[bold]{plan.stem}[/bold]")

        # Pending
        pending_branch = tree.add("[dim]⏳ Pending[/dim]")
        for plan in self.plans["pending"]:
            pending_branch.add(f"[dim]{plan.stem}[/dim]")

        console.print(Panel(tree, border_style="cyan", box=box.SIMPLE))

    def list_plans(self, category: str = "all"):
        """List all plans in a category."""
        console.clear()

        categories_to_show = []
        if category == "all":
            categories_to_show = ["completed", "current", "pending"]
        else:
            categories_to_show = [category]

        for cat in categories_to_show:
            if cat not in self.plans:
                continue

            # Style based on category
            styles = {
                "completed": ("green", "✅"),
                "current": ("yellow", "🚧"),
                "pending": ("dim", "⏳")
            }
            style, icon = styles.get(cat, ("white", "📄"))

            table = Table(
                title=f"{icon} {cat.capitalize()} Plans",
                box=box.ROUNDED,
                border_style=style
            )
            table.add_column("#", style="dim", width=3)
            table.add_column("Plan Name", style="bold")
            table.add_column("Path", style="dim")

            for idx, plan in enumerate(self.plans[cat], 1):
                table.add_row(
                    str(idx),
                    plan.stem.replace("-", " ").title(),
                    str(plan.relative_to(BASE_DIR))
                )

            if self.plans[cat]:
                console.print(table)
                console.print()

    def view_plan(self, category: str, index: int):
        """View a specific plan file."""
        if category not in self.plans or index >= len(self.plans[category]):
            console.print("[red]Invalid plan selection[/red]")
            return

        plan_file = self.plans[category][index]

        console.clear()

        # Header
        header = Panel(
            f"[bold]{plan_file.stem}[/bold]\n[dim]{plan_file.relative_to(BASE_DIR)}[/dim]",
            border_style="bright_blue"
        )
        console.print(header)
        console.print()

        # Read and display markdown content
        try:
            with open(plan_file, 'r') as f:
                content = f.read()

            # Display as markdown
            md = Markdown(content)
            console.print(Panel(md, border_style="cyan", box=box.ROUNDED))

        except Exception as e:
            console.print(f"[red]Error reading plan: {e}[/red]")

    def search_plans(self, query: str):
        """Search for plans containing a query string."""
        console.clear()

        results = []

        for category in ["completed", "current", "pending"]:
            for plan in self.plans[category]:
                # Search in filename
                if query.lower() in plan.stem.lower():
                    results.append((category, plan, "filename"))
                    continue

                # Search in content
                try:
                    with open(plan, 'r') as f:
                        content = f.read()
                        if query.lower() in content.lower():
                            results.append((category, plan, "content"))
                except:
                    pass

        if not results:
            console.print(f"[yellow]No plans found matching '{query}'[/yellow]")
            return

        # Display results
        table = Table(
            title=f"🔍 Search Results for '{query}'",
            box=box.ROUNDED,
            border_style="cyan"
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Category", style="cyan")
        table.add_column("Plan", style="bold")
        table.add_column("Match", style="dim")

        for idx, (category, plan, match_type) in enumerate(results, 1):
            table.add_row(
                str(idx),
                category.capitalize(),
                plan.stem,
                match_type
            )

        console.print(table)

    def show_mermaid_diagrams(self):
        """Show available Mermaid diagrams (if any)."""
        console.clear()

        # Search for mermaid diagrams in markdown files
        diagrams = []

        for category in ["completed", "current", "pending"]:
            for plan in self.plans[category]:
                try:
                    with open(plan, 'r') as f:
                        content = f.read()
                        if "```mermaid" in content or "```mmd" in content:
                            diagrams.append((category, plan))
                except:
                    pass

        if not diagrams:
            console.print(
                Panel(
                    "[yellow]No Mermaid diagrams found in plans[/yellow]\n\n"
                    "[dim]Add diagrams to your markdown files using:[/dim]\n"
                    "```mermaid\ngraph TD\n  A --> B\n```",
                    title="📊 Mermaid Diagrams",
                    border_style="yellow"
                )
            )
            return

        # Display diagram list
        table = Table(
            title="📊 Available Diagrams",
            box=box.ROUNDED,
            border_style="cyan"
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Plan", style="bold")
        table.add_column("Category", style="cyan")

        for idx, (category, plan) in enumerate(diagrams, 1):
            table.add_row(
                str(idx),
                plan.stem,
                category.capitalize()
            )

        console.print(table)
        console.print()
        console.print(
            "[dim]Tip: View these files directly to see Mermaid diagrams in your editor[/dim]"
        )


def main():
    """Main entry point for Dev_Man browser."""
    browser = DevManBrowser()
    browser.show_dashboard()


if __name__ == "__main__":
    main()
