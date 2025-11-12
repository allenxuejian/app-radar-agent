# Installation Guide

## Prerequisites

- Claude Code CLI installed
- Python 3.8 or higher
- pip package manager

## Quick Install

### Option 1: User-Level Installation (Recommended)

Install the agent globally for all your projects:

```bash
# Clone the repository
git clone https://github.com/yourusername/app-radar-agent.git
cd app-radar-agent

# Copy agent to Claude agents directory
cp app-radar-agent.md ~/.claude/agents/

# Copy supporting files
cp -r scripts ~/.claude/agents/app-radar-agent-scripts/
cp config.yaml ~/.claude/agents/app-radar-agent-scripts/

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
ls ~/.claude/agents/app-radar-agent.md
```

### Option 2: Project-Level Installation

Install for a specific project only:

```bash
# In your project directory
mkdir -p .claude/agents

# Copy agent file
cp /path/to/app-radar-agent.md .claude/agents/

# Copy supporting files
cp -r /path/to/scripts .claude/agents/app-radar-agent-scripts/
cp /path/to/config.yaml .claude/agents/app-radar-agent-scripts/

# Install dependencies
pip install -r requirements.txt
```

### Option 3: One-Line Install Script

```bash
curl -fsSL https://raw.githubusercontent.com/yourusername/app-radar-agent/main/install.sh | bash
```

## Verification

Test if the agent is properly installed:

```bash
# Start Claude Code
claude

# In the chat, try:
# "Show me metrics for Lemon8"
# or
# "Generate an app research report"
```

If the agent is installed correctly, it will automatically activate and run the analysis.

## Configuration

### Basic Configuration

Edit `config.yaml` to customize monitored apps:

```yaml
targets:
  - app: YourApp
    store: ios
  - app: AnotherApp
    store: android
```

### Advanced Configuration

Create a custom configuration file:

```bash
cp config.yaml config.custom.yaml
# Edit config.custom.yaml with your settings
```

Specify the custom config when using the agent:

```python
# In scripts/fetch_data.py, modify:
with open("config.custom.yaml") as f:
    cfg = yaml.safe_load(f)
```

## Updating

### Manual Update

```bash
cd app-radar-agent
git pull origin main

# Reinstall agent
cp app-radar-agent.md ~/.claude/agents/
cp -r scripts ~/.claude/agents/app-radar-agent-scripts/
```

### Automatic Update

Run the update script:

```bash
./update.sh
```

## Troubleshooting

### Agent Not Activating

1. Check if the file exists:
   ```bash
   ls ~/.claude/agents/app-radar-agent.md
   ```

2. Verify YAML frontmatter is valid:
   ```bash
   head -n 5 ~/.claude/agents/app-radar-agent.md
   ```

3. Restart Claude Code

### Python Dependencies Issues

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### API Rate Limiting

If you encounter rate limits:

1. Increase delay in `scripts/fetch_data.py`:
   ```python
   time.sleep(2)  # Change from 1 to 2 seconds
   ```

2. Reduce number of target apps in `config.yaml`

### Permission Errors

```bash
# Fix file permissions
chmod +x scripts/*.py
chmod 644 ~/.claude/agents/app-radar-agent.md
```

## Uninstall

```bash
# Remove agent file
rm ~/.claude/agents/app-radar-agent.md

# Remove supporting files
rm -rf ~/.claude/agents/app-radar-agent-scripts/

# Optionally remove Python packages
pip uninstall -y requests pyyaml
```

## Next Steps

- Read the [Usage Guide](USAGE.md) for detailed examples
- Check [Configuration Options](CONFIG.md) for advanced settings
- See [Examples](examples/) for sample outputs
- Join [Discussions](https://github.com/yourusername/app-radar-agent/discussions) for community support

## Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section above
2. Search [existing issues](https://github.com/yourusername/app-radar-agent/issues)
3. Create a [new issue](https://github.com/yourusername/app-radar-agent/issues/new) with:
   - Your OS and Python version
   - Claude Code version
   - Error messages
   - Steps to reproduce
