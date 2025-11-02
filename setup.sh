#!/bin/bash

###############################################################################
# HUGHES CLUES - ADVANCED OSINT PLATFORM SETUP
# Comprehensive setup script with error handling and validation
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║   ╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗                      ║
║   ╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝                      ║
║   ╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝                      ║
║                                                               ║
║              ELITE OSINT PLATFORM - SETUP                     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Utility functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is required but not installed. Please install it first."
    fi
}

# Environment setup
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TOOLS_DIR="$SCRIPT_DIR/tools"
VENV_DIR="$SCRIPT_DIR/venv"
CONFIG_DIR="$SCRIPT_DIR/config"
LOG_DIR="$SCRIPT_DIR/logs"

# Ensure running with correct permissions
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run with sudo or as root"
    fi
fi

# Install required packages
log_info "Installing system requirements..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu systems
    apt-get update
    apt-get install -y git python3 python3-pip python3-venv \
        wget curl tor nmap chromium-browser \
        build-essential libssl-dev libffi-dev python3-dev \
        chromium-chromedriver
elif command -v yum &> /dev/null; then
    # RHEL/CentOS systems
    yum install -y git python3 python3-pip python3-virtualenv \
        wget curl tor nmap chromium chromedriver \
        gcc openssl-devel bzip2-devel libffi-devel
else
    log_error "Unsupported package manager. Please install dependencies manually."
fi

# Check essential commands
log_info "Verifying system requirements..."
REQUIRED_COMMANDS=(
    "git" "python3" "pip3" "wget" "curl" "tor" "nmap"
)

for cmd in "${REQUIRED_COMMANDS[@]}"; do
    check_command "$cmd"
done

# Create directory structure
log_info "Creating directory structure..."
mkdir -p "$TOOLS_DIR" "$CONFIG_DIR" "$LOG_DIR" "$SCRIPT_DIR/scripts"
mkdir -p "$CONFIG_DIR/modules" "$CONFIG_DIR/api_keys"

# Set up Python virtual environment
log_info "Setting up Python virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

# Source the virtual environment with error handling
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    log_error "Virtual environment activation script not found"
fi

# Verify Python environment
if ! python3 -c "import sys; sys.exit(0 if sys.prefix != sys.base_prefix else 1)"; then
    log_error "Virtual environment not properly activated"
fi

# Upgrade pip and install basic tools
log_info "Upgrading pip and installing wheel..."
python3 -m pip install --upgrade pip wheel setuptools

# Install Python dependencies
log_info "Installing Python dependencies..."
pip install --upgrade pip

# Create requirements file
cat > "$SCRIPT_DIR/requirements.txt" << EOF
# Web and API
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
aiohttp>=3.9.1
requests>=2.31.0
websockets>=12.0

# Database
pymongo>=4.6.0
redis>=5.0.1
elasticsearch>=8.11.0

# OSINT Tools
shodan>=1.31.0
censys>=2.2.8
dnspython>=2.4.2
python-whois>=0.8.0
builtwith>=1.3.4

# Web Scraping
selenium>=4.15.2
beautifulsoup4>=4.12.2
playwright>=1.40.0
fake-useragent>=1.4.0

# Network
scapy>=2.5.0
python-nmap>=0.7.1
geoip2>=4.7.0

# AI/ML
torch>=2.1.1
transformers>=4.35.2
spacy>=3.7.2

# Security
cryptography>=41.0.7
pyjwt>=2.8.0

# Utils
pyyaml>=6.0.1
python-dotenv>=1.0.0
tqdm>=4.66.1
colorama>=0.4.6

# Testing
pytest>=7.4.3
pytest-asyncio>=0.21.1
EOF

pip install -r "$SCRIPT_DIR/requirements.txt"

# Install spaCy model
log_info "Installing spaCy language model..."
python -m spacy download en_core_web_lg

# Set up OSINT tools
log_info "Setting up OSINT tools..."

# Initialize git submodules if not already done
if [ ! -f "$SCRIPT_DIR/.gitmodules" ]; then
    git init
fi

# Function to safely clone or update repositories
clone_or_update_repo() {
    local repo_url="$1"
    local target_dir="$2"
    
    if [ ! -d "$target_dir" ]; then
        git clone "$repo_url" "$target_dir" || {
            if [ -d "$target_dir" ]; then
                rm -rf "$target_dir"
                git clone "$repo_url" "$target_dir"
            fi
        }
    else
        (cd "$target_dir" && git pull origin master)
    fi
}

# Add essential OSINT tools
OSINT_TOOLS=(
    "git://github.com/sherlock-project/sherlock.git:sherlock"
    "git://github.com/soxoj/maigret.git:maigret"
    "git://github.com/lanmaster53/recon-ng.git:recon-ng"
    "git://github.com/smicallef/spiderfoot.git:spiderfoot"
    "git://github.com/laramies/theHarvester.git:theHarvester"
)

for tool in "${OSINT_TOOLS[@]}"; do
    IFS=':' read -r repo_url tool_name <<< "$tool"
    tool_dir="$TOOLS_DIR/$tool_name"
    log_info "Setting up $tool_name..."
    clone_or_update_repo "$repo_url" "$tool_dir"
    
    # Install tool-specific requirements if they exist
    if [ -f "$tool_dir/requirements.txt" ]; then
        pip install -r "$tool_dir/requirements.txt"
    fi
done

# Generate default configuration
log_info "Creating default configuration..."
cat > "$CONFIG_DIR/config.yaml" << EOF
# Hughes Clues Configuration

# System Settings
max_workers: 4
log_level: INFO
debug_mode: false

# Database URIs
mongodb_uri: "mongodb://localhost:27017/hughes_clues"
redis_uri: "redis://localhost:6379"
elasticsearch_uri: "http://localhost:9200"

# API Settings
api_rate_limit: 100
api_timeout: 30

# Module Settings
reconnaissance:
  timeout: 30
  max_retries: 3
  parallel_scans: 2

web_scraping:
  headless: true
  max_depth: 3
  delay_min: 1.0
  delay_max: 3.0
  user_agents_rotate: true
  respect_robots_txt: true

credential_harvest:
  rate_limit: 1.0
  max_breach_age_days: 365

geolocation:
  cache_ttl: 3600
  max_radius_km: 50

dark_web:
  circuit_renew_interval: 600
  max_crawl_depth: 2
  tor_timeout: 120

ai_analysis:
  model: "gpt-4"
  temperature: 0.7
  max_tokens: 2000

monitoring:
  enabled: true
  stats_interval: 60
  alert_threshold: 0.8
EOF

# Create empty API keys file (to be filled by user)
cat > "$CONFIG_DIR/api_keys.env" << EOF
# API Keys Configuration
# Replace with your actual API keys

SHODAN_API_KEY=
CENSYS_API_ID=
CENSYS_API_SECRET=
VIRUSTOTAL_API_KEY=
SECURITY_TRAILS_API_KEY=
HAVEIBEENPWNED_API_KEY=
GOOGLE_API_KEY=
BING_API_KEY=
OPENAI_API_KEY=
EOF

# Set correct permissions
log_info "Setting permissions..."
find "$SCRIPT_DIR/scripts" -type f -name "*.sh" -exec chmod +x {} \;
chmod 600 "$CONFIG_DIR/api_keys.env"

# Create helper scripts
log_info "Creating helper scripts..."
cat > "$SCRIPT_DIR/activate.sh" << EOF
#!/bin/bash
source "$VENV_DIR/bin/activate"
export PYTHONPATH="$SCRIPT_DIR:\$PYTHONPATH"
export HUGHES_CLUES_CONFIG="$CONFIG_DIR/config.yaml"
export HUGHES_CLUES_API_KEYS="$CONFIG_DIR/api_keys.env"
EOF
chmod +x "$SCRIPT_DIR/activate.sh"

# Final setup steps
log_success "HUGHES CLUES setup completed successfully!"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Configure your API keys in:    ${GREEN}$CONFIG_DIR/api_keys.env${NC}"
echo -e "2. Review configuration in:       ${GREEN}$CONFIG_DIR/config.yaml${NC}"
echo -e "3. Activate environment:          ${GREEN}source ./activate.sh${NC}"
echo -e "4. Run test suite:                ${GREEN}pytest tests/${NC}"
echo -e "5. Start intelligence gathering:  ${GREEN}python master_orchestrator.py --target example.com${NC}"
echo -e "\n${YELLOW}Documentation:${NC} See README.md for detailed usage instructions"

# Cleanup
deactivate
