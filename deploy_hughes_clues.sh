#!/bin/bash
###############################################################################
# HUGHES CLUES - ONE-COMMAND DEPLOYMENT SCRIPT
# Deploy entire OSINT platform with single command
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗                      ║
║   ╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝                      ║
║   ╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝                      ║
║                                                               ║
║              ELITE OSINT PLATFORM - DEPLOYMENT                ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Configuration
INSTALL_DIR="/opt/hughes_clues"
PYTHON_VERSION="3.11"
DOCKER_COMPOSE_VERSION="2.23.0"

# Functions
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
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_os() {
    if [[ -f /etc/debian_version ]]; then
        OS="debian"
        log_success "Detected Debian/Ubuntu system"
    elif [[ -f /etc/redhat-release ]]; then
        OS="redhat"
        log_success "Detected RedHat/CentOS system"
    else
        log_error "Unsupported operating system"
        exit 1
    fi
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    if [[ "$OS" == "debian" ]]; then
        apt-get update
        apt-get install -y \
            build-essential \
            cmake \
            git \
            wget \
            curl \
            python3.11 \
            python3.11-dev \
            python3.11-venv \
            python3-pip \
            libssl-dev \
            libffi-dev \
            libpq-dev \
            libxml2-dev \
            libxslt1-dev \
            libtins-dev \
            libpcap-dev \
            libgeoip-dev \
            tor \
            docker.io \
            docker-compose \
            postgresql-client \
            mongodb-clients \
            redis-tools \
            nmap \
            masscan \
            whois \
            dnsutils \
            net-tools \
            traceroute \
            chromium-browser \
            chromium-chromedriver
        
    elif [[ "$OS" == "redhat" ]]; then
        yum install -y epel-release
        yum install -y \
            gcc \
            gcc-c++ \
            cmake \
            git \
            wget \
            curl \
            python311 \
            python311-devel \
            openssl-devel \
            libffi-devel \
            postgresql-devel \
            libxml2-devel \
            libxslt-devel \
            docker \
            tor \
            nmap \
            whois \
            bind-utils
    fi
    
    log_success "System dependencies installed"
}

setup_docker() {
    log_info "Setting up Docker..."
    
    # Enable and start Docker
    systemctl enable docker
    systemctl start docker
    
    # Add current user to docker group (if running with sudo)
    if [ -n "$SUDO_USER" ]; then
        usermod -aG docker "$SUDO_USER"
        log_success "Added $SUDO_USER to docker group"
    fi
    
    # Install Docker Compose if not present
    if ! command -v docker-compose &> /dev/null; then
        log_info "Installing Docker Compose..."
        curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
    fi
    
    log_success "Docker configured"
}

create_directory_structure() {
    log_info "Creating directory structure..."
    
    mkdir -p "$INSTALL_DIR"/{modules,api,ui,data,logs,nginx,monitoring,init-scripts}
    mkdir -p "$INSTALL_DIR"/init-scripts/{postgres,mongodb}
    
    log_success "Directory structure created"
}

setup_python_environment() {
    log_info "Setting up Python environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    log_success "Python environment created"
}

install_python_packages() {
    log_info "Installing Python packages (this may take 10-15 minutes)..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # Install all required packages
    pip install \
        # Web frameworks
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        websockets==12.0 \
        aiohttp==3.9.1 \
        requests==2.31.0 \
        \
        # Database drivers
        pymongo==4.6.0 \
        psycopg2-binary==2.9.9 \
        redis==5.0.1 \
        neo4j==5.14.1 \
        elasticsearch==8.11.0 \
        \
        # AI/ML libraries
        torch==2.1.1 \
        transformers==4.35.2 \
        spacy==3.7.2 \
        face-recognition==1.3.0 \
        opencv-python==4.8.1.78 \
        numpy==1.26.2 \
        scipy==1.11.4 \
        scikit-learn==1.3.2 \
        \
        # Web scraping
        playwright==1.40.0 \
        selenium==4.15.2 \
        undetected-chromedriver==3.5.4 \
        beautifulsoup4==4.12.2 \
        lxml==4.9.3 \
        fake-useragent==1.4.0 \
        \
        # Network operations
        scapy==2.5.0 \
        dnspython==2.4.2 \
        python-nmap==0.7.1 \
        python-whois==0.8.0 \
        geoip2==4.7.0 \
        \
        # Tor/Dark web
        stem==1.8.2 \
        pysocks==1.7.1 \
        \
        # Crypto/Security
        cryptography==41.0.7 \
        bcrypt==4.1.1 \
        passlib==1.7.4 \
        pyjwt==2.8.0 \
        \
        # Utilities
        pyyaml==6.0.1 \
        python-dotenv==1.0.0 \
        click==8.1.7 \
        python-multipart==0.0.6 \
        pillow==10.1.0 \
        folium==0.15.0 \
        geopy==2.4.1 \
        networkx==3.2.1 \
        matplotlib==3.8.2 \
        \
        # API clients
        anthropic==0.7.7 \
        openai==1.3.7 \
        shodan==1.31.0 \
        \
        # Testing/Monitoring
        pytest==7.4.3 \
        psutil==5.9.6 \
        pydantic==2.5.2
    
    # Install spaCy model
    python -m spacy download en_core_web_lg
    
    # Install Playwright browsers
    playwright install chromium
    
    log_success "Python packages installed"
}

compile_cpp_modules() {
    log_info "Compiling C++ modules..."
    
    cd "$INSTALL_DIR"/exploits
    mkdir -p build
    cd build
    
    cmake ..
    make -j$(nproc)
    
    # Copy compiled modules to Python site-packages
    cp elite_network_ops*.so "$INSTALL_DIR"/venv/lib/python3.11/site-packages/
    
    log_success "C++ modules compiled"
}

configure_databases() {
    log_info "Configuring databases..."
    
    # Generate random passwords
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    MONGO_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    NEO4J_PASSWORD=$(openssl rand -base64 32)
    ELASTIC_PASSWORD=$(openssl rand -base64 32)
    TOR_PASSWORD=$(openssl rand -base64 32)
    GRAFANA_PASSWORD=$(openssl rand -base64 32)
    
    # Create .env file
    cat > "$INSTALL_DIR"/.env << EOF
# Hughes Clues Environment Configuration
# Generated on $(date)

# Database Passwords
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
MONGO_PASSWORD=$MONGO_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
NEO4J_PASSWORD=$NEO4J_PASSWORD
ELASTIC_PASSWORD=$ELASTIC_PASSWORD
TOR_PASSWORD=$TOR_PASSWORD
GRAFANA_PASSWORD=$GRAFANA_PASSWORD

# API Keys (add your keys here)
SHODAN_API_KEY=
HIBP_API_KEY=
DEHASHED_API_KEY=
SNUSBASE_API_KEY=
GOOGLE_GEOLOCATION_KEY=
IPINFO_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
EOF
    
    chmod 600 "$INSTALL_DIR"/.env
    
    log_success "Database configuration created"
    log_warn "IMPORTANT: Passwords saved to $INSTALL_DIR/.env"
}

create_config_file() {
    log_info "Creating configuration file..."
    
    cat > "$INSTALL_DIR"/config.yaml << 'EOF'
# Hughes Clues Configuration

# System Settings
max_workers: 4
log_level: INFO

# Database URIs
mongodb_uri: "mongodb://hughes_admin:${MONGO_PASSWORD}@localhost:27017"
postgres_uri: "postgresql://hughes_admin:${POSTGRES_PASSWORD}@localhost:5432/hughes_clues"
redis_host: "localhost"
redis_port: 6379
neo4j_uri: "bolt://localhost:7687"
elasticsearch_host: "localhost:9200"

# Tor Settings
tor_socks_port: 9050
tor_control_port: 9051
tor_password: "${TOR_PASSWORD}"

# API Keys (configure in .env file)
api_keys:
  shodan: "${SHODAN_API_KEY}"
  hibp: "${HIBP_API_KEY}"
  dehashed: "${DEHASHED_API_KEY}"
  snusbase: "${SNUSBASE_API_KEY}"
  google_geolocation: "${GOOGLE_GEOLOCATION_KEY}"
  ipinfo: "${IPINFO_API_KEY}"
  anthropic: "${ANTHROPIC_API_KEY}"
  openai: "${OPENAI_API_KEY}"

# Module Settings
reconnaissance:
  timeout: 30
  max_retries: 3

web_scraping:
  headless: true
  max_depth: 3
  delay_min: 1.0
  delay_max: 3.0

credential_harvest:
  rate_limit: 1.0

geolocation:
  cache_ttl: 3600

dark_web:
  circuit_renew_interval: 600
  max_crawl_depth: 2

self_improvement:
  enabled: true
  check_interval: 86400  # 24 hours
  min_improvement_threshold: 10.0
EOF
    
    log_success "Configuration file created"
}

start_services() {
    log_info "Starting services with Docker Compose..."
    
    cd "$INSTALL_DIR"
    
    # Load environment variables
    export $(cat .env | xargs)
    
    # Start all services
    docker-compose up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy (this may take 2-3 minutes)..."
    sleep 30
    
    # Check service health
    docker-compose ps
    
    log_success "All services started"
}

create_systemd_service() {
    log_info "Creating systemd service..."
    
    cat > /etc/systemd/system/hughes-clues.service << EOF
[Unit]
Description=Hughes Clues OSINT Platform
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=root

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable hughes-clues.service
    
    log_success "Systemd service created and enabled"
}

display_completion_message() {
    echo ""
    echo -e "${GREEN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║              🎉 DEPLOYMENT COMPLETE! 🎉                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Access Points:${NC}"
    echo -e "  🌐 Dashboard:     ${GREEN}http://localhost:3000${NC}"
    echo -e "  🔧 API:          ${GREEN}http://localhost:8000${NC}"
    echo -e "  📊 API Docs:     ${GREEN}http://localhost:8000/api/docs${NC}"
    echo -e "  📈 Grafana:      ${GREEN}http://localhost:3001${NC}"
    echo -e "  🔍 Elasticsearch:${GREEN}http://localhost:9200${NC}"
    echo -e "  🕸️  Neo4j:        ${GREEN}http://localhost:7474${NC}"
    echo ""
    echo -e "${YELLOW}Credentials saved in:${NC} ${GREEN}$INSTALL_DIR/.env${NC}"
    echo ""
    echo -e "${YELLOW}Useful Commands:${NC}"
    echo -e "  Start services:  ${CYAN}cd $INSTALL_DIR && docker-compose up -d${NC}"
    echo -e "  Stop services:   ${CYAN}cd $INSTALL_DIR && docker-compose down${NC}"
    echo -e "  View logs:       ${CYAN}cd $INSTALL_DIR && docker-compose logs -f${NC}"
    echo -e "  System status:   ${CYAN}systemctl status hughes-clues${NC}"
    echo ""
    echo -e "${YELLOW}Run Intelligence Operation:${NC}"
    echo -e "  ${CYAN}source $INSTALL_DIR/venv/bin/activate${NC}"
    echo -e "  ${CYAN}python master_orchestrator.py --target example.com${NC}"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${PURPLE}⚠️  IMPORTANT SECURITY NOTES:${NC}"
    echo -e "  1. Change default passwords in ${GREEN}.env${NC} file"
    echo -e "  2. Configure firewall rules for production"
    echo -e "  3. Add your API keys to ${GREEN}config.yaml${NC}"
    echo -e "  4. Review and customize module settings"
    echo ""
    echo -e "${YELLOW}Documentation:${NC} ${GREEN}$INSTALL_DIR/README.md${NC}"
    echo ""
}

# Main deployment flow
main() {
    log_info "Starting Hughes Clues deployment..."
    
    check_root
    check_os
    install_dependencies
    setup_docker
    create_directory_structure
    setup_python_environment
    install_python_packages
    
    # Only compile C++ if modules exist
    if [ -d "$INSTALL_DIR/exploits" ]; then
        compile_cpp_modules
    else
        log_warn "C++ modules directory not found, skipping compilation"
    fi
    
    configure_databases
    create_config_file
    start_services
    create_systemd_service
    
    display_completion_message
    
    log_success "Hughes Clues deployment completed successfully!"
}

# Run main function
main
