# Publishing to PyPI

This guide walks you through publishing AXM Agent to PyPI.

## Prerequisites

1. **PyPI Account**
   - Create account at https://pypi.org
   - Create account at https://test.pypi.org (for testing)

2. **API Tokens**
   - Generate API token at https://pypi.org/manage/account/token/
   - Generate test token at https://test.pypi.org/manage/account/token/

3. **Install Build Tools**
   ```bash
   pip install build twine
   ```

## Testing Locally

1. **Run tests**
   ```bash
   pytest tests/
   ```

2. **Check linting**
   ```bash
   black axm tests examples
   ruff check axm tests examples
   ```

3. **Build the package**
   ```bash
   python -m build
   ```

   This creates files in `dist/`:
   - `axm_agent-0.1.0.tar.gz` (source distribution)
   - `axm_agent-0.1.0-py3-none-any.whl` (wheel)

4. **Check the package**
   ```bash
   twine check dist/*
   ```

## Publishing to Test PyPI

Test first before publishing to production PyPI:

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Or with token
twine upload --repository testpypi dist/* -u __token__ -p YOUR_TEST_TOKEN
```

**Test installation:**
```bash
pip install --index-url https://test.pypi.org/simple/ axm-agent
```

## Publishing to Production PyPI

Once testing is complete:

```bash
# Upload to PyPI
twine upload dist/*

# Or with token
twine upload dist/* -u __token__ -p YOUR_PYPI_TOKEN
```

**Verify:**
```bash
pip install axm-agent
```

## Automated Publishing with GitHub Actions

The repository includes a GitHub Action that automatically publishes to PyPI when you create a release.

### Setup

1. **Add PyPI token to GitHub Secrets**
   - Go to: Settings → Secrets and variables → Actions
   - Add new secret: `PYPI_API_TOKEN`
   - Paste your PyPI API token

2. **Create a release**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

   Or use GitHub's release interface:
   - Go to: Releases → Create a new release
   - Choose a tag (e.g., v0.1.0)
   - Write release notes
   - Publish release

3. **Automated workflow**
   - GitHub Actions will automatically:
     - Build the package
     - Run tests
     - Publish to PyPI

## Version Management

Update version in `pyproject.toml`:

```toml
[project]
version = "0.1.0"  # Update this
```

Follow Semantic Versioning:
- MAJOR: Breaking changes (1.0.0 → 2.0.0)
- MINOR: New features (0.1.0 → 0.2.0)
- PATCH: Bug fixes (0.1.0 → 0.1.1)

## Pre-Release Checklist

- [ ] All tests pass
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated
- [ ] Version number is bumped
- [ ] README.md has correct info
- [ ] Examples work correctly
- [ ] Package builds without errors
- [ ] Test installation works

## Post-Release

1. **Verify installation**
   ```bash
   pip install axm-agent --upgrade
   python -c "import axm; print(axm.__version__)"
   ```

2. **Test basic functionality**
   ```bash
   python quickstart.py
   ```

3. **Update documentation**
   - Add release notes
   - Update changelog
   - Announce on social media

## Troubleshooting

### "Package already exists"
- You can't re-upload the same version
- Bump the version number and rebuild

### "Invalid API token"
- Check token is correct
- Use `__token__` as username
- Token should start with `pypi-`

### "Package name already taken"
- Choose a different name in pyproject.toml
- Check availability at https://pypi.org

### Build errors
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Rebuild
python -m build
```

## Useful Commands

```bash
# Check package info
twine check dist/*

# View package contents
tar -tzf dist/axm-agent-0.1.0.tar.gz

# Check installed version
pip show axm-agent

# Uninstall
pip uninstall axm-agent

# Install from local build
pip install dist/axm_agent-0.1.0-py3-none-any.whl
```

## Resources

- PyPI: https://pypi.org
- Packaging Guide: https://packaging.python.org
- Twine Docs: https://twine.readthedocs.io
- Build Docs: https://build.pypa.io
