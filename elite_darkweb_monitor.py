#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

Elite Dark Web Monitor
Tor Integration | Onion Site Crawling | Marketplace Monitoring | Paste Sites | I2P
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import stem
from stem import Signal
from stem.control import Controller
import socks
import socket
from urllib.parse import urlparse, urljoin
import hashlib
import time
from collections import defaultdict
import logging
from pymongo import MongoClient
from elasticsearch import Elasticsearch
import redis
from fake_useragent import UserAgent
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OnionSite:
    """Onion site information"""
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: str = "unknown"
    last_seen: Optional[str] = None
    first_discovered: Optional[str] = None
    content_hash: Optional[str] = None
    links: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    bitcoin_addresses: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)


@dataclass
class MarketplaceListing:
    """Marketplace listing data"""
    marketplace: str
    vendor: str
    product_name: str
    price: float
    currency: str
    description: str
    category: str
    rating: Optional[float] = None
    sales_count: Optional[int] = None
    url: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DarkWebIntel:
    """Dark web intelligence summary"""
    keywords_found: Dict[str, int] = field(default_factory=dict)
    sites_monitored: int = 0
    new_sites_discovered: int = 0
    marketplaces_active: int = 0
    paste_entries: int = 0
    bitcoin_addresses: Set[str] = field(default_factory=set)
    threat_indicators: List[str] = field(default_factory=list)


class TorController:
    """Control Tor connection and circuit management"""
    
    def __init__(self, control_port: int = 9051, socks_port: int = 9050, password: str = None):
        self.control_port = control_port
        self.socks_port = socks_port
        self.password = password
        self.controller = None
        self.session = None
        
    def connect(self):
        """Connect to Tor control port"""
        try:
            self.controller = Controller.from_port(port=self.control_port)
            self.controller.authenticate(password=self.password)
            logger.info("[+] Connected to Tor control port")
            return True
        except Exception as e:
            logger.error(f"[!] Tor connection error: {str(e)}")
            return False
    
    def new_circuit(self):
        """Request new Tor circuit (new identity)"""
        if not self.controller:
            return False
        
        try:
            self.controller.signal(Signal.NEWNYM)
            logger.info("[+] New Tor circuit established")
            time.sleep(5)  # Wait for circuit to establish
            return True
        except Exception as e:
            logger.error(f"[!] Circuit renewal error: {str(e)}")
            return False
    
    def get_current_ip(self) -> Optional[str]:
        """Get current Tor exit node IP"""
        try:
            proxies = {
                'http': f'socks5h://127.0.0.1:{self.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.socks_port}'
            }
            response = requests.get('https://check.torproject.org/api/ip', proxies=proxies, timeout=10)
            if response.status_code == 200:
                data = response.json()
                ip = data.get('IP')
                logger.info(f"[*] Current Tor IP: {ip}")
                return ip
        except Exception as e:
            logger.debug(f"[!] IP check error: {str(e)}")
        return None
    
    async def create_session(self) -> aiohttp.ClientSession:
        """Create aiohttp session with Tor proxy"""
        connector = aiohttp.TCPConnector()
        
        # Configure SOCKS proxy
        proxy = f'socks5://127.0.0.1:{self.socks_port}'
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            headers={'User-Agent': UserAgent().random}
        )
        
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def disconnect(self):
        """Disconnect from Tor"""
        if self.controller:
            self.controller.close()
            logger.info("[*] Disconnected from Tor")


class OnionCrawler:
    """Crawl .onion sites"""
    
    def __init__(self, tor_controller: TorController):
        self.tor = tor_controller
        self.visited_urls: Set[str] = set()
        self.discovered_sites: List[OnionSite] = []
        self.session = None
        
    async def crawl_onion(self, onion_url: str, max_depth: int = 2) -> OnionSite:
        """Crawl a .onion site"""
        logger.info(f"[*] Crawling onion: {onion_url}")
        
        if onion_url in self.visited_urls:
            return None
        
        self.visited_urls.add(onion_url)
        
        try:
            # Configure SOCKS proxy for requests
            proxies = {
                'http': f'socks5h://127.0.0.1:{self.tor.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.tor.socks_port}'
            }
            
            response = requests.get(
                onion_url,
                proxies=proxies,
                timeout=30,
                headers={'User-Agent': UserAgent().random}
            )
            
            if response.status_code != 200:
                logger.warning(f"[!] Site returned status {response.status_code}")
                return None
            
            # Parse content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            site = OnionSite(
                url=onion_url,
                title=soup.title.string if soup.title else None,
                status='online',
                last_seen=datetime.now().isoformat(),
                first_discovered=datetime.now().isoformat(),
                content_hash=hashlib.sha256(response.text.encode()).hexdigest()
            )
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                site.description = meta_desc.get('content', '')
            
            # Extract all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Handle relative URLs
                if href.startswith('/'):
                    href = urljoin(onion_url, href)
                
                if '.onion' in href and href not in self.visited_urls:
                    site.links.append(href)
            
            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            site.emails = list(set(re.findall(email_pattern, response.text)))
            
            # Extract Bitcoin addresses
            btc_pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
            site.bitcoin_addresses = list(set(re.findall(btc_pattern, response.text)))
            
            # Extract text content for keyword analysis
            text_content = soup.get_text()
            
            # Keyword extraction (simple frequency-based)
            words = re.findall(r'\b[a-z]{4,}\b', text_content.lower())
            word_freq = defaultdict(int)
            for word in words:
                word_freq[word] += 1
            
            # Top 20 keywords
            site.keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            site.keywords = [w[0] for w in site.keywords]
            
            logger.info(f"[+] Crawled {onion_url}: {len(site.links)} links, {len(site.emails)} emails")
            
            self.discovered_sites.append(site)
            
            # Recursively crawl linked .onion sites (if depth allows)
            if max_depth > 0:
                for linked_url in site.links[:5]:  # Limit to 5 per site
                    await asyncio.sleep(2)  # Rate limiting
                    await self.crawl_onion(linked_url, max_depth - 1)
            
            return site
            
        except requests.exceptions.Timeout:
            logger.warning(f"[!] Timeout accessing {onion_url}")
        except Exception as e:
            logger.error(f"[!] Crawl error for {onion_url}: {str(e)}")
        
        return None
    
    async def crawl_multiple(self, onion_urls: List[str], max_depth: int = 1):
        """Crawl multiple onion sites"""
        tasks = [self.crawl_onion(url, max_depth) for url in onion_urls]
        await asyncio.gather(*tasks, return_exceptions=True)


class MarketplaceMonitor:
    """Monitor dark web marketplaces"""
    
    def __init__(self, tor_controller: TorController):
        self.tor = tor_controller
        self.marketplace_configs = self.load_marketplace_configs()
        self.listings: List[MarketplaceListing] = []
    
    def load_marketplace_configs(self) -> Dict:
        """Load marketplace scraping configurations"""
        return {
            'empire': {
                'url': 'http://empiremktxgjovhm.onion',
                'search_path': '/search?q={}',
                'selectors': {
                    'product': '.product-item',
                    'name': '.product-name',
                    'price': '.product-price',
                    'vendor': '.vendor-name'
                }
            },
            'whitehouse': {
                'url': 'http://whitehouse72762etjnhm.onion',
                'search_path': '/search?q={}',
                'selectors': {
                    'product': '.listing',
                    'name': 'h3.title',
                    'price': '.price',
                    'vendor': '.vendor'
                }
            }
            # Add more marketplaces as needed
        }
    
    async def monitor_marketplace(self, marketplace_name: str, search_terms: List[str]) -> List[MarketplaceListing]:
        """Monitor specific marketplace for keywords"""
        
        if marketplace_name not in self.marketplace_configs:
            logger.warning(f"[!] Unknown marketplace: {marketplace_name}")
            return []
        
        config = self.marketplace_configs[marketplace_name]
        listings = []
        
        proxies = {
            'http': f'socks5h://127.0.0.1:{self.tor.socks_port}',
            'https': f'socks5h://127.0.0.1:{self.tor.socks_port}'
        }
        
        for term in search_terms:
            try:
                logger.info(f"[*] Searching {marketplace_name} for '{term}'")
                
                search_url = config['url'] + config['search_path'].format(term)
                response = requests.get(search_url, proxies=proxies, timeout=30)
                
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract listings based on selectors
                products = soup.select(config['selectors']['product'])
                
                for product in products[:20]:  # Limit to 20 per search
                    try:
                        name = product.select_one(config['selectors']['name']).text.strip()
                        price_text = product.select_one(config['selectors']['price']).text.strip()
                        vendor = product.select_one(config['selectors']['vendor']).text.strip()
                        
                        # Parse price (assuming format: $XXX or XXX USD)
                        price_match = re.search(r'[\d.]+', price_text)
                        price = float(price_match.group()) if price_match else 0.0
                        
                        listing = MarketplaceListing(
                            marketplace=marketplace_name,
                            vendor=vendor,
                            product_name=name,
                            price=price,
                            currency='USD',
                            description='',
                            category=term,
                            url=search_url
                        )
                        
                        listings.append(listing)
                        logger.info(f"[+] Found listing: {name} by {vendor} - ${price}")
                        
                    except Exception as e:
                        logger.debug(f"[!] Listing parse error: {str(e)}")
                        continue
                
                await asyncio.sleep(3)  # Rate limiting between searches
                
            except Exception as e:
                logger.error(f"[!] Marketplace monitor error: {str(e)}")
        
        self.listings.extend(listings)
        return listings


class PasteSiteMonitor:
    """Monitor paste sites for intelligence"""
    
    def __init__(self, tor_controller: TorController):
        self.tor = tor_controller
        self.paste_sites = [
            'http://strongerw2ise74v3duebgsvug4mehyhlpa7f6kfwnas7zofs3kov7yd.onion',  # Stronghold
            'http://nzxj65x32vh2fkhk.onion'  # OnionPaste (example)
        ]
        self.pastes: List[Dict] = []
    
    async def monitor_pastes(self, keywords: List[str]) -> List[Dict]:
        """Monitor paste sites for keywords"""
        
        proxies = {
            'http': f'socks5h://127.0.0.1:{self.tor.socks_port}',
            'https': f'socks5h://127.0.0.1:{self.tor.socks_port}'
        }
        
        for site_url in self.paste_sites:
            try:
                logger.info(f"[*] Monitoring paste site: {site_url}")
                
                response = requests.get(site_url, proxies=proxies, timeout=30)
                
                if response.status_code != 200:
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract recent pastes
                paste_links = soup.find_all('a', href=re.compile(r'/paste/'))
                
                for link in paste_links[:50]:  # Check last 50 pastes
                    paste_url = urljoin(site_url, link['href'])
                    
                    # Get paste content
                    paste_response = requests.get(paste_url, proxies=proxies, timeout=20)
                    if paste_response.status_code != 200:
                        continue
                    
                    paste_content = paste_response.text
                    
                    # Check for keywords
                    found_keywords = []
                    for keyword in keywords:
                        if keyword.lower() in paste_content.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        paste_data = {
                            'url': paste_url,
                            'content': paste_content[:1000],  # First 1000 chars
                            'keywords': found_keywords,
                            'timestamp': datetime.now().isoformat(),
                            'source': site_url
                        }
                        
                        self.pastes.append(paste_data)
                        logger.info(f"[+] Found paste with keywords: {found_keywords}")
                    
                    await asyncio.sleep(1)  # Rate limiting
                
            except Exception as e:
                logger.error(f"[!] Paste monitoring error: {str(e)}")
        
        return self.pastes


class EliteDarkWebMonitor:
    """Master dark web monitoring orchestrator"""
    
    def __init__(self, tor_password: str = None):
        self.tor = TorController(password=tor_password)
        self.crawler = None
        self.marketplace_monitor = None
        self.paste_monitor = None
        self.intel = DarkWebIntel()
        
        # Storage
        self.mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = self.mongo_client['hughes_clues']
        self.darkweb_collection = self.db['darkweb']
        
        # Elasticsearch for full-text search
        try:
            self.es = Elasticsearch(['http://localhost:9200'])
            logger.info("[+] Connected to Elasticsearch")
        except Exception as e:
            self.es = None
            logger.warning(f"[!] Elasticsearch not available: {str(e)}")
        
        # Redis for caching
        try:
            self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
            logger.info("[+] Connected to Redis")
        except Exception as e:
            self.redis = None
            logger.warning(f"[!] Redis connection failed: {str(e)}")
    
    async def initialize(self) -> bool:
        """Initialize Tor and monitoring components"""
        if not self.tor.connect():
            return False
        
        # Verify Tor connection
        ip = self.tor.get_current_ip()
        if not ip:
            logger.error("[!] Failed to establish Tor connection")
            return False
        
        self.crawler = OnionCrawler(self.tor)
        self.marketplace_monitor = MarketplaceMonitor(self.tor)
        self.paste_monitor = PasteSiteMonitor(self.tor)
        
        logger.info("[+] Dark web monitor initialized")
        return True
    
    async def discover_onion_sites(self, seed_urls: List[str], max_depth: int = 2):
        """Discover and crawl onion sites"""
        logger.info(f"[*] Starting onion site discovery from {len(seed_urls)} seeds")
        
        await self.crawler.crawl_multiple(seed_urls, max_depth)
        
        self.intel.sites_monitored = len(self.crawler.visited_urls)
        self.intel.new_sites_discovered = len(self.crawler.discovered_sites)
        
        # Store in database
        for site in self.crawler.discovered_sites:
            self.darkweb_collection.insert_one({
                'type': 'onion_site',
                'data': site.__dict__,
                'timestamp': datetime.now().isoformat()
            })
            
            # Index in Elasticsearch
            if self.es:
                self.es.index(
                    index='darkweb',
                    document={
                        'url': site.url,
                        'title': site.title,
                        'content': site.description,
                        'keywords': site.keywords,
                        'timestamp': datetime.now().isoformat()
                    }
                )
        
        logger.info(f"[+] Discovered {self.intel.new_sites_discovered} onion sites")
    
    async def monitor_marketplaces(self, marketplaces: List[str], search_terms: List[str]):
        """Monitor dark web marketplaces"""
        logger.info(f"[*] Monitoring {len(marketplaces)} marketplaces for {len(search_terms)} terms")
        
        all_listings = []
        for marketplace in marketplaces:
            listings = await self.marketplace_monitor.monitor_marketplace(marketplace, search_terms)
            all_listings.extend(listings)
        
        self.intel.marketplaces_active = len(marketplaces)
        
        # Store listings
        for listing in all_listings:
            self.darkweb_collection.insert_one({
                'type': 'marketplace_listing',
                'data': listing.__dict__,
                'timestamp': datetime.now().isoformat()
            })
        
        logger.info(f"[+] Found {len(all_listings)} marketplace listings")
        return all_listings
    
    async def monitor_paste_sites(self, keywords: List[str]):
        """Monitor paste sites for intelligence"""
        logger.info(f"[*] Monitoring paste sites for {len(keywords)} keywords")
        
        pastes = await self.paste_monitor.monitor_pastes(keywords)
        
        self.intel.paste_entries = len(pastes)
        
        # Store pastes
        for paste in pastes:
            self.darkweb_collection.insert_one({
                'type': 'paste',
                'data': paste,
                'timestamp': datetime.now().isoformat()
            })
        
        logger.info(f"[+] Found {len(pastes)} relevant pastes")
        return pastes
    
    def generate_intelligence_report(self, output_file: str = None) -> str:
        """Generate comprehensive dark web intelligence report"""
        
        if output_file is None:
            output_file = f"darkweb_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'sites_monitored': self.intel.sites_monitored,
                'new_sites_discovered': self.intel.new_sites_discovered,
                'marketplaces_active': self.intel.marketplaces_active,
                'paste_entries': self.intel.paste_entries,
                'bitcoin_addresses_found': len(self.intel.bitcoin_addresses)
            },
            'discovered_sites': [site.__dict__ for site in self.crawler.discovered_sites if self.crawler],
            'marketplace_listings': [listing.__dict__ for listing in self.marketplace_monitor.listings if self.marketplace_monitor],
            'paste_intelligence': self.paste_monitor.pastes if self.paste_monitor else [],
            'threat_indicators': self.intel.threat_indicators
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"[+] Intelligence report saved to {output_file}")
        return output_file
    
    def rotate_identity(self):
        """Rotate Tor identity for anonymity"""
        logger.info("[*] Rotating Tor identity...")
        self.tor.new_circuit()
    
    async def cleanup(self):
        """Cleanup resources"""
        self.tor.disconnect()
        self.mongo_client.close()
        if self.redis:
            self.redis.close()


async def main():
    """Demo execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hughes Clues Elite Dark Web Monitor')
    parser.add_argument('--mode', choices=['discover', 'marketplaces', 'pastes', 'all'], default='all')
    parser.add_argument('--seeds', nargs='+', help='Seed onion URLs')
    parser.add_argument('--keywords', nargs='+', help='Keywords to monitor')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--tor-password', help='Tor control port password')
    
    args = parser.parse_args()
    
    monitor = EliteDarkWebMonitor(tor_password=args.tor_password)
    
    try:
        if not await monitor.initialize():
            logger.error("[!] Failed to initialize dark web monitor")
            return
        
        # Default seeds if none provided
        seeds = args.seeds or [
            'http://thehiddenwiki.onion',
            'http://darkfailenbsdla5mal2mxn2uz66od5vtzd5qozslagrfzachha3f3id.onion'
        ]
        
        keywords = args.keywords or ['drugs', 'weapons', 'stolen', 'hacked', 'database']
        
        if args.mode in ['discover', 'all']:
            await monitor.discover_onion_sites(seeds, max_depth=2)
        
        if args.mode in ['marketplaces', 'all']:
            await monitor.monitor_marketplaces(['empire', 'whitehouse'], keywords)
        
        if args.mode in ['pastes', 'all']:
            await monitor.monitor_paste_sites(keywords)
        
        # Generate report
        monitor.generate_intelligence_report(args.output)
        
        print(f"\n{'='*60}")
        print("DARK WEB INTELLIGENCE SUMMARY")
        print(f"{'='*60}")
        print(f"Sites monitored: {monitor.intel.sites_monitored}")
        print(f"New sites discovered: {monitor.intel.new_sites_discovered}")
        print(f"Marketplaces active: {monitor.intel.marketplaces_active}")
        print(f"Paste entries: {monitor.intel.paste_entries}")
        
    finally:
        await monitor.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
