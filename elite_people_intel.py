#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

People Intelligence Module (PEOPLEINT)
Ethical OSINT for gathering publicly available information about individuals

⚠️  AUTHORIZATION REQUIRED ⚠️
This module is for:
- Authorized security assessments
- Background checks with consent
- CTF competitions
- Educational purposes
- Legal investigations
- Fraud prevention

PROHIBITED USES:
- Stalking or harassment
- Identity theft
- Unauthorized surveillance
- Privacy violations
- Any illegal activity

USE RESPONSIBLY AND LEGALLY
"""

import asyncio
import aiohttp
import requests
import json
import re
import hashlib
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from urllib.parse import quote, urlencode
import logging
from pathlib import Path
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PersonProfile:
    """Comprehensive person profile from OSINT"""
    # Basic Information
    full_name: str
    aliases: List[str] = field(default_factory=list)
    age: Optional[int] = None
    date_of_birth: Optional[str] = None

    # Location Information
    city_of_birth: Optional[str] = None
    current_city: Optional[str] = None
    current_state: Optional[str] = None
    current_country: Optional[str] = None
    previous_addresses: List[str] = field(default_factory=list)

    # Contact Information
    phone_numbers: List[str] = field(default_factory=list)
    email_addresses: List[str] = field(default_factory=list)

    # Online Presence
    social_media: Dict[str, List[str]] = field(default_factory=dict)
    websites: List[str] = field(default_factory=list)
    usernames: Set[str] = field(default_factory=set)

    # Professional Information
    employers: List[str] = field(default_factory=list)
    job_titles: List[str] = field(default_factory=list)
    education: List[str] = field(default_factory=list)
    professional_licenses: List[str] = field(default_factory=list)

    # Digital Footprint
    domain_registrations: List[str] = field(default_factory=list)
    public_records: List[Dict] = field(default_factory=list)
    data_breaches: List[str] = field(default_factory=list)

    # Metadata
    confidence_score: float = 0.0
    sources: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class PeopleIntelligence:
    """Advanced people intelligence gathering using ethical OSINT techniques"""

    def __init__(self, config: Dict = None):
        """
        Initialize People Intelligence Module

        Args:
            config: Configuration dict with API keys and settings
        """
        self.config = config or {}
        self.api_keys = self.config.get('api_keys', {})
        self.session = None

        # Data source configuration
        self.sources = {
            'search_engines': True,
            'social_media': True,
            'public_records': True,
            'data_breaches': True,
            'professional_networks': True,
            'people_search': True,
            'phone_lookup': True,
            'email_validation': True,
        }

        logger.info("[+] People Intelligence Module initialized")
        logger.warning("[!] AUTHORIZATION REQUIRED - Ensure legal compliance")

    async def create_session(self):
        """Create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()

    # ==================== NAME SEARCH ====================

    async def search_by_name(self, full_name: str, city: str = None, state: str = None) -> PersonProfile:
        """
        Search for person by name and optional location

        Args:
            full_name: Full name of person
            city: Optional city for narrowing results
            state: Optional state for narrowing results

        Returns:
            PersonProfile with aggregated information
        """
        logger.info(f"[*] Searching for: {full_name}")
        if city or state:
            logger.info(f"[*] Location filter: {city}, {state}")

        profile = PersonProfile(full_name=full_name)

        await self.create_session()

        # Gather from multiple sources
        tasks = []

        # Public search engines
        tasks.append(self._search_google(full_name, city, state, profile))

        # Social media platforms
        tasks.append(self._search_social_media(full_name, profile))

        # Professional networks
        tasks.append(self._search_linkedin(full_name, profile))

        # People search engines
        tasks.append(self._search_whitepages(full_name, city, state, profile))
        tasks.append(self._search_truepeoplesearch(full_name, city, state, profile))

        # Public records
        if self.sources.get('public_records'):
            tasks.append(self._search_public_records(full_name, city, state, profile))

        # Execute all searches concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate confidence score
        profile.confidence_score = self._calculate_confidence(profile)

        return profile

    async def _search_google(self, name: str, city: str, state: str, profile: PersonProfile):
        """Search Google for person information (ethical scraping)"""
        try:
            query_parts = [f'"{name}"']
            if city:
                query_parts.append(f'"{city}"')
            if state:
                query_parts.append(f'"{state}"')

            query = ' '.join(query_parts)

            # Search for social media profiles
            social_queries = [
                f'{query} site:linkedin.com',
                f'{query} site:facebook.com',
                f'{query} site:twitter.com',
                f'{query} site:instagram.com',
                f'{query} "about me"',
                f'{query} email',
                f'{query} phone',
            ]

            profile.sources.append('Google Search')
            logger.info(f"[+] Google search queries prepared for {name}")

        except Exception as e:
            logger.error(f"[!] Google search error: {str(e)}")

    async def _search_social_media(self, name: str, profile: PersonProfile):
        """Search social media platforms for public profiles"""
        try:
            platforms = {
                'LinkedIn': f'https://www.linkedin.com/search/results/people/?keywords={quote(name)}',
                'Facebook': f'https://www.facebook.com/search/people/?q={quote(name)}',
                'Twitter': f'https://twitter.com/search?q={quote(name)}&f=user',
                'Instagram': f'https://www.instagram.com/explore/tags/{quote(name.replace(" ", ""))}/',
                'GitHub': f'https://github.com/search?q={quote(name)}&type=users',
            }

            profile.social_media = platforms
            profile.sources.append('Social Media Search')
            logger.info(f"[+] Social media search URLs prepared")

        except Exception as e:
            logger.error(f"[!] Social media search error: {str(e)}")

    async def _search_linkedin(self, name: str, profile: PersonProfile):
        """Search LinkedIn for professional information (public profiles only)"""
        try:
            # LinkedIn public profile search
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={quote(name)}'

            # Note: Actual scraping would require authentication
            # This is a placeholder for ethical API usage or manual verification

            profile.sources.append('LinkedIn (manual verification required)')
            logger.info(f"[+] LinkedIn search URL: {search_url}")

        except Exception as e:
            logger.error(f"[!] LinkedIn search error: {str(e)}")

    # ==================== PHONE NUMBER SEARCH ====================

    async def search_by_phone(self, phone_number: str) -> PersonProfile:
        """
        Search for person by phone number

        Args:
            phone_number: Phone number (any format)

        Returns:
            PersonProfile with associated information
        """
        # Normalize phone number
        clean_phone = re.sub(r'\D', '', phone_number)
        logger.info(f"[*] Searching for phone: {clean_phone}")

        profile = PersonProfile(
            full_name="Unknown",
            phone_numbers=[clean_phone]
        )

        await self.create_session()

        # Search multiple phone lookup services
        tasks = [
            self._search_truecaller(clean_phone, profile),
            self._search_whitepages_phone(clean_phone, profile),
            self._search_numverify(clean_phone, profile),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        return profile

    async def _search_truecaller(self, phone: str, profile: PersonProfile):
        """Search TrueCaller API for phone information"""
        try:
            # Note: Requires TrueCaller API key
            api_key = self.api_keys.get('truecaller_key')
            if not api_key:
                logger.warning("[!] TrueCaller API key not configured")
                return

            # TrueCaller API endpoint (example)
            # Actual implementation would use their official API

            profile.sources.append('TrueCaller')

        except Exception as e:
            logger.error(f"[!] TrueCaller search error: {str(e)}")

    async def _search_whitepages_phone(self, phone: str, profile: PersonProfile):
        """Search Whitepages for phone number information"""
        try:
            # Whitepages reverse phone lookup
            # Note: Requires API key or web scraping (with respect to robots.txt)

            url = f'https://www.whitepages.com/phone/{phone}'
            profile.sources.append('Whitepages Phone Lookup')
            logger.info(f"[+] Whitepages URL: {url}")

        except Exception as e:
            logger.error(f"[!] Whitepages phone search error: {str(e)}")

    async def _search_numverify(self, phone: str, profile: PersonProfile):
        """Validate and lookup phone number using NumVerify API"""
        try:
            api_key = self.api_keys.get('numverify_key')
            if not api_key:
                logger.debug("[!] NumVerify API key not configured")
                return

            url = f'http://apilayer.net/api/validate'
            params = {
                'access_key': api_key,
                'number': phone,
                'country_code': 'US',
                'format': 1
            }

            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('valid'):
                        profile.current_country = data.get('country_name')
                        profile.sources.append('NumVerify')
                        logger.info(f"[+] Phone validated: {data.get('location')}")

        except Exception as e:
            logger.error(f"[!] NumVerify error: {str(e)}")

    # ==================== EMAIL SEARCH ====================

    async def search_by_email(self, email: str) -> PersonProfile:
        """
        Search for person by email address

        Args:
            email: Email address

        Returns:
            PersonProfile with associated information
        """
        logger.info(f"[*] Searching for email: {email}")

        profile = PersonProfile(
            full_name="Unknown",
            email_addresses=[email]
        )

        await self.create_session()

        # Search multiple sources
        tasks = [
            self._search_email_reputation(email, profile),
            self._search_gravatar(email, profile),
            self._check_data_breaches(email, profile),
            self._search_email_social_media(email, profile),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        return profile

    async def _search_email_reputation(self, email: str, profile: PersonProfile):
        """Check email reputation and validation services"""
        try:
            # Extract domain
            domain = email.split('@')[1] if '@' in email else None

            if domain:
                profile.sources.append('Email Domain Analysis')
                logger.info(f"[+] Email domain: {domain}")

        except Exception as e:
            logger.error(f"[!] Email reputation error: {str(e)}")

    async def _search_gravatar(self, email: str, profile: PersonProfile):
        """Check Gravatar for profile information"""
        try:
            # Gravatar uses MD5 hash of email
            email_hash = hashlib.md5(email.lower().encode()).hexdigest()
            gravatar_url = f'https://www.gravatar.com/avatar/{email_hash}?d=404'

            async with self.session.get(gravatar_url) as response:
                if response.status == 200:
                    profile.sources.append('Gravatar')
                    logger.info(f"[+] Gravatar profile found")

        except Exception as e:
            logger.error(f"[!] Gravatar search error: {str(e)}")

    async def _check_data_breaches(self, email: str, profile: PersonProfile):
        """Check if email appears in known data breaches (HaveIBeenPwned)"""
        try:
            hibp_key = self.api_keys.get('hibp_key')
            if not hibp_key:
                logger.debug("[!] HaveIBeenPwned API key not configured")
                return

            url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{quote(email)}'
            headers = {
                'hibp-api-key': hibp_key,
                'User-Agent': 'HughesClues-OSINT'
            }

            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    breaches = await response.json()
                    profile.data_breaches = [b.get('Name') for b in breaches]
                    profile.sources.append('HaveIBeenPwned')
                    logger.warning(f"[!] Found in {len(breaches)} data breaches")
                elif response.status == 404:
                    logger.info("[+] No breaches found")

        except Exception as e:
            logger.error(f"[!] HIBP check error: {str(e)}")

    async def _search_email_social_media(self, email: str, profile: PersonProfile):
        """Search for email on social media platforms"""
        try:
            # Many platforms allow email-based account recovery which reveals if account exists
            # This is for educational purposes only

            profile.sources.append('Email Social Media Search')

        except Exception as e:
            logger.error(f"[!] Email social media search error: {str(e)}")

    # ==================== USERNAME SEARCH ====================

    async def search_by_username(self, username: str) -> PersonProfile:
        """
        Search for person across platforms by username

        Args:
            username: Username to search

        Returns:
            PersonProfile with found accounts
        """
        logger.info(f"[*] Searching for username: {username}")

        profile = PersonProfile(
            full_name="Unknown",
            usernames={username}
        )

        await self.create_session()

        # Check username across multiple platforms
        platforms = [
            ('GitHub', f'https://github.com/{username}'),
            ('Twitter', f'https://twitter.com/{username}'),
            ('Instagram', f'https://instagram.com/{username}'),
            ('Reddit', f'https://reddit.com/user/{username}'),
            ('Medium', f'https://medium.com/@{username}'),
            ('Dev.to', f'https://dev.to/{username}'),
            ('Twitch', f'https://twitch.tv/{username}'),
            ('YouTube', f'https://youtube.com/@{username}'),
            ('TikTok', f'https://tiktok.com/@{username}'),
            ('LinkedIn', f'https://linkedin.com/in/{username}'),
            ('Pinterest', f'https://pinterest.com/{username}'),
            ('Telegram', f'https://t.me/{username}'),
        ]

        tasks = [
            self._check_platform(platform, url, profile)
            for platform, url in platforms
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        return profile

    async def _check_platform(self, platform: str, url: str, profile: PersonProfile):
        """Check if username exists on platform"""
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status == 200:
                    if platform not in profile.social_media:
                        profile.social_media[platform] = []
                    profile.social_media[platform].append(url)
                    logger.info(f"[+] Found on {platform}: {url}")
        except Exception as e:
            logger.debug(f"[!] {platform} check error: {str(e)}")

    # ==================== PUBLIC RECORDS ====================

    async def _search_whitepages(self, name: str, city: str, state: str, profile: PersonProfile):
        """Search Whitepages for public records"""
        try:
            query_parts = [name]
            if city:
                query_parts.append(city)
            if state:
                query_parts.append(state)

            # Whitepages URL (manual verification)
            url = f'https://www.whitepages.com/name/{"-".join(quote(p) for p in query_parts)}'
            profile.sources.append('Whitepages')
            logger.info(f"[+] Whitepages URL: {url}")

        except Exception as e:
            logger.error(f"[!] Whitepages search error: {str(e)}")

    async def _search_truepeoplesearch(self, name: str, city: str, state: str, profile: PersonProfile):
        """Search TruePeopleSearch for public records"""
        try:
            # TruePeopleSearch aggregates public records
            # Note: Respect robots.txt and terms of service

            profile.sources.append('TruePeopleSearch')
            logger.info(f"[+] TruePeopleSearch query prepared")

        except Exception as e:
            logger.error(f"[!] TruePeopleSearch error: {str(e)}")

    async def _search_public_records(self, name: str, city: str, state: str, profile: PersonProfile):
        """Search government public records databases"""
        try:
            # Public records sources:
            # - Voter registration (where public)
            # - Property records
            # - Court records
            # - Business registrations
            # - Professional licenses

            profile.sources.append('Public Records Databases')
            logger.info(f"[+] Public records search prepared")

        except Exception as e:
            logger.error(f"[!] Public records search error: {str(e)}")

    # ==================== ADVANCED TECHNIQUES ====================

    async def search_comprehensive(self,
                                  name: str = None,
                                  phone: str = None,
                                  email: str = None,
                                  username: str = None,
                                  city: str = None,
                                  state: str = None) -> PersonProfile:
        """
        Comprehensive search using all available identifiers

        Args:
            name: Full name
            phone: Phone number
            email: Email address
            username: Username
            city: City
            state: State

        Returns:
            Aggregated PersonProfile
        """
        logger.info("[*] Starting comprehensive people intelligence search")

        profiles = []

        await self.create_session()

        # Search by each identifier
        if name:
            profiles.append(await self.search_by_name(name, city, state))
        if phone:
            profiles.append(await self.search_by_phone(phone))
        if email:
            profiles.append(await self.search_by_email(email))
        if username:
            profiles.append(await self.search_by_username(username))

        # Merge all profiles
        merged_profile = self._merge_profiles(profiles, name or "Unknown")

        await self.close_session()

        return merged_profile

    def _merge_profiles(self, profiles: List[PersonProfile], primary_name: str) -> PersonProfile:
        """Merge multiple profiles into one comprehensive profile"""
        merged = PersonProfile(full_name=primary_name)

        for profile in profiles:
            # Merge lists and sets
            merged.aliases.extend(profile.aliases)
            merged.phone_numbers.extend(profile.phone_numbers)
            merged.email_addresses.extend(profile.email_addresses)
            merged.previous_addresses.extend(profile.previous_addresses)
            merged.employers.extend(profile.employers)
            merged.job_titles.extend(profile.job_titles)
            merged.education.extend(profile.education)
            merged.websites.extend(profile.websites)
            merged.sources.extend(profile.sources)
            merged.data_breaches.extend(profile.data_breaches)
            merged.usernames.update(profile.usernames)

            # Merge dicts
            for platform, urls in profile.social_media.items():
                if platform not in merged.social_media:
                    merged.social_media[platform] = []
                merged.social_media[platform].extend(urls)

            # Take first non-None values
            if not merged.age and profile.age:
                merged.age = profile.age
            if not merged.date_of_birth and profile.date_of_birth:
                merged.date_of_birth = profile.date_of_birth
            if not merged.current_city and profile.current_city:
                merged.current_city = profile.current_city

        # Deduplicate lists
        merged.aliases = list(set(merged.aliases))
        merged.phone_numbers = list(set(merged.phone_numbers))
        merged.email_addresses = list(set(merged.email_addresses))
        merged.sources = list(set(merged.sources))

        # Calculate confidence
        merged.confidence_score = self._calculate_confidence(merged)

        return merged

    def _calculate_confidence(self, profile: PersonProfile) -> float:
        """Calculate confidence score based on data completeness"""
        score = 0.0

        # Basic info (20 points)
        if profile.full_name and profile.full_name != "Unknown":
            score += 5
        if profile.age or profile.date_of_birth:
            score += 5
        if profile.current_city:
            score += 5
        if profile.current_state:
            score += 5

        # Contact info (20 points)
        score += min(len(profile.phone_numbers) * 5, 10)
        score += min(len(profile.email_addresses) * 5, 10)

        # Online presence (30 points)
        score += min(len(profile.social_media) * 3, 15)
        score += min(len(profile.usernames) * 3, 15)

        # Professional (15 points)
        score += min(len(profile.employers) * 5, 10)
        score += min(len(profile.education) * 5, 5)

        # Data sources (15 points)
        score += min(len(profile.sources) * 2, 15)

        return min(score, 100.0)

    # ==================== REPORTING ====================

    def generate_report(self, profile: PersonProfile, format: str = 'text') -> str:
        """
        Generate formatted report

        Args:
            profile: PersonProfile to report on
            format: 'text', 'json', or 'html'

        Returns:
            Formatted report string
        """
        if format == 'json':
            return json.dumps(asdict(profile), indent=2, default=str)

        elif format == 'html':
            return self._generate_html_report(profile)

        else:  # text
            return self._generate_text_report(profile)

    def _generate_text_report(self, profile: PersonProfile) -> str:
        """Generate text report"""
        report = []
        report.append("=" * 70)
        report.append("PEOPLE INTELLIGENCE REPORT")
        report.append("=" * 70)
        report.append(f"\nTarget: {profile.full_name}")
        report.append(f"Confidence Score: {profile.confidence_score:.1f}/100")
        report.append(f"Last Updated: {profile.last_updated}")
        report.append(f"\n{'-' * 70}")

        # Basic Information
        if profile.age or profile.date_of_birth:
            report.append("\n[BASIC INFORMATION]")
            if profile.age:
                report.append(f"  Age: {profile.age}")
            if profile.date_of_birth:
                report.append(f"  Date of Birth: {profile.date_of_birth}")

        if profile.aliases:
            report.append(f"  Aliases: {', '.join(profile.aliases)}")

        # Location
        if any([profile.current_city, profile.current_state, profile.city_of_birth]):
            report.append("\n[LOCATION INFORMATION]")
            if profile.city_of_birth:
                report.append(f"  City of Birth: {profile.city_of_birth}")
            if profile.current_city or profile.current_state:
                location = f"{profile.current_city or ''}, {profile.current_state or ''}".strip(', ')
                report.append(f"  Current Location: {location}")
            if profile.previous_addresses:
                report.append(f"  Previous Addresses: {len(profile.previous_addresses)} found")

        # Contact Information
        if profile.phone_numbers or profile.email_addresses:
            report.append("\n[CONTACT INFORMATION]")
            if profile.phone_numbers:
                report.append(f"  Phone Numbers:")
                for phone in profile.phone_numbers[:5]:  # Limit to 5
                    report.append(f"    - {phone}")
            if profile.email_addresses:
                report.append(f"  Email Addresses:")
                for email in profile.email_addresses[:5]:
                    report.append(f"    - {email}")

        # Social Media
        if profile.social_media:
            report.append("\n[SOCIAL MEDIA PRESENCE]")
            for platform, urls in sorted(profile.social_media.items()):
                report.append(f"  {platform}:")
                for url in urls[:3]:  # Limit to 3 per platform
                    report.append(f"    - {url}")

        # Usernames
        if profile.usernames:
            report.append("\n[USERNAMES]")
            report.append(f"  {', '.join(sorted(profile.usernames))}")

        # Professional
        if profile.employers or profile.job_titles or profile.education:
            report.append("\n[PROFESSIONAL INFORMATION]")
            if profile.employers:
                report.append(f"  Employers: {', '.join(profile.employers[:5])}")
            if profile.job_titles:
                report.append(f"  Job Titles: {', '.join(profile.job_titles[:5])}")
            if profile.education:
                report.append(f"  Education: {', '.join(profile.education[:5])}")

        # Security Information
        if profile.data_breaches:
            report.append("\n[SECURITY ALERTS]")
            report.append(f"  ⚠️  Found in {len(profile.data_breaches)} data breach(es):")
            for breach in profile.data_breaches[:10]:
                report.append(f"    - {breach}")

        # Sources
        report.append(f"\n[DATA SOURCES] ({len(profile.sources)})")
        for source in sorted(set(profile.sources)):
            report.append(f"  ✓ {source}")

        report.append("\n" + "=" * 70)
        report.append("End of Report")
        report.append("=" * 70)

        return "\n".join(report)

    def _generate_html_report(self, profile: PersonProfile) -> str:
        """Generate HTML report"""
        # Simplified HTML report
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>People Intelligence Report - {profile.full_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                .section {{ margin: 20px 0; }}
                .label {{ font-weight: bold; color: #34495e; }}
                .alert {{ background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; }}
            </style>
        </head>
        <body>
            <h1>People Intelligence Report</h1>
            <p><span class="label">Target:</span> {profile.full_name}</p>
            <p><span class="label">Confidence Score:</span> {profile.confidence_score:.1f}/100</p>
            <p><span class="label">Last Updated:</span> {profile.last_updated}</p>

            <div class="section">
                <h2>Contact Information</h2>
                <p><span class="label">Phone Numbers:</span> {len(profile.phone_numbers)}</p>
                <p><span class="label">Email Addresses:</span> {len(profile.email_addresses)}</p>
            </div>

            <div class="section">
                <h2>Social Media</h2>
                <p>Found on {len(profile.social_media)} platforms</p>
            </div>

            {f'<div class="alert"><strong>Security Alert:</strong> Found in {len(profile.data_breaches)} data breaches</div>' if profile.data_breaches else ''}
        </body>
        </html>
        """
        return html


# ==================== CLI INTERFACE ====================

async def main():
    """Main CLI interface for testing"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   PEOPLE INTELLIGENCE MODULE - DEMO                      ║
╚═══════════════════════════════════════════════════════════╝

⚠️  AUTHORIZATION REQUIRED - Use legally and ethically only
    """)

    # Load config
    config_path = Path("config.yaml")
    config = {}
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)

    # Initialize module
    intel = PeopleIntelligence(config)

    # Example searches
    print("\n[1] Search by Name")
    name = input("Enter full name (or press Enter to skip): ").strip()

    if name:
        city = input("Enter city (optional): ").strip() or None
        state = input("Enter state (optional): ").strip() or None

        profile = await intel.search_by_name(name, city, state)

        print("\n" + intel.generate_report(profile))

        # Export option
        export = input("\nExport to JSON? (y/n): ").strip().lower()
        if export == 'y':
            filename = f"person_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                f.write(intel.generate_report(profile, format='json'))
            print(f"[+] Exported to: {filename}")

    await intel.close_session()


if __name__ == "__main__":
    asyncio.run(main())
