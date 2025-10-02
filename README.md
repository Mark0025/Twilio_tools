# Twilio CLI Tools

A comprehensive toolkit for managing Twilio services, including TrustHub customer profiles, phone number analysis, call log management, and more.

## 🚀 Features

- **TrustHub Inspector**: Manage customer profiles, subaccounts, and compliance
- **PhoneInfoga Integration**: Phone number lookup and analysis tools
- **Call Log Analysis**: Analyze and visualize call data
- **Error Code Lookup**: Comprehensive Twilio error code explanations
- **Index-Based CLI**: Simple number-based command execution
- **Rich Terminal UI**: Beautiful, color-coded output with tables and panels

## 📦 Installation

### Prerequisites

- Python 3.12+
- Go (for PhoneInfoga tools)
- Twilio account with API credentials

### Setup

1. **Clone the repository**:

   ```bash
   git clone <your-repo-url>
   cd twilio
   ```

2. **Install dependencies**:

   ```bash
   uv sync
   ```

3. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your Twilio credentials
   ```

4. **Install the package** (optional):
   ```bash
   uv pip install -e .
   ```

## 🎯 Quick Start

### Using the Index-Based CLI

The CLI provides a simple number-based system for quick access to all tools:

```bash
# Show all available commands
python twilio_cli.py index

# Execute commands by number
python twilio_cli.py 9 239          # Search subaccount for '239'
python twilio_cli.py 15 +1234567890 # Scan phone number with PhoneInfoga
python twilio_cli.py 6               # List TrustHub profiles
```

### Interactive Menu

For a guided experience:

```bash
python twilio_cli.py menu
```

### Direct Command Access

```bash
# TrustHub commands
python twilio_cli.py list-profiles
python twilio_cli.py search-subaccount 239
python twilio_cli.py profile-health-check

# PhoneInfoga commands
python twilio_cli.py phone-infoga-scan +1234567890
python twilio_cli.py phone-infoga-serve

# Call log analysis
python twilio_cli.py analyze-logs
python twilio_cli.py show-summary
```

## 🛠️ Available Commands

### Navigation (0-1)

- **0**: Interactive menu
- **1**: Analyze call logs

### Call Logs (2-3)

- **2**: Show call summary
- **3**: Visualize call volume

### Error Handling (4)

- **4**: Lookup Twilio error codes

### TrustHub (5-14)

- **5**: TrustHub Inspector menu
- **6**: List customer profiles
- **7**: Inspect specific profile
- **8**: List subaccounts
- **9**: Search subaccounts by number
- **10**: Delete customer profile
- **11**: Quick search for '239'
- **12**: Profile health check
- **13**: Subaccount overview
- **14**: Export profiles

### PhoneInfoga (15-19)

- **15**: Scan phone number
- **16**: Start web server
- **17**: Show version
- **18**: List scanners
- **19**: PhoneInfoga menu

## 🏗️ Project Structure

```
twilio/
├── src/
│   └── twilio_cli/              # Main Python package
│       ├── __init__.py
│       ├── main.py
│       ├── cli.py
│       ├── api/
│       │   └── trusthub_inspector.py
│       ├── utils/
│       │   ├── call_log.py
│       │   └── twilio_error_map.json
│       ├── cli_commands/
│       │   └── cli_commands.json
│       ├── core/                # Core business logic
│       └── tools/               # Tool integrations
├── tools/
│   └── PhoneInfoga/             # Go-based phone lookup tools
├── uploads/                     # CSV upload directory
├── tests/                       # Test files and logs
├── Dev_Man/                     # Project planning & docs
├── .env                         # Environment variables
├── pyproject.toml              # Project configuration
├── twilio_cli.py               # Root launcher script
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
```

### PhoneInfoga Setup

The PhoneInfoga tools are automatically detected if they exist in `tools/PhoneInfoga/`. Ensure you have Go installed and the tools are properly built.

## 📚 Usage Examples

### TrustHub Management

```bash
# Quick subaccount search
python twilio_cli.py 9 239

# Profile health overview
python twilio_cli.py 12

# Export all profiles
python twilio_cli.py 14
```

### Phone Number Analysis

```bash
# Scan a phone number
python twilio_cli.py 15 +1234567890

# Start PhoneInfoga web server
python twilio_cli.py 16

# List available scanners
python twilio_cli.py 18
```

### Call Log Analysis

```bash
# Analyze uploaded CSV files
python twilio_cli.py 1

# Show summary statistics
python twilio_cli.py 2

# Lookup error codes
python twilio_cli.py 4 12345
```

## 🧪 Development

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
uv run flake8 src/
```

### Installing in Development Mode

```bash
uv pip install -e .
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root or have the package installed
2. **PhoneInfoga Not Found**: Verify Go is installed and the tools are in the correct directory
3. **Twilio API Errors**: Check your `.env` file and API credentials

### Debug Mode

Enable verbose logging by setting the log level:

```bash
export LOGURU_LEVEL=DEBUG
python twilio_cli.py menu
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Twilio](https://www.twilio.com/) for their excellent API
- [PhoneInfoga](https://github.com/sundowndev/phoneinfoga) for phone number analysis tools
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [Click](https://click.palletsprojects.com/) for CLI framework

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the command index with `python twilio_cli.py index`
