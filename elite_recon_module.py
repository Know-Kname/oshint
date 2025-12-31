#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

Advanced Reconnaissance Module - Elite Intelligence Gathering
Integrates: Shodan, Censys, VirusTotal, URLScan, SecurityTrails, HaveIBeenPwned
"""

import dns.resolver
import whois
import requests
import socket
import ssl
import subprocess
import json
import sys
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime
import concurrent.futures
from urllib.parse import urlparse
import ipaddress
import hashlib
import base64
from dataclasses import dataclass, asdict
import yaml
import re
from pathlib import Path

# Configuration management
@dataclass
class APIConfig:
    """API credentials configuration"""
    shodan_key: Optional[str] = None
    censys_id: Optional[str] = None
    censys_secret: Optional[str] = None
    virustotal_key: Optional[str] = None
    securitytrails_key: Optional[str] = None
    urlscan_key: Optional[str] = None
    hibp_key: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: str = "config.yaml"):
        """Load API keys from config file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return cls(**config.get('api_keys', {}))
        except FileNotFoundError:
            print(f"[!] Config file not found: {config_path}")
            return cls()


class AdvancedReconModule:
    """Elite reconnaissance with multiple intelligence sources"""
    
    def __init__(self, target: str, config: APIConfig = None, timeout: int = 15):
        self.target = target.strip()
        self.timeout = timeout
        self.config = config or APIConfig()
        self.session = None
        
        self.results = {
            'target': self.target,
            'timestamp': datetime.now().isoformat(),
            'dns': {},
            'whois': {},
            'ssl': {},
            'subdomains': [],
            'ports': {},
            'ip_info': {},
            'headers': {},
            'shodan': {},
            'censys': {},
            'virustotal': {},
            'security_trails': {},
            'certificate_transparency': {},
            'breaches': {},
            'technologies': [],
            'cloud_assets': {},
            'github_exposure': {},
            'social_media': {},
            'risk_score': 0
        }
    
    async def create_session(self):
        """Create aiohttp session for async requests"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def dns_enumeration_advanced(self) -> Dict:
        """Advanced DNS enumeration with DNSSEC and zone transfer attempts"""
        print(f"[*] Advanced DNS enumeration on {self.target}")
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME', 'PTR', 
                       'DNSKEY', 'DS', 'RRSIG', 'NSEC', 'NSEC3', 'CAA', 'SRV']
        dns_results = {'records': {}, 'dnssec_enabled': False, 'zone_transfer': None}
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(self.target, record_type, lifetime=self.timeout)
                dns_results['records'][record_type] = [str(rdata) for rdata in answers]
                
                if record_type in ['DNSKEY', 'DS', 'RRSIG']:
                    dns_results['dnssec_enabled'] = True
                    
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout):
                dns_results['records'][record_type] = None
            except Exception as e:
                dns_results['records'][record_type] = f"Error: {str(e)}"
        
        # Attempt zone transfer (AXFR)
        if 'NS' in dns_results['records'] and dns_results['records']['NS']:
            for ns_server in dns_results['records']['NS'][:3]:  # Try first 3 NS servers
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(ns_server, self.target, timeout=5))
                    dns_results['zone_transfer'] = {
                        'server': ns_server,
                        'success': True,
                        'records': [name.to_text() for name in zone.nodes.keys()]
                    }
                    break
                except Exception:
                    continue
        
        # Reverse DNS
        try:
            ip = socket.gethostbyname(self.target)
            reverse_dns = socket.gethostbyaddr(ip)
            dns_results['reverse'] = reverse_dns[0]
        except Exception as e:
            logger.debug(f"Reverse DNS lookup failed: {str(e)}")
            dns_results['reverse'] = None
        
        return dns_results
    
    async def shodan_intel(self) -> Dict:
        """Shodan intelligence gathering"""
        if not self.config.shodan_key:
            return {'error': 'No Shodan API key configured'}
        
        print(f"[*] Querying Shodan for {self.target}")
        
        try:
            ip = socket.gethostbyname(self.target)
            url = f"https://api.shodan.io/shodan/host/{ip}?key={self.config.shodan_key}"
            
            if self.session:
                async with self.session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'ip': ip,
                            'organization': data.get('org'),
                            'isp': data.get('isp'),
                            'asn': data.get('asn'),
                            'open_ports': data.get('ports', []),
                            'vulnerabilities': data.get('vulns', []),
                            'services': [
                                {
                                    'port': svc.get('port'),
                                    'protocol': svc.get('transport'),
                                    'product': svc.get('product'),
                                    'version': svc.get('version'),
                                    'banner': svc.get('data', '')[:200]
                                }
                                for svc in data.get('data', [])
                            ],
                            'tags': data.get('tags', []),
                            'hostnames': data.get('hostnames', []),
                            'last_update': data.get('last_update')
                        }
            
            # Fallback synchronous request
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return {
                    'ip': ip,
                    'vulnerabilities': data.get('vulns', []),
                    'ports': data.get('ports', []),
                    'services': len(data.get('data', []))
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    async def certificate_transparency_logs(self) -> Dict:
        """Search certificate transparency logs for subdomains"""
        print(f"[*] Searching certificate transparency logs")
        
        try:
            url = f"https://crt.sh/?q=%.{self.target}&output=json"
            
            if self.session:
                async with self.session.get(url, timeout=self.timeout) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        subdomains = set()
                        certificates = []
                        
                        for entry in data:
                            name_value = entry.get('name_value', '')
                            for domain in name_value.split('\n'):
                                domain = domain.strip().replace('*.', '')
                                if domain.endswith(self.target):
                                    subdomains.add(domain)
                            
                            certificates.append({
                                'issuer': entry.get('issuer_name'),
                                'not_before': entry.get('not_before'),
                                'not_after': entry.get('not_after'),
                                'serial_number': entry.get('serial_number')
                            })
                        
                        return {
                            'unique_subdomains': sorted(list(subdomains)),
                            'total_certificates': len(certificates),
                            'certificates': certificates[:50]  # Limit to 50 most recent
                        }
        except Exception as e:
            return {'error': str(e)}
    
    async def github_dorking(self) -> Dict:
        """Search GitHub for exposed secrets and sensitive information"""
        print(f"[*] Searching GitHub for {self.target} exposure")

        search_queries = [
            f'"{self.target}" password',
            f'"{self.target}" api_key',
            f'"{self.target}" secret',
            f'"{self.target}" token',
            f'"{self.target}" credentials',
            f'"{self.target}" .env',
            f'"{self.target}" config.yml',
        ]

        findings = []

        try:
            import time as time_module
            for query in search_queries:
                url = f"https://api.github.com/search/code?q={query}"

                if self.session:
                    async with self.session.get(url, timeout=self.timeout) as response:
                        # Check rate limit headers
                        remaining = response.headers.get('X-RateLimit-Remaining')
                        reset_time = response.headers.get('X-RateLimit-Reset')

                        if remaining and int(remaining) < 1:
                            if reset_time:
                                wait_seconds = max(0, int(reset_time) - int(time_module.time()))
                                print(f"[!] GitHub rate limit exceeded, waiting {wait_seconds}s")
                                await asyncio.sleep(wait_seconds + 1)

                        if response.status == 200:
                            data = await response.json()
                            for item in data.get('items', [])[:5]:  # Top 5 results per query
                                findings.append({
                                    'repository': item.get('repository', {}).get('full_name'),
                                    'path': item.get('path'),
                                    'url': item.get('html_url'),
                                    'query': query
                                })

                await asyncio.sleep(1)  # Rate limiting between queries

        except Exception as e:
            return {'error': str(e)}

        return {
            'total_findings': len(findings),
            'repositories': findings,
            'risk_level': 'HIGH' if len(findings) > 5 else 'MEDIUM' if len(findings) > 0 else 'LOW'
        }
    
    async def haveibeenpwned_check(self) -> Dict:
        """Check for email breaches on HaveIBeenPwned"""
        print(f"[*] Checking breach databases")

        # Extract emails from WHOIS
        emails = self.results.get('whois', {}).get('emails', [])

        if not emails:
            return {'error': 'No emails found to check'}

        breach_data = {}

        for email in emails[:5]:  # Check first 5 emails
            try:
                url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
                headers = {
                    'hibp-api-key': self.config.hibp_key or '',
                    'User-Agent': 'Hughes-Clues-OSINT'
                }

                if self.session:
                    async with self.session.get(url, headers=headers, timeout=self.timeout) as response:
                        if response.status == 200:
                            breaches = await response.json()
                            breach_data[email] = {
                                'breached': True,
                                'breach_count': len(breaches),
                                'breaches': [
                                    {
                                        'name': b.get('Name'),
                                        'date': b.get('BreachDate'),
                                        'compromised_data': b.get('DataClasses', [])
                                    }
                                    for b in breaches[:10]
                                ]
                            }
                        elif response.status == 404:
                            breach_data[email] = {'breached': False}

            except Exception as e:
                breach_data[email] = {'error': str(e)}
            finally:
                # Rate limiting applied regardless of success or failure
                await asyncio.sleep(1.5)

        return breach_data
    
    async def cloud_asset_discovery(self) -> Dict:
        """Discover cloud assets (AWS S3, Azure, GCP)"""
        print(f"[*] Discovering cloud assets")
        
        domain_parts = self.target.replace('.', '-').replace('_', '-')
        company_name = self.target.split('.')[0]
        
        # Common S3 bucket name patterns
        s3_patterns = [
            company_name,
            f"{company_name}-backup",
            f"{company_name}-data",
            f"{company_name}-prod",
            f"{company_name}-dev",
            f"{company_name}-staging",
            f"{company_name}-logs",
            f"{company_name}-static",
            f"{company_name}-assets",
            domain_parts
        ]
        
        found_buckets = []
        
        for bucket_name in s3_patterns:
            try:
                url = f"https://{bucket_name}.s3.amazonaws.com"

                if self.session:
                    async with self.session.head(url, timeout=5) as response:
                        if response.status in [200, 403]:  # 403 means exists but private
                            found_buckets.append({
                                'bucket': bucket_name,
                                'url': url,
                                'status': 'PUBLIC' if response.status == 200 else 'PRIVATE',
                                'accessible': response.status == 200
                            })
            except Exception:
                continue
        
        return {
            'aws_s3_buckets': found_buckets,
            'total_found': len(found_buckets),
            'public_buckets': len([b for b in found_buckets if b['accessible']])
        }
    
    def technology_fingerprinting(self) -> Dict:
        """Advanced technology detection"""
        print(f"[*] Fingerprinting technologies")
        
        try:
            url = f"https://{self.target}"
            response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            
            technologies = {
                'web_server': response.headers.get('Server', 'Unknown'),
                'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                'frameworks': [],
                'cms': None,
                'programming_languages': [],
                'analytics': [],
                'cdn': None
            }
            
            content = response.text.lower()
            headers_str = str(response.headers).lower()
            
            # Framework detection
            framework_patterns = {
                'React': ['react', '_next', '__next'],
                'Vue.js': ['vue.js', 'vue.min.js', '__vue__'],
                'Angular': ['angular', 'ng-version'],
                'Django': ['csrf', 'django'],
                'Laravel': ['laravel', 'laravel_session'],
                'WordPress': ['wp-content', 'wp-includes'],
                'Drupal': ['drupal', '/sites/default'],
                'Joomla': ['joomla', '/components/com_'],
            }
            
            for framework, patterns in framework_patterns.items():
                if any(pattern in content or pattern in headers_str for pattern in patterns):
                    technologies['frameworks'].append(framework)
                    if framework in ['WordPress', 'Drupal', 'Joomla']:
                        technologies['cms'] = framework
            
            # CDN detection
            cdn_headers = {
                'cloudflare': 'Cloudflare',
                'akamai': 'Akamai',
                'fastly': 'Fastly',
                'cloudfront': 'CloudFront',
                'cdn77': 'CDN77'
            }
            
            for pattern, cdn_name in cdn_headers.items():
                if pattern in headers_str:
                    technologies['cdn'] = cdn_name
                    break
            
            # Analytics detection
            analytics_patterns = {
                'Google Analytics': 'google-analytics.com',
                'Hotjar': 'hotjar.com',
                'Mixpanel': 'mixpanel.com',
                'Segment': 'segment.com'
            }
            
            for analytics, pattern in analytics_patterns.items():
                if pattern in content:
                    technologies['analytics'].append(analytics)
            
            return technologies
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_risk_score(self) -> int:
        """Calculate overall security risk score (0-100)"""
        risk_score = 0
        
        # Open ports risk
        open_ports = self.results.get('ports', {})
        risk_score += min(len(open_ports) * 2, 20)
        
        # Shodan vulnerabilities
        shodan_vulns = self.results.get('shodan', {}).get('vulnerabilities', [])
        risk_score += min(len(shodan_vulns) * 10, 30)
        
        # Breach exposure
        breaches = self.results.get('breaches', {})
        for email_breaches in breaches.values():
            if isinstance(email_breaches, dict) and email_breaches.get('breached'):
                risk_score += min(email_breaches.get('breach_count', 0) * 2, 15)
        
        # GitHub exposure
        github_findings = self.results.get('github_exposure', {}).get('total_findings', 0)
        risk_score += min(github_findings * 5, 15)
        
        # Public cloud buckets
        public_buckets = self.results.get('cloud_assets', {}).get('public_buckets', 0)
        risk_score += min(public_buckets * 10, 20)
        
        return min(risk_score, 100)
    
    async def run_full_recon_async(self) -> Dict:
        """Execute all reconnaissance modules asynchronously"""
        print(f"\n{'='*60}")
        print(f"Hughes Clues ELITE - Advanced Reconnaissance")
        print(f"Target: {self.target}")
        print(f"{'='*60}\n")
        
        await self.create_session()
        
        try:
            # Synchronous operations
            self.results['dns'] = self.dns_enumeration_advanced()
            self.results['whois'] = self.whois_lookup()
            self.results['ssl'] = self.ssl_certificate_info()
            self.results['technologies'] = self.technology_fingerprinting()
            
            # Asynchronous operations
            async_tasks = [
                self.shodan_intel(),
                self.certificate_transparency_logs(),
                self.github_dorking(),
                self.haveibeenpwned_check(),
                self.cloud_asset_discovery()
            ]
            
            results = await asyncio.gather(*async_tasks, return_exceptions=True)
            
            self.results['shodan'] = results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])}
            self.results['certificate_transparency'] = results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])}
            self.results['github_exposure'] = results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])}
            self.results['breaches'] = results[3] if not isinstance(results[3], Exception) else {'error': str(results[3])}
            self.results['cloud_assets'] = results[4] if not isinstance(results[4], Exception) else {'error': str(results[4])}
            
            # Calculate risk score
            self.results['risk_score'] = self.calculate_risk_score()
            
        finally:
            await self.close_session()
        
        print(f"\n{'='*60}")
        print("[+] Elite Reconnaissance Complete!")
        print(f"{'='*60}\n")
        
        return self.results
    
    def whois_lookup(self) -> Dict:
        """Enhanced WHOIS with additional parsing"""
        try:
            w = whois.whois(self.target)
            return {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date) if w.creation_date else None,
                'expiration_date': str(w.expiration_date) if w.expiration_date else None,
                'updated_date': str(w.updated_date) if w.updated_date else None,
                'name_servers': w.name_servers if isinstance(w.name_servers, list) else [w.name_servers] if w.name_servers else [],
                'status': w.status if isinstance(w.status, list) else [w.status] if w.status else [],
                'emails': list(w.emails) if w.emails else [],
                'org': w.org,
                'country': w.country,
                'state': w.state,
                'city': w.city
            }
        except Exception as e:
            return {'error': str(e)}
    
    def ssl_certificate_info(self) -> Dict:
        """Enhanced SSL certificate analysis"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.target, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.target) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'version': cert.get('version'),
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'issuer': dict(x[0] for x in cert.get('issuer', [])),
                        'notBefore': cert.get('notBefore'),
                        'notAfter': cert.get('notAfter'),
                        'serialNumber': cert.get('serialNumber'),
                        'san': [x[1] for x in cert.get('subjectAltName', [])],
                        'cipher': ssock.cipher(),
                        'tls_version': ssock.version(),
                        'expired': False  # Would need date comparison
                    }
        except Exception as e:
            return {'error': str(e)}
    
    def export_comprehensive_report(self, filename: str = None):
        """Export comprehensive intelligence report"""
        if filename is None:
            filename = f'elite_recon_{self.target}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        # Also create a summary report
        summary_filename = filename.replace('.json', '_summary.txt')
        with open(summary_filename, 'w') as f:
            f.write(f"{'='*80}\n")
            f.write(f"HUGHES CLUES ELITE - INTELLIGENCE REPORT\n")
            f.write(f"Target: {self.target}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*80}\n\n")
            
            f.write(f"RISK SCORE: {self.results['risk_score']}/100\n\n")
            
            # Key findings
            f.write("KEY FINDINGS:\n")
            f.write("-" * 80 + "\n")
            
            shodan_vulns = self.results.get('shodan', {}).get('vulnerabilities', [])
            if shodan_vulns:
                f.write(f"⚠ {len(shodan_vulns)} vulnerabilities detected via Shodan\n")
            
            github_findings = self.results.get('github_exposure', {}).get('total_findings', 0)
            if github_findings > 0:
                f.write(f"⚠ {github_findings} potential secret exposures found on GitHub\n")
            
            public_buckets = self.results.get('cloud_assets', {}).get('public_buckets', 0)
            if public_buckets > 0:
                f.write(f"⚠ {public_buckets} publicly accessible S3 buckets found\n")
            
            breach_count = sum(
                b.get('breach_count', 0) for b in self.results.get('breaches', {}).values() 
                if isinstance(b, dict) and b.get('breached')
            )
            if breach_count > 0:
                f.write(f"⚠ Email addresses found in {breach_count} data breaches\n")
            
            f.write("\n")
        
        print(f"[+] Comprehensive report exported to {filename}")
        print(f"[+] Summary report exported to {summary_filename}")
        return filename, summary_filename


def main():
    """Main execution"""
    if len(sys.argv) < 2:
        print("""
Hughes Clues ELITE - Advanced OSINT Reconnaissance

Usage: python elite_recon.py <target> [options]

Options:
    --config PATH    Path to config.yaml with API keys
    -o, --output     Output filename
    -t, --timeout    Timeout in seconds (default: 15)
    
Example:
    python elite_recon.py example.com --config config.yaml
        """)
        sys.exit(1)
    
    target = sys.argv[1]
    config_path = "config.yaml"
    output_file = None
    timeout = 15
    
    # Parse arguments
    for i, arg in enumerate(sys.argv[2:], start=2):
        if arg == '--config' and i + 1 < len(sys.argv):
            config_path = sys.argv[i + 1]
        elif arg in ['-o', '--output'] and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
        elif arg in ['-t', '--timeout'] and i + 1 < len(sys.argv):
            timeout = int(sys.argv[i + 1])
    
    # Load configuration
    config = APIConfig.from_file(config_path)
    
    # Run reconnaissance
    recon = AdvancedReconModule(target, config=config, timeout=timeout)
    
    # Execute async reconnaissance
    results = asyncio.run(recon.run_full_recon_async())
    
    # Export reports
    if output_file:
        recon.export_comprehensive_report(output_file)
    else:
        recon.export_comprehensive_report()
    
    print(f"\n🎯 Risk Score: {results['risk_score']}/100")


if __name__ == '__main__':
    main()
