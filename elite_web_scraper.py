#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

Elite Web Scraper - Advanced Stealth Intelligence Collection
Anti-Detection | Proxy Rotation | JavaScript Rendering | CAPTCHA Bypass
"""

import asyncio
import aiohttp
from playwright.async_api import async_playwright, Page, Browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
import json
import random
import time
from datetime import datetime
import re
from urllib.parse import urljoin, urlparse, parse_qs
import hashlib
from fake_useragent import UserAgent
import logging
from pymongo import MongoClient
from redis import Redis
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    """Scraper configuration"""
    use_proxies: bool = True
    proxy_list: List[str] = None
    headless: bool = True
    stealth_mode: bool = True
    javascript_enabled: bool = True
    max_depth: int = 3
    delay_min: float = 1.0
    delay_max: float = 3.0
    user_agent_rotation: bool = True
    captcha_solving: bool = False
    mongodb_uri: str = "mongodb://localhost:27017"
    redis_host: str = "localhost"
    redis_port: int = 6379


class ProxyRotator:
    """Advanced proxy rotation with health checking"""
    
    def __init__(self, proxy_list: List[str]):
        self.proxies = proxy_list or []
        self.working_proxies = []
        self.failed_proxies = set()
        self.current_index = 0
        self.test_url = "https://api.ipify.org?format=json"
    
    async def test_proxy(self, proxy: str) -> bool:
        """Test if proxy is working"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.test_url,
                    proxy=f"http://{proxy}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✓ Proxy {proxy} working - IP: {data.get('ip')}")
                        return True
        except Exception as e:
            logger.debug(f"✗ Proxy {proxy} failed: {str(e)}")
        return False
    
    async def initialize_proxies(self):
        """Test all proxies and build working list"""
        logger.info(f"[*] Testing {len(self.proxies)} proxies...")
        
        tasks = [self.test_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks)
        
        self.working_proxies = [
            proxy for proxy, is_working in zip(self.proxies, results)
            if is_working
        ]
        
        logger.info(f"[+] {len(self.working_proxies)}/{len(self.proxies)} proxies operational")
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next working proxy in rotation"""
        if not self.working_proxies:
            return None
        
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        return proxy
    
    def mark_proxy_failed(self, proxy: str):
        """Mark proxy as failed and remove from rotation"""
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            self.failed_proxies.add(proxy)
            logger.warning(f"[!] Removed failed proxy: {proxy}")


class StealthBrowser:
    """Ultra-stealthy browser with anti-detection"""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.ua = UserAgent()
        self.browser = None
        self.context = None
        self.page = None
        
    async def initialize_playwright(self):
        """Initialize Playwright browser with stealth settings"""
        logger.info("[*] Initializing stealth browser...")
        
        playwright = await async_playwright().start()
        
        # Launch arguments for maximum stealth
        launch_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-setuid-sandbox',
            '--no-first-run',
            '--no-service-autorun',
            '--password-store=basic',
            '--disable-gpu',
            '--disable-software-rasterizer',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-infobars',
            '--window-size=1920,1080'
        ]
        
        self.browser = await playwright.chromium.launch(
            headless=self.config.headless,
            args=launch_args
        )
        
        # Create context with realistic fingerprint
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.ua.random,
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},  # NYC
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            // Overwrite navigator properties
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            
            // Mock chrome property
            window.chrome = {runtime: {}};
            
            // Mock permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({state: Notification.permission}) :
                    originalQuery(parameters)
            );
            
            // WebGL vendor spoofing
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter(parameter);
            };
        """)
        
        self.page = await self.context.new_page()
        logger.info("[+] Stealth browser initialized")
    
    def initialize_undetected_chrome(self):
        """Initialize undetected Chrome driver"""
        logger.info("[*] Initializing undetected Chrome...")
        
        options = uc.ChromeOptions()
        
        if self.config.headless:
            options.add_argument('--headless')
        
        options.add_argument(f'user-agent={self.ua.random}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = uc.Chrome(options=options)
        logger.info("[+] Undetected Chrome initialized")
    
    async def navigate(self, url: str) -> str:
        """Navigate to URL with random delay"""
        try:
            # Random delay to mimic human behavior
            delay = random.uniform(self.config.delay_min, self.config.delay_max)
            await asyncio.sleep(delay)
            
            logger.info(f"[*] Navigating to {url}")
            await self.page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Random scroll behavior
            await self.random_scroll()
            
            # Wait for dynamic content
            await asyncio.sleep(random.uniform(1, 2))
            
            content = await self.page.content()
            return content
            
        except Exception as e:
            logger.error(f"[!] Navigation error: {str(e)}")
            return ""
    
    async def random_scroll(self):
        """Perform random scrolling to mimic human behavior"""
        try:
            # Scroll to random positions
            for _ in range(random.randint(1, 3)):
                scroll_amount = random.randint(100, 800)
                await self.page.evaluate(f"window.scrollBy(0, {scroll_amount})")
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Scroll back up occasionally
            if random.random() > 0.7:
                await self.page.evaluate("window.scrollTo(0, 0)")
                await asyncio.sleep(random.uniform(0.5, 1))
        except Exception as e:
            logger.debug(f"Scroll simulation error (non-critical): {str(e)}")
            pass
    
    async def extract_javascript_data(self) -> Dict:
        """Extract data rendered by JavaScript"""
        try:
            # Wait for common JS frameworks to load
            await self.page.wait_for_load_state('networkidle')
            
            # Extract data from window object
            data = await self.page.evaluate("""
                () => {
                    return {
                        url: window.location.href,
                        title: document.title,
                        meta: Array.from(document.querySelectorAll('meta')).map(m => ({
                            name: m.getAttribute('name') || m.getAttribute('property'),
                            content: m.getAttribute('content')
                        })),
                        scripts: Array.from(document.querySelectorAll('script[src]')).map(s => s.src),
                        links: Array.from(document.querySelectorAll('a[href]')).map(a => a.href),
                        images: Array.from(document.querySelectorAll('img[src]')).map(img => img.src)
                    }
                }
            """)
            
            return data
        except Exception as e:
            logger.error(f"[!] JS extraction error: {str(e)}")
            return {}
    
    async def close(self):
        """Clean up browser resources"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()


class SocialMediaScraper:
    """Specialized scrapers for social media platforms"""
    
    def __init__(self, browser: StealthBrowser):
        self.browser = browser
    
    async def scrape_linkedin_profile(self, profile_url: str) -> Dict:
        """Scrape LinkedIn profile (requires login session)"""
        logger.info(f"[*] Scraping LinkedIn: {profile_url}")
        
        try:
            await self.browser.navigate(profile_url)
            await asyncio.sleep(3)
            
            # Extract profile data
            profile_data = await self.browser.page.evaluate("""
                () => {
                    const getText = (selector) => {
                        const el = document.querySelector(selector);
                        return el ? el.textContent.trim() : null;
                    };
                    
                    return {
                        name: getText('.text-heading-xlarge'),
                        headline: getText('.text-body-medium'),
                        location: getText('.text-body-small.inline'),
                        about: getText('.display-flex.ph5.pv3'),
                        connections: getText('.link-without-visited-state'),
                        experience: Array.from(document.querySelectorAll('.pvs-list__item--line-separated')).map(item => ({
                            title: item.querySelector('.mr1.t-bold')?.textContent.trim(),
                            company: item.querySelector('.t-14.t-normal')?.textContent.trim(),
                            duration: item.querySelector('.t-14.t-normal.t-black--light')?.textContent.trim()
                        })).filter(e => e.title)
                    }
                }
            """)
            
            return {
                'platform': 'linkedin',
                'url': profile_url,
                'data': profile_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[!] LinkedIn scraping error: {str(e)}")
            return {'error': str(e)}
    
    async def scrape_twitter_profile(self, username: str) -> Dict:
        """Scrape Twitter/X profile"""
        logger.info(f"[*] Scraping Twitter: {username}")
        
        url = f"https://twitter.com/{username}"
        
        try:
            await self.browser.navigate(url)
            await asyncio.sleep(3)
            
            profile_data = await self.browser.page.evaluate("""
                () => {
                    const getText = (selector) => {
                        const el = document.querySelector(selector);
                        return el ? el.textContent.trim() : null;
                    };
                    
                    return {
                        username: getText('[data-testid="UserName"]'),
                        bio: getText('[data-testid="UserDescription"]'),
                        followers: getText('[href$="/followers"] span'),
                        following: getText('[href$="/following"] span'),
                        tweets: getText('[data-testid="primaryColumn"] [role="tablist"] a span'),
                        location: getText('[data-testid="UserLocation"]'),
                        website: getText('[data-testid="UserUrl"] a'),
                        joined: getText('[data-testid="UserJoinDate"]')
                    }
                }
            """)
            
            return {
                'platform': 'twitter',
                'username': username,
                'url': url,
                'data': profile_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[!] Twitter scraping error: {str(e)}")
            return {'error': str(e)}
    
    async def scrape_instagram_profile(self, username: str) -> Dict:
        """Scrape Instagram profile"""
        logger.info(f"[*] Scraping Instagram: {username}")
        
        url = f"https://www.instagram.com/{username}/"
        
        try:
            await self.browser.navigate(url)
            await asyncio.sleep(3)
            
            # Instagram loads data in script tags
            content = await self.browser.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find JSON data in script tag
            scripts = soup.find_all('script', type='application/ld+json')
            profile_data = {}
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if '@type' in data and data['@type'] == 'ProfilePage':
                        profile_data = data
                        break
                except Exception as e:
                    logger.debug(f"JSON parsing error in script tag: {str(e)}")
                    continue
            
            return {
                'platform': 'instagram',
                'username': username,
                'url': url,
                'data': profile_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"[!] Instagram scraping error: {str(e)}")
            return {'error': str(e)}


class EliteWebScraper:
    """Master scraper orchestrating all operations"""
    
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.browser = StealthBrowser(config)
        self.proxy_rotator = ProxyRotator(config.proxy_list or [])
        self.visited_urls: Set[str] = set()
        self.scraped_data: List[Dict] = []
        
        # Database connections
        self.mongo_client = MongoClient(config.mongodb_uri)
        self.db = self.mongo_client['hughes_clues']
        self.collection = self.db['scraped_data']
        
        # Redis for caching
        self.redis = Redis(host=config.redis_host, port=config.redis_port, decode_responses=False)
    
    async def initialize(self):
        """Initialize scraper components"""
        await self.browser.initialize_playwright()
        if self.config.use_proxies and self.config.proxy_list:
            await self.proxy_rotator.initialize_proxies()
    
    def get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return f"scrape:{hashlib.md5(url.encode()).hexdigest()}"
    
    def cache_get(self, url: str) -> Optional[Dict]:
        """Get cached scrape result"""
        try:
            data = self.redis.get(self.get_cache_key(url))
            if data:
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Cache get error for {url}: {str(e)}")
            pass
        return None
    
    def cache_set(self, url: str, data: Dict, ttl: int = 3600):
        """Cache scrape result"""
        try:
            self.redis.setex(
                self.get_cache_key(url),
                ttl,
                pickle.dumps(data)
            )
        except Exception as e:
            logger.warning(f"Cache set error for {url}: {str(e)}")
            pass
    
    async def scrape_url(self, url: str, depth: int = 0) -> Dict:
        """Scrape a single URL"""
        
        # Check cache first
        cached = self.cache_get(url)
        if cached:
            logger.info(f"[CACHE] Using cached data for {url}")
            return cached
        
        # Check if already visited
        if url in self.visited_urls:
            return {'status': 'already_visited'}
        
        self.visited_urls.add(url)
        
        try:
            # Navigate and get content
            content = await self.browser.navigate(url)
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract JavaScript data
            js_data = await self.browser.extract_javascript_data()
            
            # Extract structured data
            result = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'meta_description': self.extract_meta_description(soup),
                'headings': self.extract_headings(soup),
                'links': self.extract_links(soup, url),
                'images': [img.get('src') for img in soup.find_all('img', src=True)],
                'text_content': self.extract_text_content(soup),
                'emails': self.extract_emails(content),
                'phone_numbers': self.extract_phone_numbers(content),
                'social_links': self.extract_social_links(soup),
                'javascript_data': js_data,
                'timestamp': datetime.now().isoformat(),
                'depth': depth
            }
            
            # Cache result
            self.cache_set(url, result)
            
            # Store in MongoDB
            self.collection.insert_one(result.copy())
            
            self.scraped_data.append(result)
            logger.info(f"[+] Successfully scraped {url}")
            
            return result
            
        except Exception as e:
            logger.error(f"[!] Error scraping {url}: {str(e)}")
            return {'url': url, 'error': str(e)}
    
    def extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')
        meta = soup.find('meta', attrs={'property': 'og:description'})
        if meta:
            return meta.get('content', '')
        return ''
    
    def extract_headings(self, soup: BeautifulSoup) -> Dict:
        """Extract all headings"""
        return {
            'h1': [h.get_text(strip=True) for h in soup.find_all('h1')],
            'h2': [h.get_text(strip=True) for h in soup.find_all('h2')],
            'h3': [h.get_text(strip=True) for h in soup.find_all('h3')]
        }
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            links.append(full_url)
        return list(set(links))  # Remove duplicates
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        text = soup.get_text(separator=' ')
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # Limit to first 5000 chars
    
    def extract_emails(self, content: str) -> List[str]:
        """Extract email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(email_pattern, content)))
    
    def extract_phone_numbers(self, content: str) -> List[str]:
        """Extract phone numbers"""
        phone_pattern = r'(\+\d{1,3}[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'
        return list(set(re.findall(phone_pattern, content)))
    
    def extract_social_links(self, soup: BeautifulSoup) -> Dict:
        """Extract social media links"""
        social_patterns = {
            'linkedin': r'linkedin\.com',
            'twitter': r'twitter\.com|x\.com',
            'facebook': r'facebook\.com',
            'instagram': r'instagram\.com',
            'github': r'github\.com',
            'youtube': r'youtube\.com'
        }
        
        social_links = {}
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href):
                    if platform not in social_links:
                        social_links[platform] = []
                    social_links[platform].append(href)
        
        return social_links
    
    async def crawl_recursive(self, start_url: str, max_depth: int = 3):
        """Recursively crawl website"""
        logger.info(f"[*] Starting recursive crawl from {start_url}")
        
        await self.crawl_url_recursive(start_url, 0, max_depth)
        
        logger.info(f"[+] Crawl complete! Visited {len(self.visited_urls)} URLs")
    
    async def crawl_url_recursive(self, url: str, current_depth: int, max_depth: int):
        """Recursive crawling helper"""
        if current_depth > max_depth:
            return
        
        result = await self.scrape_url(url, current_depth)
        
        if current_depth < max_depth and 'links' in result:
            # Filter links to same domain
            parsed_start = urlparse(url)
            same_domain_links = [
                link for link in result['links']
                if urlparse(link).netloc == parsed_start.netloc
            ][:10]  # Limit to 10 links per page
            
            for link in same_domain_links:
                if link not in self.visited_urls:
                    await self.crawl_url_recursive(link, current_depth + 1, max_depth)
    
    async def bulk_scrape(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs concurrently"""
        logger.info(f"[*] Bulk scraping {len(urls)} URLs")
        
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if isinstance(r, dict)]
    
    def export_results(self, filename: str = None):
        """Export scraped data to JSON"""
        if filename is None:
            filename = f"scrape_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.scraped_data, f, indent=2, default=str)
        
        logger.info(f"[+] Results exported to {filename}")
        return filename
    
    async def cleanup(self):
        """Clean up resources"""
        await self.browser.close()
        self.mongo_client.close()
        self.redis.close()


async def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hughes Clues Elite Web Scraper')
    parser.add_argument('url', help='Target URL to scrape')
    parser.add_argument('--depth', type=int, default=2, help='Crawl depth')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--output', help='Output filename')
    
    args = parser.parse_args()
    
    config = ScraperConfig(
        headless=args.headless,
        max_depth=args.depth
    )
    
    scraper = EliteWebScraper(config)
    
    try:
        await scraper.initialize()
        await scraper.crawl_recursive(args.url, args.depth)
        scraper.export_results(args.output)
    finally:
        await scraper.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
