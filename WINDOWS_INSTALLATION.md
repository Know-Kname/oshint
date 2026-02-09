# Windows Installation Guide for Hughes Clues OSINT

**Last Updated**: 2025-12-31
**Tested On**: Windows 10/11, Python 3.11-3.13

---

## Quick Start (Recommended for Windows)

### Step 1: Install Windows-Compatible Dependencies

```powershell
# Install core dependencies (without problematic packages)
pip install -r requirements-windows.txt
```

**Note**: This skips some optional packages that are difficult to install on Windows:
- `face_recognition` (requires CMake and Visual C++ Build Tools)
- `dlib` (requires compilation)
- `torch` (2GB+ download - commented out by default)
- `transformers` (commented out by default)
- `spacy` (commented out by default)

---

## Common Installation Issues & Fixes

### Issue 1: face_recognition Installation Fails ❌

**Error**: `No matching distribution found for face_recognition>=1.3.5`

**Root Cause**:
- Maximum version is 1.3.0 (not 1.3.5)
- Requires CMake and Visual C++ Build Tools on Windows
- Not compatible with Python 3.13 yet

**Solution 1 - Skip face_recognition (Recommended)**:
The app works without it. Face recognition features will be disabled but all other functionality remains.

**Solution 2 - Install with Build Tools**:
```powershell
# 1. Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
# Select "Desktop development with C++"

# 2. Install CMake
# Download from: https://cmake.org/download/

# 3. Try installing face_recognition
pip install cmake
pip install dlib
pip install face_recognition==1.3.0
```

**Solution 3 - Use Python 3.11 (Most Compatible)**:
```powershell
# Uninstall Python 3.13, install Python 3.11
python --version  # Should show 3.11.x

# Create new venv
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements-windows.txt
```

---

### Issue 2: aioredis Deprecated Warning ⚠️

**Error**: `aioredis is deprecated`

**Fix**: Already fixed! `requirements-windows.txt` uses `redis>=5.0.1` which includes async support.

```python
# Old code (don't use)
import aioredis
redis = await aioredis.create_redis_pool('redis://localhost')

# New code (use this)
import redis.asyncio as aioredis
redis = await aioredis.from_url('redis://localhost')
```

---

### Issue 3: ModuleNotFoundError: No module named 'aiohttp' ❌

**Root Cause**: Installation was interrupted before completing

**Fix**:
```powershell
# Clear pip cache and retry
pip cache purge

# Install requirements again
pip install -r requirements-windows.txt

# Verify aiohttp is installed
pip show aiohttp
```

---

### Issue 4: Python 3.13 Compatibility Issues ⚠️

**Problem**: Python 3.13 is very new (released Oct 2024). Many packages don't have wheels yet.

**Recommended Python Versions for Windows**:
- ✅ **Python 3.11** (Most compatible - RECOMMENDED)
- ✅ **Python 3.12** (Good compatibility)
- ⚠️ **Python 3.13** (Limited package support)

**Downgrade to Python 3.11**:
```powershell
# 1. Download Python 3.11.x from python.org
# 2. Install with "Add to PATH" checked
# 3. Create new virtual environment
python3.11 -m venv venv
.\venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements-windows.txt
```

---

## Step-by-Step Installation

### 1. Prerequisites

**Required**:
- Windows 10 or 11
- Python 3.11 or 3.12 (3.13 may have issues)
- pip 24.0 or higher
- Git for Windows

**Optional** (for full features):
- Visual Studio Build Tools (for face_recognition)
- CMake (for dlib/face_recognition)
- Docker Desktop (for containerized services)

### 2. Clone Repository

```powershell
git clone https://github.com/Know-Kname/oshint.git
cd oshint
```

### 3. Create Virtual Environment

```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\activate

# Verify activation (you should see (venv) in prompt)
# (venv) PS C:\Users\YourName\oshint>
```

### 4. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 5. Install Dependencies

**Option A: Windows-Optimized (Recommended)**
```powershell
pip install -r requirements-windows.txt
```

**Option B: Full Installation (May Fail)**
```powershell
pip install -r requirements.txt
# If this fails, use Option A instead
```

**Option C: Minimal Core Only**
```powershell
# Just the essentials to get started
pip install aiohttp requests beautifulsoup4 dnspython pyyaml rich colorama fastapi uvicorn redis pymongo
```

### 6. Configure API Keys

```powershell
# Run interactive setup
python setup_api_keys.py

# Or manually edit config.yaml
notepad config.yaml
```

### 7. Verify Installation

```powershell
# Check installed packages
pip list | findstr aiohttp
pip list | findstr requests
pip list | findstr redis

# Test import
python -c "import aiohttp; print('aiohttp OK')"
python -c "import redis; print('redis OK')"
```

---

## Running the Application

### CLI Mode

```powershell
# Interactive menu
python cli_interface.py

# Direct command
python master_orchestrator.py example.com
```

### API Server

```powershell
# Start FastAPI server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Open browser to http://localhost:8000/docs
```

---

## Troubleshooting

### Error: "pip is not recognized"

```powershell
# Use python -m pip instead
python -m pip install -r requirements-windows.txt
```

### Error: "Cannot activate venv"

```powershell
# Enable script execution
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\activate
```

### Error: "SSL Certificate Verify Failed"

```powershell
# Install certificates
pip install --upgrade certifi

# Or bypass (not recommended)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-windows.txt
```

### Error: "Microsoft Visual C++ 14.0 is required"

**For face_recognition and other C++ packages**:

1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/
2. Run installer, select "Desktop development with C++"
3. Restart computer
4. Retry installation

**Or skip those packages**:
```powershell
# Use requirements-windows.txt which excludes problematic packages
pip install -r requirements-windows.txt
```

### ImportError: "No module named 'aiohttp'"

```powershell
# Installation was interrupted - reinstall
pip uninstall aiohttp -y
pip install aiohttp~=3.9.3
```

---

## Package Versions (Windows-Tested)

| Package | Version | Status | Notes |
|---------|---------|--------|-------|
| aiohttp | 3.9.3 | ✅ Works | HTTP async client |
| requests | 2.31.0 | ✅ Works | HTTP client |
| redis | 5.0.1 | ✅ Works | Replaces aioredis |
| cryptography | 42.0.2 | ✅ Works | Security fix |
| beautifulsoup4 | 4.12.0 | ✅ Works | HTML parsing |
| selenium | 4.16.0 | ✅ Works | Browser automation |
| playwright | 1.40.0 | ✅ Works | Modern browser automation |
| fastapi | 0.108.0 | ✅ Works | API framework |
| pandas | 2.1.4 | ✅ Works | Data analysis |
| numpy | 1.26.3 | ✅ Works | Numerical computing |
| opencv-python | 4.9.0 | ✅ Works | Computer vision |
| face_recognition | 1.3.0 | ⚠️ Optional | Needs build tools |
| torch | 2.0+ | ⚠️ Optional | 2GB+ download |
| spacy | 3.7+ | ⚠️ Optional | NLP (large) |

---

## Python Version Compatibility

| Python | Status | Notes |
|--------|--------|-------|
| 3.9 | ⚠️ Limited | End of life soon |
| 3.10 | ⚠️ Limited | Works but outdated |
| 3.11 | ✅ **RECOMMENDED** | Best compatibility |
| 3.12 | ✅ Good | Most packages available |
| 3.13 | ⚠️ Experimental | Some packages missing |

---

## Windows-Specific Configuration

### Running as Administrator

Some network operations may require admin privileges:

```powershell
# Right-click PowerShell
# Select "Run as Administrator"
cd C:\Users\YourName\oshint
.\venv\Scripts\activate
python master_orchestrator.py example.com
```

### Windows Defender / Antivirus

Add exclusions for:
- `C:\Users\YourName\oshint\` (project folder)
- `C:\Users\YourName\oshint\venv\` (virtual environment)

**Why**: Security tools may flag OSINT reconnaissance as suspicious.

### Firewall Configuration

Allow Python through Windows Firewall:
- Settings → Privacy & Security → Windows Security → Firewall & Network Protection
- Allow an app through firewall
- Add Python (python.exe from venv)

---

## Optional Services (Windows)

### MongoDB (Database)

**Option 1: MongoDB Community Server**
```powershell
# Download from: https://www.mongodb.com/try/download/community
# Install as Windows Service
# Default: mongodb://localhost:27017
```

**Option 2: Docker**
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Redis (Caching)

**Option 1: Redis for Windows (Memurai)**
```powershell
# Download: https://www.memurai.com/
# Free alternative to Redis for Windows
```

**Option 2: Docker**
```powershell
docker run -d -p 6379:6379 --name redis redis:latest
```

### Elasticsearch (Search)

**Option 1: Windows Installation**
```powershell
# Download: https://www.elastic.co/downloads/elasticsearch
# Extract and run bin\elasticsearch.bat
```

**Option 2: Docker**
```powershell
docker run -d -p 9200:9200 -e "discovery.type=single-node" elasticsearch:8.11.0
```

---

## Performance Tips for Windows

### 1. Use SSD for Virtual Environment
```powershell
# Move venv to SSD drive
C:\> cd D:\oshint  # If D: is SSD
D:\oshint> python -m venv venv
```

### 2. Increase Virtual Memory
- Control Panel → System → Advanced → Performance Settings
- Advanced tab → Virtual Memory → Change
- Set custom size: Initial 4096 MB, Maximum 8192 MB

### 3. Disable Windows Search Indexing
- Exclude `oshint` folder from Windows Search indexing
- Speeds up file operations

### 4. Use PowerShell 7 (Recommended)
```powershell
# Install PowerShell 7
winget install Microsoft.PowerShell

# Run with pwsh instead of powershell
pwsh
```

---

## Next Steps

1. ✅ Install dependencies with `requirements-windows.txt`
2. ✅ Configure API keys using `python setup_api_keys.py`
3. ✅ Test basic functionality: `python cli_interface.py`
4. ✅ Review documentation in `COMPREHENSIVE_REPAIR_PLAN.md`
5. ✅ Set up optional services (MongoDB, Redis, Elasticsearch)

---

## Getting Help

### Documentation
- `README.md` - Project overview
- `SECURITY_AUDIT_REPORT.md` - Security audit results
- `BUG_FIXES_AND_OPTIMIZATIONS.md` - Recent fixes
- `PEOPLE_INTELLIGENCE_GUIDE.md` - People search features

### Common Commands
```powershell
# Check Python version
python --version

# Check installed packages
pip list

# Check specific package
pip show aiohttp

# Reinstall package
pip uninstall aiohttp -y
pip install aiohttp~=3.9.3

# Clear pip cache
pip cache purge

# Update all packages
pip list --outdated
pip install --upgrade <package>
```

---

## Contact & Support

- **GitHub Issues**: https://github.com/Know-Kname/oshint/issues
- **Documentation**: See `docs/` folder
- **API Docs**: http://localhost:8000/docs (when API running)

---

**Installation Status Checklist**:

- [ ] Python 3.11 or 3.12 installed
- [ ] Virtual environment created and activated
- [ ] pip upgraded to latest version
- [ ] Dependencies installed successfully
- [ ] API keys configured in config.yaml
- [ ] Application runs without errors
- [ ] Optional services configured (MongoDB, Redis)
- [ ] Windows Defender exclusions added
- [ ] Firewall configured

**Happy OSINT hunting!** 🔍
