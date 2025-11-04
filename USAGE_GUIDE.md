# Hughes Clues - Complete Usage Guide

## Table of Contents
1. [Setup & Installation](#setup--installation)
2. [Configuration](#configuration)
3. [Running the System](#running-the-system)
4. [Module Reference](#module-reference)
5. [API Examples](#api-examples)
6. [CTF Challenge Tips](#ctf-challenge-tips)
7. [Troubleshooting](#troubleshooting)

---

## Setup & Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB 5.0+ or Docker
- Redis 6.0+ or Docker
- PostgreSQL 13+ (optional, for full deployment)

### Docker Setup (Recommended for CTF)

```bash
# Navigate to project directory
cd Hughes\ Clues

# Build all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f orchestrator
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start databases manually
# MongoDB
mongod

# Redis (in another terminal)
redis-server

# Then run the orchestrator
python master_orchestrator.py --target example.com
```

---

## Configuration

### config.yaml Structure

```yaml
# Database Configuration
mongodb_uri: "mongodb://localhost:27017"
redis_host: "localhost"
redis_port: 6379

# Performance Settings
max_workers: 4           # Number of worker threads
cache_ttl: 3600          # Cache time-to-live in seconds
enable_uvloop: true      # Use uvloop for better async performance

# API Keys (required for full functionality)
api_keys:
  shodan_key: "your_shodan_api_key"
  censys_id: "your_censys_id"
  censys_secret: "your_censys_secret"
  virustotal_key: "your_vt_key"
  securitytrails_key: "your_securitytrails_key"
  urlscan_key: "your_urlscan_key"
  hibp_key: "your_hibp_key"
  dehashed_key: "your_dehashed_key"
  snusbase_key: "your_snusbase_key"

# Analysis Configuration
analysis:
  anomaly_threshold: 0.95      # Anomaly detection sensitivity
  correlation_threshold: 0.7   # Min correlation for findings
  risk_weights:
    vulnerabilities: 0.3
    exposures: 0.25
    breaches: 0.2
    infrastructure: 0.15
    reconnaissance: 0.1

# Operation Timeouts (seconds)
timeouts:
  reconnaissance: 300
  web_scraping: 600
  credential_harvest: 300
  geolocation: 120
  dark_web: 900

# Logging Configuration
logging:
  level: "INFO"            # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "hughes_clues.log"
```

### Environment Variables

You can override config values with environment variables:

```bash
# Set config file location
export CONFIG_FILE=/path/to/config.yaml

# Set app directory (for Docker compatibility)
export APP_DIR=/app

# Set modules directory
export MODULES_DIR=/app/modules

# Run the orchestrator
python master_orchestrator.py
```

---

## Running the System

### Method 1: Master Orchestrator (Recommended)

The Master Orchestrator coordinates all intelligence gathering operations.

```bash
# Basic reconnaissance on a target
python master_orchestrator.py --target example.com

# Run specific operations
python master_orchestrator.py --target example.com \
  --operations recon scrape creds geo

# Custom config file
python master_orchestrator.py --target example.com \
  --config /path/to/config.yaml

# Adjust worker count
python master_orchestrator.py --target example.com --workers 8

# Run as daemon (no target, just wait for operations)
python master_orchestrator.py
```

### Method 2: Individual Modules

Run specific intelligence modules directly.

#### Reconnaissance Module
```bash
python elite_recon_module.py example.com \
  --config config.yaml \
  --output recon_report.json \
  --timeout 30
```

**Gathers:**
- DNS records (A, AAAA, MX, NS, TXT, DNSSEC)
- WHOIS information
- SSL/TLS certificate data
- Technology fingerprinting
- Shodan vulnerability data
- Certificate transparency logs
- GitHub exposure detection
- Breach database checks (HaveIBeenPwned)
- Cloud asset discovery (S3 buckets)

#### Credential Harvester
```bash
python elite_credential_harvester.py user@example.com \
  --type email \
  --config config.yaml \
  --output credentials.json
```

**Operations:**
- Query breach databases (DeHashed, Snusbase, HIBP)
- Password strength analysis
- Hash cracking attempts
- Credential stuffing (SSH, FTP, HTTP forms)
- Results storage in MongoDB

#### Dark Web Monitor
Requires Tor connection configured:

```bash
python elite_darkweb_monitor.py example.com \
  --keywords "example,sensitive_data" \
  --max-depth 2
```

**Monitors:**
- Onion site discovery
- Marketplace monitoring
- Paste site aggregation
- Bitcoin address tracking

---

## Module Reference

### 1. Elite Reconnaissance Module (`elite_recon_module.py`)

**Key Functions:**

```python
from elite_recon_module import AdvancedReconModule, APIConfig

# Initialize with API keys
config = APIConfig(
    shodan_key="your_key",
    censys_id="id",
    censys_secret="secret"
)

recon = AdvancedReconModule("example.com", config=config, timeout=30)

# Run individual tests
dns_results = recon.dns_enumeration_advanced()
whois_data = recon.whois_lookup()
ssl_info = recon.ssl_certificate_info()
tech_stack = recon.technology_fingerprinting()

# Run all tests asynchronously
import asyncio
results = asyncio.run(recon.run_full_recon_async())

# Export results
recon.export_comprehensive_report("output.json")
```

**Output Structure:**
```json
{
  "target": "example.com",
  "timestamp": "2024-11-03T12:00:00",
  "dns": {...},
  "whois": {...},
  "ssl": {...},
  "shodan": {"vulnerabilities": [...]},
  "github_exposure": {"total_findings": 5},
  "cloud_assets": {"aws_s3_buckets": [...]},
  "risk_score": 65
}
```

### 2. Credential Harvester (`elite_credential_harvester.py`)

**Key Functions:**

```python
from elite_credential_harvester import EliteCredentialHarvester

harvester = EliteCredentialHarvester(api_keys={
    "hibp": "key",
    "dehashed": "key",
    "snusbase": "key"
})

# Harvest for email
results = asyncio.run(harvester.harvest_email("user@example.com"))

# Harvest for domain
results = asyncio.run(harvester.harvest_domain("example.com"))

# Test credentials
stuffing = CredentialStuffer(credentials, rate_limit=1.0)
ssh_success = asyncio.run(stuffing.test_ssh("192.168.1.1"))
ftp_success = asyncio.run(stuffing.test_ftp("192.168.1.1"))
http_success = asyncio.run(stuffing.test_http_form("http://example.com/login"))
```

**Output Structure:**
```json
{
  "email": "user@example.com",
  "breaches": [
    {
      "breach_name": "LinkedIn",
      "breach_date": "2021-06-15",
      "compromised_data": ["email", "password"]
    }
  ],
  "credentials": [
    {
      "username": "user",
      "password": "password123",
      "domain": "example.com",
      "source": "dehashed",
      "verified": true,
      "verified_on": ["ssh://192.168.1.1:22"]
    }
  ],
  "statistics": {
    "total_breaches": 3,
    "total_credentials": 15,
    "cleartext_passwords": 8
  }
}
```

### 3. Analysis Engine (`elite_analysis_engine.py`)

```python
from elite_analysis_engine import AdvancedAnalyzer, AnalysisConfig

config = AnalysisConfig(
    anomaly_threshold=0.95,
    correlation_threshold=0.7
)

analyzer = AdvancedAnalyzer(config)

# Analyze patterns in data
patterns = analyzer.analyze_patterns(intelligence_data)

# Detect anomalies
anomaly_indices, scores = analyzer.detect_anomalies(data)

# Calculate risk score
risk_assessment = analyzer.calculate_advanced_risk_score(intel_data)
```

### 4. Dark Web Monitor (`elite_darkweb_monitor.py`)

Requires Tor connection:

```bash
# Start Tor
tor --control-port 9051 --socks-port 9050

# Run monitor
python elite_darkweb_monitor.py example.com \
  --keywords "credentials,data" \
  --max-depth 2
```

---

## API Examples

### Using Master Orchestrator Programmatically

```python
import asyncio
from master_orchestrator import MasterOrchestrator, OperationType

async def main():
    # Initialize orchestrator
    orchestrator = MasterOrchestrator("config.yaml")

    # Start worker threads
    orchestrator.start_workers()

    try:
        # Run full intelligence pipeline
        report = await orchestrator.run_full_intelligence_pipeline(
            target="example.com",
            operations=[
                OperationType.RECONNAISSANCE,
                OperationType.WEB_SCRAPING,
                OperationType.CREDENTIAL_HARVEST,
                OperationType.GEOLOCATION
            ]
        )

        print(f"Risk Score: {report.risk_score}/100")
        print(f"Confidence: {report.confidence:.2%}")

        # Access cached results
        cached = orchestrator.get_cached_result("recon:example.com")

        # Get system statistics
        stats = orchestrator.get_system_stats()
        print(f"Operations Completed: {stats['operations_completed']}")
        print(f"Success Rate: {stats['success_rate']:.2%}")

    finally:
        orchestrator.shutdown()

asyncio.run(main())
```

### Caching Operations

```python
# Cache a result for 1 hour
orchestrator.cache_result(
    "recon:example.com",
    recon_results,
    ttl=3600
)

# Retrieve from cache
cached_data = orchestrator.get_cached_result("recon:example.com")

# Invalidate cache by pattern
orchestrator.invalidate_cache("recon:*")
```

---

## CTF Challenge Tips

### 1. Finding Hidden Information

**DNS Enumeration:**
- Look for zone transfers (`dns_results['zone_transfer']`)
- Check for DNSSEC misconfiguration
- Extract subdomain information from CT logs

**GitHub Secrets:**
- The GitHub dorking automatically searches for:
  - Exposed API keys
  - .env files
  - Config files with credentials
  - Password patterns
- Rate limiting is now implemented to avoid blocking

**Bucket Discovery:**
- Enumerate common S3 bucket patterns
- Check permissions (public vs private)
- Look in `cloud_assets['aws_s3_buckets']`

### 2. Credential Exploitation

**Breach Database Queries:**
```python
# Query for known breaches
breaches = await harvester.harvest_email("target@example.com")

# Try credential stuffing with discovered credentials
stuffing = CredentialStuffer(found_credentials)
successful = await stuffing.test_ssh("target_host")
```

**Password Analysis:**
- Strength scoring helps identify weak passwords
- Mutations generate common variations automatically
- Hash cracking attempts common wordlists

### 3. Network Reconnaissance

**Technology Fingerprinting:**
- Identifies web frameworks (React, Django, Laravel)
- Detects CMS systems (WordPress, Drupal)
- Finds CDN usage
- Reveals security headers

**Port & Service Detection:**
- Shodan integration for known vulnerabilities
- Service version identification
- Banner grabbing

### 4. Risk Score Interpretation

```
CRITICAL (80-100): Immediate action required
HIGH (60-79):      Multiple security issues found
MEDIUM (40-59):    Some concerning findings
LOW (20-39):       Minor issues detected
MINIMAL (0-19):    Clean target
```

Risk components breakdown:
- **Vulnerabilities (30%)** - CVE severity
- **Exposures (25%)** - Secret leaks, public buckets
- **Breaches (20%)** - Email compromises
- **Infrastructure (15%)** - Open ports, outdated software
- **Reconnaissance (10%)** - DNS issues, zone transfers

---

## Troubleshooting

### Common Issues

#### 1. Module Not Found Error
```
[!] Module not found: /opt/hughes_clues/modules/elite_recon_module.py
```

**Solution:**
```bash
# Set MODULES_DIR environment variable
export MODULES_DIR=/path/to/modules
export APP_DIR=/app

# Or pass config explicitly
python master_orchestrator.py --config ./config.yaml
```

#### 2. MongoDB Connection Failed
```
pymongo.errors.ServerSelectionTimeoutError: No servers found yet
```

**Solution:**
```bash
# Verify MongoDB is running
docker-compose ps

# Check logs
docker-compose logs mongodb

# Restart if needed
docker-compose restart mongodb
```

#### 3. Redis Connection Error
```
redis.exceptions.ConnectionError: Connection refused
```

**Solution:**
```bash
# Start Redis
docker-compose up -d redis

# Or manually
redis-server --port 6379
```

#### 4. Rate Limiting Failures

**GitHub API:**
- Implement delays between requests
- Now handled automatically with rate limit headers
- Check `X-RateLimit-Remaining` header

**HIBP API:**
- 1.5 second delay between requests (enforced)
- Authentication optional but recommended
- Now uses try/finally to guarantee delays

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python master_orchestrator.py --target example.com 2>&1 | tee debug.log

# Check specific module logs
tail -f hughes_clues.log | grep "elite_recon"
```

### Performance Tuning

```yaml
# config.yaml
max_workers: 8                # Increase for parallel processing
cache_ttl: 7200              # Longer caching reduces API calls
enable_uvloop: true          # Use uvloop for better performance

# Async operation timeouts
timeouts:
  reconnaissance: 600        # Increase for slow networks
  web_scraping: 900
  credential_harvest: 600
```

---

## Key Improvements Made

### Fixed Issues

1. ✅ **Path Mismatches** - Environment variable support for Docker compatibility
2. ✅ **Zone Transfer Bug** - Corrected DNS method call syntax
3. ✅ **Event Loop Efficiency** - Persistent loops per worker thread
4. ✅ **GitHub Rate Limiting** - Implemented rate limit header checking
5. ✅ **HIBP Rate Limiting** - Fixed with try/finally pattern
6. ✅ **Async SSH/FTP** - Non-blocking credential testing
7. ✅ **Password Mutations** - Deterministic ordering with deduplication
8. ✅ **Data Serialization** - MongoDB-compatible DateTime/Enum handling
9. ✅ **Redis Caching** - Full caching layer implementation
10. ✅ **Bare Exceptions** - Replaced with specific Exception handling

---

## Example CTF Workflow

```bash
# 1. Set up environment
export CONFIG_FILE=./config.yaml
export APP_DIR=$(pwd)

# 2. Start services
docker-compose up -d

# 3. Run reconnaissance
python master_orchestrator.py --target vulnerable.ctf \
  --operations recon scrape geo

# 4. Check results in MongoDB
mongosh
> use hughes_clues
> db.reports.findOne({})

# 5. Analyze findings for flags
# Look for:
# - Exposed credentials in github_exposure
# - Public S3 buckets
# - Vulnerable services in shodan
# - Email breaches
# - Sensitive files in web scraping results

# 6. Extract flags and submit
```

---

For more detailed documentation, refer to individual module docstrings and README.md.
