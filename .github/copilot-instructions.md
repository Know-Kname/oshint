# OSHINT AI Agent Instructions

OSHINT is an advanced modular intelligence gathering system for conducting comprehensive OSINT operations. This guide covers essential knowledge for AI agents working in this codebase.

## Core Architecture

### Master Orchestrator (`master_orchestrator.py`)
- Central coordinator for all intelligence operations 
- Multi-threaded operation queue with priority support
- Dynamic module loading system
- Integrates with MongoDB (reports) and Redis (real-time updates)
- Manages worker threads, operation status, and system stats

### Intelligence Flow
1. Operations are queued via `MasterOrchestrator.run_full_intelligence_pipeline()`
2. Worker threads execute operations asynchronously
3. Results aggregate into `IntelligenceReport` objects
4. Reports persist to MongoDB with real-time updates to Redis

### Module System
- Modules prefixed with `elite_` focus on specific domains
- Each module provides an orchestrator class implementing:
  ```python
  class EliteModuleOrchestrator:
      def __init__(self, api_keys: Dict[str, str] = None)
      async def initialize(self)  # Optional setup
      async def cleanup(self)  # Resource cleanup 
      def generate_intelligence_report(self) # Report generation
  ```

### Key Integration Points
- MongoDB: Report storage (`hughes_clues` database)
- Redis: Real-time operation updates
- Tor: Dark web monitoring via control port
- APIs: Shodan, HaveIBeenPwned, DeHashed, etc.

## Development Workflows 

### Running Operations
```bash
# Full pipeline
python master_orchestrator.py --target example.com

# Specific operations 
python master_orchestrator.py --target example.com --operations recon scrape geo
```

### Configuration
- API keys in `/opt/hughes_clues/config.yaml`
- Redis and MongoDB connection settings
- Module-specific settings (timeouts, rate limits)
- Sample config structure in `deploy_hughes_clues.sh`

### Adding New Module
1. Create `elite_<module>.py` implementing standard interface
2. Add operation type to `OperationType` enum
3. Add execution handler in `MasterOrchestrator`
4. Update configuration as needed

## Project Patterns

### Asynchronous Operations
- Use `aiohttp` for HTTP requests
- Implement `cleanup()` for resource management
- Handle session lifecycle in modules

### Error Handling & Reporting
- Operations catch and report errors without crashing
- Failed operations marked in queue and stats
- Comprehensive logging with standardized format

### Intelligence Reports
- Structured via `IntelligenceReport` dataclass
- Risk scoring based on findings
- Multi-source data correlation

### Data Flows
1. Target specification
2. Module-specific intelligence gathering
3. Result aggregation and scoring
4. Report generation and storage

## Module-Specific Notes

### Reconnaissance (`elite_recon_module.py`)
- Multi-source intel gathering (Shodan, CT logs, GitHub, etc.)
- Automated risk scoring based on findings
- Technology fingerprinting

### Web Scraping (`elite_web_scraper.py`)
- Recursive crawling with depth control
- Caching support for efficiency
- Configurable scraping rules

### Dark Web Monitor (`elite_darkweb_monitor.py`)
- Tor circuit management
- Marketplace and paste site monitoring
- Identity rotation for anonymity
