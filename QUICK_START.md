# Hughes Clues - Quick Start Guide for CTF

## 30-Second Setup

```bash
# Clone/navigate to directory
cd Hughes\ Clues

# Start Docker services
docker-compose up -d

# Wait for services to be healthy (30 seconds)
docker-compose ps

# Run reconnaissance on target
python master_orchestrator.py --target TARGET_DOMAIN.com
```

## Immediate Results

Check MongoDB for results:
```bash
# Access MongoDB
docker-compose exec mongodb mongosh

# View intelligence reports
> use hughes_clues
> db.reports.findOne()

# View operations
> db.operations.findOne()

# Search for specific targets
> db.reports.find({"report.target": "example.com"})
```

## Quick Command Reference

### Reconnaissance Only
```bash
python master_orchestrator.py --target example.com --operations recon
```

### Credential Harvesting
```bash
python elite_credential_harvester.py user@example.com --type email --output creds.json
```

### Direct Module Usage
```bash
# Recon report
python elite_recon_module.py example.com -o report.json

# Analysis
python elite_analysis_engine.py report.json
```

## Finding CTF Flags

Look in the intelligence reports for:

1. **GitHub Secrets** → `github_exposure.repositories[]`
   - API keys, tokens, passwords
   - .env files, config files

2. **Cloud Buckets** → `cloud_assets.aws_s3_buckets[]`
   - Public data exposure
   - Misconfigured permissions

3. **Breach Credentials** → `credentials_found[]`
   - Plaintext passwords
   - Hash cracking results

4. **Network Info** → `reconnaissance.shodan`
   - Open ports revealing services
   - Version information for exploits

5. **DNS/Zone Transfer** → `reconnaissance.dns.zone_transfer`
   - Hidden subdomains
   - Server configuration details

## System Status

```bash
# Check if everything is running
docker-compose ps

# View logs in real-time
docker-compose logs -f orchestrator

# Stop all services
docker-compose down

# Clean slate
docker-compose down -v
```

## Performance Tips

1. **Multiple Targets**: Run in parallel with multiple workers
   ```bash
   python master_orchestrator.py --target domain1.com --workers 8 &
   python master_orchestrator.py --target domain2.com --workers 8 &
   ```

2. **Cached Results**: Redis automatically caches for 1 hour
   - Faster re-runs on same target
   - Check `redis-cli` to view cache

3. **Selective Operations**: Run only needed intelligence
   ```bash
   # Fast recon only
   python master_orchestrator.py --target example.com --operations recon

   # Add credentials after
   python master_orchestrator.py --target example.com --operations creds geo
   ```

## Debugging

```bash
# Enable debug logging
DEBUG=1 python master_orchestrator.py --target example.com

# Check worker status
docker-compose logs orchestrator | grep "Worker"

# Monitor Redis cache
docker-compose exec redis redis-cli monitor

# Verify config
cat config.yaml
```

## Known Flag Locations (CTF Patterns)

- **Exposed .env files** → GitHub dorking
- **Hardcoded credentials** → Breach database queries
- **SSH keys** → S3 bucket discovery
- **Admin panels** → Technology fingerprinting (find CMS)
- **API endpoints** → DNS enumeration + subdomain discovery
- **Database dumps** → Paste site monitoring (dark web)
- **Source code** → GitHub exposure detection
- **Configuration files** → Cloud bucket scanning

---

**Time to first result: ~2-5 minutes**

For detailed usage, see [USAGE_GUIDE.md](USAGE_GUIDE.md)
