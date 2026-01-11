# Quick Fix for PyPI Upload Error

## Immediate Solution

The error occurs because the project doesn't exist on PyPI yet or the token is incorrectly scoped.

### Step 1: Create an "Entire Account" API Token

1. Go to https://pypi.org/manage/account/
2. Scroll to "API tokens"
3. Click "Add API token"
4. **Important**: Select "Entire account" scope (not project-specific)
5. Copy the token (starts with `pypi-`)

### Step 2: Upload Using the Token

```bash
# Install tools
pip install build twine

# Build the package
python -m build

# Upload using the token
twine upload dist/* -u __token__ -p pypi-YourTokenHere
```

Replace `pypi-YourTokenHere` with your actual token.

### Step 3: Verify

After successful upload, verify:
```bash
pip install translateplus
python -c "import translateplus; print(translateplus.__version__)"
```

## Why This Works

- "Entire account" tokens can create new projects on PyPI
- Project-specific tokens only work for existing projects
- The first upload automatically creates the project

## Alternative: Use .pypirc

Create `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-YourTokenHere
```

Then simply run:
```bash
twine upload dist/*
```
