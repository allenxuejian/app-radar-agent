# Contributing to App Radar Agent

Thank you for your interest in contributing to App Radar Agent! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates.

When filing a bug report, include:
- Clear, descriptive title
- Detailed steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Claude Code version)
- Error messages and logs
- Screenshots if applicable

### Suggesting Features

We welcome feature suggestions! Please:
- Check if the feature has already been requested
- Clearly describe the use case
- Explain how it would benefit users
- Provide examples if possible

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/app-radar-agent.git
   cd app-radar-agent
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write clear, commented code
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   # Run the scripts
   python scripts/fetch_data.py
   python scripts/analyze.py
   python scripts/report.py

   # Verify the agent works with Claude Code
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   ```

   Follow commit message conventions:
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `style:` code style changes
   - `refactor:` code refactoring
   - `test:` test additions/changes
   - `chore:` maintenance tasks

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Reference related issues
   - Include screenshots/examples if relevant

## Development Setup

### Prerequisites

- Python 3.8+
- pip
- git
- Claude Code CLI

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/app-radar-agent.git
cd app-radar-agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Install the agent locally
cp app-radar-agent.md ~/.claude/agents/
```

### Code Style

We follow PEP 8 guidelines for Python code:

```bash
# Format code with black
black scripts/*.py

# Check style with flake8
flake8 scripts/*.py

# Type checking with mypy
mypy scripts/*.py
```

### Testing

```bash
# Run tests
pytest tests/

# Run specific test
pytest tests/test_fetch_data.py

# Run with coverage
pytest --cov=scripts tests/
```

## Project Structure

```
app-radar-agent/
├── app-radar-agent.md      # Main agent definition (YAML + Markdown)
├── scripts/
│   ├── fetch_data.py       # Data fetching logic
│   ├── analyze.py          # Analysis engine
│   └── report.py           # Report generation
├── tests/                  # Test files
├── examples/               # Example outputs
└── docs/                   # Additional documentation
```

## Adding New Features

### Adding New App Stores

To add support for a new app store (e.g., Google Play):

1. Create a new fetcher function in `scripts/fetch_data.py`:
   ```python
   def fetch_playstore_data(app_name):
       # Implementation
       pass
   ```

2. Update `config.yaml` schema to support new store type

3. Update documentation

4. Add tests

### Adding New Metrics

To add new metrics to track:

1. Modify the data structure in `fetch_data.py`
2. Update analysis logic in `analyze.py`
3. Add new columns to report in `analyze.py`
4. Update documentation
5. Add example in `examples/`

### Adding New Analysis Types

To add new analysis capabilities:

1. Create new analysis function in `scripts/analyze.py`
2. Update report generation to include new insights
3. Document the new analysis type
4. Add examples

## Documentation

When adding features, please update:

- `README.md` - User-facing documentation
- `INSTALL.md` - Installation instructions
- `app-radar-agent.md` - Agent definition and usage
- Code comments - Inline documentation
- Examples - Sample outputs

## Release Process

Maintainers will handle releases:

1. Update version number
2. Update CHANGELOG.md
3. Create release tag
4. Publish release notes

## Questions?

- Open a [Discussion](https://github.com/yourusername/app-radar-agent/discussions)
- Join our community chat
- Check existing documentation

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

Thank you for contributing! 🙏
