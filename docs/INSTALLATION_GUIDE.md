# Hughes Clues - Installation Guide

## Problem: "Externally Managed Environment" Error

When running `pip install -r requirements.txt`, you may see:
```
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install xyz, where xyz is
    the package you are trying to install.
```

This happens because your Python installation is managed by the system package manager (apt/dnf/pacman).

---

## Solution 1: Use Virtual Environment (RECOMMENDED)

### Windows (Most Reliable)

```bash
# Navigate to Hughes Clues directory
cd "Hughes Clues"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Now install requirements
pip install -r requirements.txt
```

After this, you'll see `(venv)` in your terminal prompt.

### Linux/Mac

```bash
# Navigate to Hughes Clues directory
cd "Hughes Clues"

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Now install requirements
pip install -r requirements.txt
```

### How to Use After Setup

**Every time** you want to run Hughes Clues:

```bash
# Activate the environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Run the CLI
python cli_interface.py

# Deactivate when done
deactivate
```

---

## Solution 2: Use --break-system-packages Flag (QUICK FIX)

If you don't want to use virtual environments:

```bash
pip install --break-system-packages -r requirements.txt
```

**⚠️ Warning**: This modifies system Python and may affect other applications.

---

## Solution 3: Use Conda (IF YOU HAVE IT)

If you have Anaconda/Miniconda installed:

```bash
# Create conda environment
conda create -n hughes-clues python=3.10

# Activate environment
conda activate hughes-clues

# Install requirements
pip install -r requirements.txt

# Run
python cli_interface.py
```

---

## Solution 4: Use Docker (CLEANEST)

Using Docker eliminates dependency conflicts:

```bash
# Build Docker image
docker-compose build

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps

# Access MongoDB
docker-compose exec mongodb mongosh
```

All dependencies are already configured in `docker-compose.yml`.

---

## Troubleshooting: "No module named 'pymongo'"

If you get this error after installation:

### Quick Fix
```bash
pip install pymongo
```

### Full Fix with Virtual Environment
```bash
# Activate your virtual environment first!
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Then install
pip install pymongo
```

### Verify Installation
```bash
python -c "import pymongo; print(pymongo.__version__)"
```

Should print version number (e.g., `4.5.0`).

---

## Step-by-Step Installation

### 1. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Upgrade pip

```bash
pip install --upgrade pip
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

**This will install:**
- ✅ aiohttp, requests, httpx
- ✅ beautifulsoup4, selenium, lxml, playwright, scrapy
- ✅ dnspython, python-whois, aiodns
- ✅ bcrypt, passlib, paramiko, asyncssh
- ✅ pandas, numpy, scipy, scikit-learn
- ✅ motor, redis, aioredis, psutil
- ✅ pymongo ← This is what you need!
- ✅ And 20+ more packages

### 4. Verify Installation

```bash
python -c "import pymongo; import bcrypt; print('All imports OK')"
```

Should output: `All imports OK`

### 5. Run Hughes Clues

```bash
python cli_interface.py
```

---

## Common Issues & Solutions

### Issue: "No module named 'pymongo'"

**Cause**: Virtual environment not activated

**Solution**:
```bash
# Activate first!
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Verify active (should show (venv) in prompt)
pip install pymongo
python cli_interface.py
```

### Issue: "No module named 'bcrypt'"

**Solution**:
```bash
source venv/bin/activate
pip install bcrypt>=4.0.0
```

### Issue: "No module named 'psutil'"

**Solution**:
```bash
source venv/bin/activate
pip install psutil>=5.9.0
```

### Issue: Permission Denied

**Solution**: Use virtual environment instead of system Python

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Virtual Environment Management

### Check Active Environment

```bash
# Shows path to active Python
which python  # Linux/Mac
where python  # Windows
```

Should show path inside `venv` directory.

### Deactivate Environment

```bash
deactivate
```

### Delete Environment

```bash
# If you want to start over
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows
```

---

## Docker Alternative

If you don't want to deal with Python environments:

```bash
# Everything is containerized
docker-compose up -d

# Run CLI in container
docker-compose exec orchestrator python cli_interface.py

# Check logs
docker-compose logs -f orchestrator
```

---

## Verification Checklist

After installation, verify everything works:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Check Python version
python --version  # Should be 3.8+

# 3. Check pip location
pip --version  # Should show (venv) path

# 4. Check critical imports
python -c "
import pymongo
import bcrypt
import paramiko
import asyncssh
import playwright
print('✓ All critical modules loaded')
"

# 5. Check if MongoDB is accessible
python -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://localhost:27017')
    print('✓ MongoDB connection works')
except:
    print('✗ MongoDB not running (start with docker-compose)')
"

# 6. Run the CLI
python cli_interface.py
```

---

## Quick Start Script

Save this as `setup.sh` (Linux/Mac) or `setup.bat` (Windows):

### Linux/Mac (setup.sh):
```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Installation complete!"
echo "Run: python cli_interface.py"
```

### Windows (setup.bat):
```batch
@echo off
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
echo Installation complete!
echo Run: python cli_interface.py
```

---

## Summary

| Method | Pros | Cons | Best For |
|--------|------|------|----------|
| Virtual Env | Clean, isolated, no conflicts | Extra steps | **Recommended** |
| --break-system | Quick, one command | May break system Python | Testing only |
| Conda | Easy, powerful | Requires Conda installed | Conda users |
| Docker | Complete isolation | More resources | Production |

**Recommended**: Use Virtual Environment (Solution 1)

---

## Getting Help

If you still have issues:

1. Check Python version: `python --version` (Should be 3.8+)
2. Check pip: `pip --version` (Should show venv path)
3. Try upgrading: `pip install --upgrade pip`
4. Install one package: `pip install pymongo` (test if pip works)
5. Check requirements.txt is in correct directory: `ls requirements.txt`

