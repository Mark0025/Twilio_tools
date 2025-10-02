# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Twilio CLI Tools - A comprehensive Python toolkit for managing Twilio services including TrustHub customer profiles, phone number analysis via PhoneInfoga integration, call log management, and compliance monitoring. Features an index-based CLI system for quick command access.

## Development Environment

### Python Environment Management

**CRITICAL**: This project uses `uv` for dependency management with a `.venv` virtual environment.

```bash
# Activate virtual environment (REQUIRED before any Python work)
source .venv/bin/activate

# Install/sync dependencies
uv sync

# Install in development mode
uv pip install -e .

# Verify environment is active
which python  # Should show: .venv/bin/python
```

**NEVER** use `uv run` - it doesn't properly activate the virtual environment and will cause import errors with Rich library components.

### Required Credentials

Create `.env` file in project root:
```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
```

## Build & Test Commands

```bash
# Activate environment first
source .venv/bin/activate

# Run tests
uv run pytest

# Code formatting
uv run black src/
uv run flake8 src/

# Run main CLI
python twilio_cli.py menu           # Interactive menu
python twilio_cli.py index          # Show all commands
python twilio_cli.py 9 239          # Execute command #9 with arg "239"

# Run specific tests
uv run pytest tests/test_specific.py -v
```

## Architecture & Key Concepts

### Index-Based CLI System

The CLI uses a unique **number-based command system** for quick access:
- Commands are indexed in `src/twilio_cli/cli_commands/cli_commands.json`
- Execute via: `python twilio_cli.py <index> [args...]`
- Example: `python twilio_cli.py 9 239` searches subaccounts for "239"

**Key Files:**
- `twilio_cli.py` - Root launcher script
- `src/twilio_cli/cli.py` - Main CLI implementation with command routing
- `src/twilio_cli/cli_commands/cli_commands.json` - Command index mapping

### Module Structure

```
src/twilio_cli/
├── __init__.py
├── main.py              # Entry point when imported as module
├── cli.py               # CLI command implementation (~2000 lines)
├── api/
│   └── trusthub_inspector.py  # TrustHub API integration (~600 lines)
├── utils/
│   ├── call_log.py            # Call log analysis
│   └── twilio_error_map.json  # Error code reference (3MB)
├── cli_commands/
│   └── cli_commands.json      # Command index (20 commands)
├── core/                      # Core business logic
└── tools/                     # Tool integrations
```

### TrustHub Inspector Architecture

Located in `src/twilio_cli/api/trusthub_inspector.py`:
- **Fetch Functions**: `fetch_customer_profile()`, `list_customer_profiles()`, `list_subaccounts()`
- **Rendering Functions**: `render_profile_table()`, `render_subaccounts_table()`, `status_style()`
- **Search Functions**: `search_subaccount_by_number()`, `get_subaccount_trusthub_profiles()`

**Data Flow**: Twilio API → Fetch Functions → Rendering Functions → Rich Console Output

**Safe Attribute Access Pattern**: Always use `getattr(obj, 'attribute', default)` for Twilio API objects as field availability varies.

### Rich Library Integration

**CRITICAL**: Box constants must be imported and used correctly:

```python
from rich import box  # REQUIRED import

# CORRECT
table = Table(box=box.ROUNDED)
panel = Panel(content, box=box.SIMPLE)

# WRONG - causes "str object has no attribute 'substitute'" error
table = Table(box="round")
```

Standard pattern:
```python
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()
```

## PhoneInfoga Integration

PhoneInfoga tools live in `tools/PhoneInfoga/` (Go-based).

**Requirements**:
- Go installed
- PhoneInfoga binary or source in tools directory

**Commands** (indices 15-19):
- `15` - Scan phone number
- `16` - Start web server
- `17` - Version info
- `18` - List scanners

**Check availability**: `check_phone_infoga_available()` in `cli.py`

## Common Development Patterns

### Adding a New CLI Command

1. Add to `src/twilio_cli/cli_commands/cli_commands.json`:
```json
{
  "21": {
    "name": "new-command",
    "description": "Description of command",
    "command": "new-command",
    "args": ["arg1", "arg2"],
    "category": "CategoryName"
  }
}
```

2. Implement in `src/twilio_cli/cli.py`:
```python
@cli.command("new-command")
@click.argument("arg1")
@click.argument("arg2")
def new_command(arg1, arg2):
    """Command implementation."""
    # Implementation here
```

### Creating Rich Tables

```python
table = Table(title="Title", box=box.ROUNDED)
table.add_column("Column Name", style="cyan", no_wrap=True)
table.add_row("value1", "value2")
console.print(table)
```

### Status Color Coding

Use `status_style()` function for consistent status display:
- Green: APPROVED, ACTIVE, REGISTERED, COMPLETED
- Yellow: PENDING, IN_REVIEW, SUBMITTED
- Red: FAILED, REJECTED, DENIED, SUSPENDED

## Troubleshooting Guide

### Import Errors
**Solution**: Activate virtual environment first:
```bash
source .venv/bin/activate
which python  # Verify .venv is active
```

### "str object has no attribute 'substitute'"
**Cause**: Using string values instead of box constants
**Solution**: Change `box="round"` to `box=box.ROUNDED` and add `from rich import box`

### Rich Components Not Rendering
**Cause**: Virtual environment not activated or wrong Python path
**Solution**:
```bash
source .venv/bin/activate
python -c "import rich; print(rich.__file__)"  # Should show .venv path
```

### Twilio API Errors
**Cause**: Missing or invalid credentials
**Solution**: Check `.env` file has valid `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`

## Project-Specific Conventions

### Logging
- Uses `loguru` library
- Logs to: `applogs/app.log` and `tests/logs/test.log`
- Auto-rotation at 1MB, 10-day retention

### Error Handling
- All Twilio API calls wrapped in try-except
- Use `console.print("[yellow]Warning:...")` for warnings
- Use `console.print("[bold red]Error:...")` for errors

### File Locations
- CSV uploads: `uploads/` directory
- Application logs: `applogs/` directory
- Test logs: `tests/logs/` directory

### Code Style
- Python 3.12+ required
- Line length: 88 characters (Black default)
- Use type hints where possible
- Follow PEP 8 guidelines

## Recent Feature: Calendar Integration

The project includes Microsoft Calendar integration for VAPI appointment booking (see git history for `calendar` related commits). Files may include `.ics` data handling and user ID management.
