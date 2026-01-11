# Publishing to PyPI

This guide explains how to publish the `translateplus` package to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org) if you don't have one
2. **API Token**: Generate a PyPI API token with upload permissions

## Step 1: Register the Project on PyPI (First Time Only)

If this is the first time publishing, you need to register the project name on PyPI:

### Option A: Using Web Interface

1. Go to [pypi.org](https://pypi.org)
2. Log in to your account
3. Go to "Your projects" → "Add new project"
4. Enter project name: `translateplus`
5. Fill in the project details
6. Click "Create"

### Option B: Using Twine (Recommended)

```bash
# Install twine if not already installed
pip install twine build

# Build the package
python -m build

# Register the project (first time only)
twine register dist/translateplus-2.0.0.tar.gz
```

**Note**: PyPI no longer requires explicit registration. You can skip this step and go directly to uploading.

## Step 2: Create PyPI API Token

1. Go to [pypi.org/manage/account/](https://pypi.org/manage/account/)
2. Scroll to "API tokens"
3. Click "Add API token"
4. Choose scope:
   - **For new projects**: Select "Entire account" (recommended for first upload)
   - **For existing projects**: Select "Project: translateplus"
5. Copy the token (it starts with `pypi-`)

## Step 3: Configure Authentication

### Option A: Using .pypirc (Recommended)

Create or edit `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YourAPITokenHere
```

### Option B: Using Environment Variable

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YourAPITokenHere
```

### Option C: Pass Directly to Twine

```bash
twine upload dist/* -u __token__ -p pypi-YourAPITokenHere
```

## Step 4: Build the Package

```bash
# Install build tools
pip install build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/translateplus-2.0.0.tar.gz` (source distribution)
- `dist/translateplus-2.0.0-py3-none-any.whl` (wheel)

## Step 5: Check the Package (Optional but Recommended)

```bash
# Check the package for common issues
twine check dist/*
```

## Step 6: Upload to PyPI

### Test PyPI (Recommended for First Upload)

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*
```

Then test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ translateplus
```

### Production PyPI

```bash
# Upload to production PyPI
twine upload dist/*
```

Or if using environment variables:
```bash
twine upload dist/* --username __token__ --password $TWINE_PASSWORD
```

## Troubleshooting

### Error: "Invalid API Token: OIDC scoped token is not valid for project"

**Solution**: This means the project doesn't exist on PyPI yet or the token is scoped incorrectly.

1. **If project doesn't exist**: The first upload will automatically create it. Make sure your token has "Entire account" scope, not project-specific.

2. **If using project-scoped token**: 
   - The project name must match exactly (case-insensitive)
   - Try using an "Entire account" token instead

3. **Check token scope**:
   - Go to [pypi.org/manage/account/](https://pypi.org/manage/account/)
   - Verify your token has the correct scope

### Error: "403 Forbidden"

**Possible causes**:
- Invalid or expired API token
- Token doesn't have upload permissions
- Project name mismatch

**Solution**:
- Generate a new API token with "Entire account" scope
- Verify the token is correct (starts with `pypi-`)
- Check that you're using `__token__` as username

### Error: "File already exists"

**Solution**: The version already exists on PyPI. You need to:
- Increment the version in `pyproject.toml` and `setup.py`
- Rebuild and upload

## Automated Publishing with GitHub Actions

The repository includes a GitHub Actions workflow (`.github/workflows/publish.yml`) that automatically publishes when you create a release.

### Setup

1. Go to PyPI → Account Settings → API tokens
2. Create a token with "Entire account" scope
3. Go to GitHub → Repository → Settings → Secrets and variables → Actions
4. Add a new secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (starts with `pypi-`)

### Usage

1. Update version in `pyproject.toml` and `setup.py`
2. Commit and push changes
3. Create a new GitHub release
4. The workflow will automatically build and publish to PyPI

## Version Management

Always update the version in both files:
- `pyproject.toml`: `version = "2.0.0"`
- `setup.py`: `version="2.0.0"`
- `translateplus/__init__.py`: `__version__ = "2.0.0"`

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (2.0.0): Breaking changes
- **MINOR** (2.1.0): New features, backward compatible
- **PATCH** (2.0.1): Bug fixes, backward compatible

## Verification

After publishing, verify the package:

```bash
# Install from PyPI
pip install translateplus

# Verify version
python -c "import translateplus; print(translateplus.__version__)"

# Test import
python -c "from translateplus import TranslatePlusClient; print('OK')"
```

Check on PyPI: https://pypi.org/project/translateplus/
