# Contributing to AXM Agent

Thank you for your interest in contributing to AXM Agent! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Any relevant code snippets

### Suggesting Features

We love feature suggestions! Please open an issue with:
- Clear description of the feature
- Use cases and examples
- Any implementation ideas

### Pull Requests

1. **Fork the repository**

2. **Clone your fork**
   ```bash
   git clone https://github.com/yourusername/axm-agent.git
   cd axm-agent
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

6. **Make your changes**
   - Write clear, documented code
   - Add tests for new features
   - Update documentation as needed

7. **Run tests**
   ```bash
   pytest tests/
   ```

8. **Run linting**
   ```bash
   black axm tests examples
   ruff check axm tests examples
   ```

9. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: description of your changes"
   ```

10. **Push to your fork**
    ```bash
    git push origin feature/your-feature-name
    ```

11. **Open a Pull Request**
    - Go to the original repository
    - Click "New Pull Request"
    - Select your branch
    - Describe your changes

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public APIs
- Keep lines under 100 characters
- Use Black for formatting

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use pytest for testing
- Mock external API calls

### Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update examples if adding new features
- Keep docs clear and concise

### Commit Messages

Use clear, descriptive commit messages:
- `Add: new feature description`
- `Fix: bug description`
- `Update: improvement description`
- `Docs: documentation changes`
- `Test: test-related changes`

## Project Structure

```
axm-agent/
├── axm/                 # Main package
│   ├── core/           # Core agent functionality
│   ├── llm/            # LLM providers
│   ├── mcp/            # MCP support
│   ├── memory/         # Memory implementations
│   ├── tools/          # Tool definitions
│   └── utils/          # Utilities
├── examples/           # Example scripts
├── tests/              # Test suite
├── docs/               # Documentation
└── pyproject.toml      # Package configuration
```

## Running Tests Locally

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=axm

# Run specific test file
pytest tests/test_agent.py

# Run with verbose output
pytest -v
```

## Building Documentation

```bash
# If we add docs later
cd docs
make html
```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a git tag
4. Push tag to trigger CI/CD
5. GitHub Actions will publish to PyPI

## Questions?

Feel free to open an issue or start a discussion on GitHub!

## Code of Conduct

Be respectful and inclusive. We want a welcoming community for everyone.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
