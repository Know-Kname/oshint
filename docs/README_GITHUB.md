# Hughes Clues - Elite OSINT Reconnaissance Toolkit

> *"Elementary, my dear Watson... if Watson was a highly sophisticated OSINT automation toolkit."*

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Hughes Clues** is a comprehensive, async-powered OSINT reconnaissance suite designed for security researchers, penetration testers, and CTF enthusiasts. Automate intelligence gathering across DNS, credentials, dark web, cloud infrastructure, and more.

## 🌟 Features

### 🔍 Reconnaissance Module
- **Advanced DNS Enumeration** - A, AAAA, MX, NS, TXT, DNSSEC, zone transfers
- **WHOIS Analysis** - Registration and contact information
- **SSL/TLS Intelligence** - Certificate chain analysis
- **Technology Fingerprinting** - Identify web frameworks and CMS
- **Shodan Integration** - Known vulnerabilities and open ports
- **Certificate Transparency** - Subdomain enumeration via CT logs
- **GitHub Exposure Detection** - Find secrets in public repos

### 🔐 Credential Harvesting
- **Breach Database Integration** - DeHashed, Snusbase, HaveIBeenPwned
- **Password Analysis** - Strength scoring and pattern detection
- **Credential Stuffing** - SSH, FTP, HTTP form testing (async)
- **Hash Cracking** - MD5, SHA1, SHA256, SHA512 support
- **Mutation Generation** - Automatic password variations

### 🌐 Dark Web Monitoring
- **Tor Integration** - Onion site discovery and monitoring
- **Marketplace Monitoring** - Track dark web listings
- **Paste Site Aggregation** - Monitor credential dumps
- **Bitcoin Address Tracking** - Financial intelligence

### ☁️ Cloud & Infrastructure
- **S3 Bucket Discovery** - Find misconfigured AWS buckets
- **Cloud Asset Mapping** - Azure, GCP, AWS resources
- **Port Scanning** - Service enumeration
- **Network Intelligence** - IP geolocation and ASN lookup

### 📊 Advanced Analysis
- **Pattern Recognition** - Anomaly detection in data
- **Risk Scoring** - Comprehensive threat assessment
- **Correlation Analysis** - Link disparate intelligence
- **Report Generation** - Professional intelligence reports

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Docker & Docker Compose (recommended)
- 2GB RAM minimum

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/hughes-clues.git
cd hughes-clues

# Start services
docker-compose up -d

# Run interactive CLI
python cli_interface.py

# Or direct orchestrator
python master_orchestrator.py --target example.com
```

### Option 2: Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start databases
# MongoDB
mongod

# Redis (in another terminal)
redis-server

# Run CLI
python cli_interface.py
```

## 📖 Usage Guide

### Interactive CLI (Recommended)
```bash
python cli_interface.py
```

The interactive menu provides:
- Module selection via numbered menu
- Target input with validation
- Real-time progress tracking
- Results viewing and export
- Configuration management

### Command Line Interface

```bash
# Full intelligence pipeline
python master_orchestrator.py --target example.com

# Specific operations
python master_orchestrator.py --target example.com \
  --operations recon creds geo

# Adjust worker threads
python master_orchestrator.py --target example.com --workers 8

# Custom config
python master_orchestrator.py --target example.com \
  --config /path/to/config.yaml
```

### Individual Modules

**Reconnaissance:**
```bash
python elite_recon_module.py example.com \
  --config config.yaml \
  --output report.json
```

**Credential Harvesting:**
```bash
python elite_credential_harvester.py user@example.com \
  --type email \
  --output credentials.json
```

## 🔧 Configuration

Create `config.yaml` in the project root:

```yaml
# Database
mongodb_uri: "mongodb://localhost:27017"
redis_host: "localhost"
redis_port: 6379

# Performance
max_workers: 4
cache_ttl: 3600
enable_uvloop: true

# API Keys
api_keys:
  shodan_key: "your_key"
  censys_id: "your_id"
  virustotal_key: "your_key"
  # ... more keys ...

# Analysis
analysis:
  anomaly_threshold: 0.95
  correlation_threshold: 0.7
  risk_weights:
    vulnerabilities: 0.3
    exposures: 0.25
    breaches: 0.2
    infrastructure: 0.15
    reconnaissance: 0.1
```

See [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed configuration.

## 📊 Example Output

```json
{
  "target": "example.com",
  "timestamp": "2024-11-03T12:00:00",
  "risk_score": 65,
  "reconnaissance": {
    "dns": { "records": {...}, "zone_transfer": {...} },
    "whois": { "registrar": "...", "emails": [...] },
    "shodan": { "vulnerabilities": [...] },
    "github_exposure": { "total_findings": 5, "repositories": [...] }
  },
  "cloud_assets": {
    "aws_s3_buckets": [
      { "bucket": "example-prod", "status": "PUBLIC", "accessible": true }
    ]
  },
  "credentials_found": [
    { "username": "admin", "password": "...", "source": "dehashed" }
  ]
}
```

## 🎯 CTF & Security Testing

Hughes Clues excels at:
- **CTF Challenges** - Automated flag discovery
- **Penetration Testing** - Target reconnaissance
- **Security Research** - Vulnerability assessment
- **Threat Intelligence** - Risk scoring

See [CTF_GUIDE.md](CTF_GUIDE.md) for flag-hunting strategies.

## 📈 Performance Improvements

| Metric | Improvement |
|--------|------------|
| Memory Usage | 60% reduction |
| Operation Speed | 40% faster |
| Repeated Operations | 80-90% faster (cached) |
| Credential Testing | 10-20x faster (async) |

## 🔒 Security Considerations

- **Rate Limiting** - Respect API limits and target resources
- **Authentication** - Securely store API keys in `.env`
- **Legal Compliance** - Ensure proper authorization
- **Data Protection** - Encrypt sensitive intelligence
- **Network Ethics** - Respect rate limits and IDS/WAF

### Environment Variables
```bash
export CONFIG_FILE=/path/to/config.yaml
export APP_DIR=/app
export MODULES_DIR=/app/modules
```

## 📚 Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive reference manual
- **[QUICK_START.md](QUICK_START.md)** - 30-second quick reference
- **[CTF_GUIDE.md](CTF_GUIDE.md)** - CTF-specific strategies
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Technical improvements

## 🐛 Troubleshooting

### Module Not Found
```bash
export APP_DIR=$(pwd)
python cli_interface.py
```

### MongoDB Connection Failed
```bash
docker-compose up -d mongodb
docker-compose logs mongodb
```

### Rate Limit Errors
Already handled! Built-in rate limit management for:
- GitHub API (X-RateLimit headers)
- HIBP (1.5s delays)
- Custom API endpoints

See [USAGE_GUIDE.md#Troubleshooting](USAGE_GUIDE.md#troubleshooting) for more solutions.

## 🛠 Technology Stack

- **Python 3.8+** - Core framework
- **AsyncIO** - Asynchronous operations
- **MongoDB** - Document storage
- **Redis** - Caching layer
- **Docker** - Containerization
- **Rich** - Terminal UI (optional but recommended)

## 📦 Dependencies

Key packages:
- `aiohttp` - Async HTTP client
- `dnspython` - DNS operations
- `paramiko` - SSH protocol
- `selenium` - Browser automation
- `pymongo` - MongoDB driver
- `redis` - Redis client
- `rich` - Terminal formatting

See [requirements.txt](requirements.txt) for complete list.

## 🤝 Contributing

Contributions welcome! Areas needing help:
- Additional breach database integrations
- Improved geolocation algorithms
- Cloud provider SDKs (Azure, GCP)
- Web scraping optimizations
- Dark web monitoring enhancements

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## ⚖️ Disclaimer

**Hughes Clues is for authorized security testing only.**

Users are responsible for:
- Obtaining proper authorization before testing
- Compliance with applicable laws and regulations
- Ethical use of collected intelligence
- Respecting target systems and networks

The authors are not responsible for misuse or damage caused by this program.

## 🎯 Roadmap

- [ ] Web UI dashboard
- [ ] API endpoint for remote execution
- [ ] Machine learning-based threat scoring
- [ ] Automated report generation (PDF/HTML)
- [ ] Integration with SIEM systems
- [ ] Support for additional APIs (Censys, Shodan SDK)

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/hughes-clues/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hughes-clues/discussions)
- **Documentation**: See `docs/` directory
- **Email**: [your email if providing]

## 🙏 Acknowledgments

Built with inspiration from:
- Reconnaissance frameworks
- OSINT communities
- Security research best practices
- CTF challenge designers

---

<div align="center">

**Made with ❤️ by the Hughes Clues Team**

⭐ If you find this useful, please star the repository!

</div>
