#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

Elite Geolocation Intelligence
IP Geolocation | EXIF Data | WiFi/Cell Tower Mapping | Satellite Imagery | OSINT Fusion
"""

import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import json
from datetime import datetime
import re
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import ipaddress
import socket
import struct
import geoip2.database
import geoip2.errors
from collections import defaultdict
import numpy as np
import logging
from pymongo import MongoClient
import sqlite3
import base64
import io
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GeoLocation:
    """Geolocation data structure"""
    latitude: float
    longitude: float
    accuracy: float = 0.0
    altitude: Optional[float] = None
    source: str = "unknown"
    timestamp: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    additional_data: Dict = field(default_factory=dict)
    confidence: float = 0.0


@dataclass
class IPIntelligence:
    """IP geolocation intelligence"""
    ip: str
    location: Optional[GeoLocation] = None
    isp: Optional[str] = None
    organization: Optional[str] = None
    asn: Optional[str] = None
    is_vpn: bool = False
    is_proxy: bool = False
    is_tor: bool = False
    is_hosting: bool = False
    threat_level: str = "low"
    open_ports: List[int] = field(default_factory=list)
    reverse_dns: Optional[str] = None


class IPGeolocationEngine:
    """Advanced IP geolocation with multiple sources"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.session = None
        self.geoip_reader = None
        
        # Try to load GeoIP2 database
        try:
            self.geoip_reader = geoip2.database.Reader('/usr/share/GeoIP/GeoLite2-City.mmdb')
            logger.info("[+] GeoIP2 database loaded")
        except:
            logger.warning("[!] GeoIP2 database not found - install GeoLite2-City.mmdb")
    
    async def create_session(self):
        """Create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close session"""
        if self.session:
            await self.session.close()
    
    async def geolocate_ip_multi_source(self, ip: str) -> IPIntelligence:
        """Geolocate IP using multiple sources for accuracy"""
        logger.info(f"[*] Geolocating IP: {ip}")
        
        intel = IPIntelligence(ip=ip)
        
        # Source 1: GeoIP2 database (offline, fast)
        if self.geoip_reader:
            try:
                response = self.geoip_reader.city(ip)
                intel.location = GeoLocation(
                    latitude=response.location.latitude,
                    longitude=response.location.longitude,
                    accuracy=response.location.accuracy_radius,
                    city=response.city.name,
                    region=response.subdivisions.most_specific.name if response.subdivisions else None,
                    country=response.country.name,
                    postal_code=response.postal.code,
                    source='geoip2',
                    confidence=0.8
                )
                logger.info(f"[+] GeoIP2: {response.city.name}, {response.country.name}")
            except geoip2.errors.AddressNotFoundError:
                logger.warning("[!] IP not found in GeoIP2 database")
        
        # Source 2: IPapi.co (free, good accuracy)
        try:
            await self.create_session()
            async with self.session.get(f"https://ipapi.co/{ip}/json/", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not intel.location:
                        intel.location = GeoLocation(
                            latitude=data.get('latitude'),
                            longitude=data.get('longitude'),
                            city=data.get('city'),
                            region=data.get('region'),
                            country=data.get('country_name'),
                            postal_code=data.get('postal'),
                            source='ipapi',
                            confidence=0.7
                        )
                    
                    intel.isp = data.get('org')
                    intel.asn = data.get('asn')
                    logger.info(f"[+] IPapi: {data.get('city')}, {data.get('country_name')}")
        except Exception as e:
            logger.debug(f"[!] IPapi error: {str(e)}")
        
        # Source 3: ip-api.com (free, no rate limit)
        try:
            async with self.session.get(f"http://ip-api.com/json/{ip}", timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        # Cross-reference with existing data
                        if intel.location:
                            # Average coordinates for better accuracy
                            intel.location.latitude = (intel.location.latitude + data.get('lat')) / 2
                            intel.location.longitude = (intel.location.longitude + data.get('lon')) / 2
                        
                        intel.organization = data.get('org')
                        intel.is_proxy = data.get('proxy', False)
                        
                        if not intel.isp:
                            intel.isp = data.get('isp')
                        
                        logger.info(f"[+] IP-API: {data.get('city')}, {data.get('country')}")
        except Exception as e:
            logger.debug(f"[!] IP-API error: {str(e)}")
        
        # Source 4: IPInfo.io (requires API key for advanced features)
        ipinfo_key = self.api_keys.get('ipinfo')
        if ipinfo_key:
            try:
                url = f"https://ipinfo.io/{ip}?token={ipinfo_key}"
                async with self.session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'privacy' in data:
                            intel.is_vpn = data['privacy'].get('vpn', False)
                            intel.is_proxy = data['privacy'].get('proxy', False)
                            intel.is_tor = data['privacy'].get('tor', False)
                            intel.is_hosting = data['privacy'].get('hosting', False)
                        
                        logger.info("[+] IPInfo: Privacy check complete")
            except Exception as e:
                logger.debug(f"[!] IPInfo error: {str(e)}")
        
        # Source 5: Shodan (requires API key)
        shodan_key = self.api_keys.get('shodan')
        if shodan_key:
            try:
                url = f"https://api.shodan.io/shodan/host/{ip}?key={shodan_key}"
                async with self.session.get(url, timeout=15) as response:
                    if response.status == 200:
                        data = await response.json()
                        intel.open_ports = data.get('ports', [])
                        intel.organization = data.get('org') or intel.organization
                        
                        # Check for vulnerabilities
                        if data.get('vulns'):
                            intel.threat_level = 'high'
                        
                        logger.info(f"[+] Shodan: {len(intel.open_ports)} open ports")
            except Exception as e:
                logger.debug(f"[!] Shodan error: {str(e)}")
        
        # Reverse DNS lookup
        try:
            intel.reverse_dns = socket.gethostbyaddr(ip)[0]
            logger.info(f"[+] Reverse DNS: {intel.reverse_dns}")
        except Exception as e:
            logger.debug(f"[!] Reverse DNS lookup failed for {ip}: {str(e)}")
            intel.reverse_dns = None
        
        # Calculate threat level
        if intel.is_tor or (intel.is_proxy and intel.is_vpn):
            intel.threat_level = 'high'
        elif intel.is_proxy or intel.is_vpn:
            intel.threat_level = 'medium'
        
        return intel
    
    async def trace_route(self, target: str) -> List[Dict]:
        """Trace route to target asynchronously without blocking event loop"""
        logger.info(f"[*] Tracing route to {target}")

        import asyncio
        import os

        try:
            # Determine correct command based on OS
            cmd = 'tracert' if os.name == 'nt' else 'traceroute'
            cmd_args = [cmd, target]
            if os.name != 'nt':  # Linux/Mac specific args
                cmd_args.extend(['-n', '-m', '30'])

            # Run asynchronously without blocking event loop
            proc = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for process with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=30.0
                )
            except asyncio.TimeoutError:
                logger.warning(f"[!] Traceroute timeout for {target}")
                return []

            if proc.returncode != 0:
                logger.warning(f"[!] Traceroute failed: {stderr_bytes.decode()}")
                return []

            # Parse output
            output = stdout_bytes.decode()
            hops = []

            for line in output.split('\n'):
                # Parse traceroute output for IP addresses
                match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                if match:
                    hop_ip = match.group(1)
                    if hop_ip != '* * *':
                        try:
                            intel = await self.geolocate_ip_multi_source(hop_ip)
                            hops.append({
                                'hop': len(hops) + 1,
                                'ip': hop_ip,
                                'location': intel.location if intel else 'Unknown',
                                'isp': intel.isp if intel else 'Unknown'
                            })
                        except Exception as e:
                            logger.debug(f"[!] Failed to geolocate hop {hop_ip}: {str(e)}")
                            hops.append({
                                'hop': len(hops) + 1,
                                'ip': hop_ip,
                                'location': 'Unknown',
                                'isp': 'Unknown'
                            })

            logger.info(f"[+] Traced {len(hops)} hops to {target}")
            return hops

        except Exception as e:
            logger.error(f"[!] Traceroute failed for {target}: {str(e)}")
            return []


class EXIFExtractor:
    """Extract geolocation from image EXIF data"""
    
    def __init__(self):
        self.geolocator = Nominatim(user_agent="hughes-clues-osint")
    
    def extract_exif(self, image_path: str) -> Dict:
        """Extract all EXIF data from image"""
        logger.info(f"[*] Extracting EXIF from {image_path}")
        
        try:
            image = Image.open(image_path)
            exif_data = {}
            
            info = image._getexif()
            if not info:
                logger.warning("[!] No EXIF data found")
                return {}
            
            for tag, value in info.items():
                tag_name = TAGS.get(tag, tag)
                exif_data[tag_name] = value
            
            logger.info(f"[+] Extracted {len(exif_data)} EXIF fields")
            return exif_data
            
        except Exception as e:
            logger.error(f"[!] EXIF extraction error: {str(e)}")
            return {}
    
    def extract_gps_data(self, exif_data: Dict) -> Optional[GeoLocation]:
        """Extract GPS coordinates from EXIF data"""
        
        if 'GPSInfo' not in exif_data:
            logger.warning("[!] No GPS data in EXIF")
            return None
        
        gps_info = exif_data['GPSInfo']
        
        def convert_to_degrees(value):
            """Convert GPS coordinates to degrees"""
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)
        
        try:
            # Extract latitude
            lat = convert_to_degrees(gps_info[2])
            if gps_info[1] == 'S':
                lat = -lat
            
            # Extract longitude
            lon = convert_to_degrees(gps_info[4])
            if gps_info[3] == 'W':
                lon = -lon
            
            # Extract altitude
            altitude = None
            if 6 in gps_info:
                altitude = float(gps_info[6])
            
            # Extract timestamp
            timestamp = None
            if 29 in gps_info:
                timestamp = gps_info[29]
            
            location = GeoLocation(
                latitude=lat,
                longitude=lon,
                altitude=altitude,
                source='exif',
                timestamp=str(timestamp),
                confidence=0.95
            )
            
            # Reverse geocode to get address
            try:
                address = self.geolocator.reverse(f"{lat}, {lon}", language='en')
                if address:
                    location.address = address.address
                    location.city = address.raw.get('address', {}).get('city')
                    location.country = address.raw.get('address', {}).get('country')
            except Exception as e:
                logger.debug(f"[!] Reverse geocoding error: {str(e)}")
            
            logger.info(f"[+] GPS coordinates: {lat}, {lon}")
            return location
            
        except Exception as e:
            logger.error(f"[!] GPS extraction error: {str(e)}")
            return None
    
    def extract_camera_info(self, exif_data: Dict) -> Dict:
        """Extract camera and device information"""
        
        camera_info = {
            'make': exif_data.get('Make'),
            'model': exif_data.get('Model'),
            'software': exif_data.get('Software'),
            'datetime': exif_data.get('DateTime'),
            'datetime_original': exif_data.get('DateTimeOriginal'),
            'orientation': exif_data.get('Orientation')
        }
        
        return {k: v for k, v in camera_info.items() if v}


class WiFiGeolocation:
    """WiFi-based geolocation"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.session = None
    
    async def create_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def geolocate_by_wifi(self, wifi_access_points: List[Dict]) -> Optional[GeoLocation]:
        """
        Geolocate using WiFi access points
        wifi_access_points format: [{'macAddress': 'XX:XX:XX:XX:XX:XX', 'signalStrength': -50}, ...]
        """
        
        if not self.api_key:
            logger.warning("[!] Google Geolocation API key required")
            return None
        
        logger.info(f"[*] Geolocating using {len(wifi_access_points)} WiFi APs")
        
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.api_key}"
        
        payload = {
            'considerIp': False,
            'wifiAccessPoints': wifi_access_points
        }
        
        try:
            await self.create_session()
            async with self.session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    location = GeoLocation(
                        latitude=data['location']['lat'],
                        longitude=data['location']['lng'],
                        accuracy=data.get('accuracy', 0),
                        source='wifi',
                        confidence=0.85
                    )
                    
                    logger.info(f"[+] WiFi location: {location.latitude}, {location.longitude}")
                    return location
                    
        except Exception as e:
            logger.error(f"[!] WiFi geolocation error: {str(e)}")
            return None
    
    async def close_session(self):
        if self.session:
            await self.session.close()


class CellTowerGeolocation:
    """Cell tower based geolocation"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.session = None
    
    async def create_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def geolocate_by_cell_tower(self, cell_towers: List[Dict]) -> Optional[GeoLocation]:
        """
        Geolocate using cell towers
        cell_towers format: [{'cellId': 123, 'locationAreaCode': 456, 'mobileCountryCode': 310, 'mobileNetworkCode': 410}, ...]
        """
        
        if not self.api_key:
            logger.warning("[!] Google Geolocation API key required")
            return None
        
        logger.info(f"[*] Geolocating using {len(cell_towers)} cell towers")
        
        url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={self.api_key}"
        
        payload = {
            'considerIp': False,
            'cellTowers': cell_towers
        }
        
        try:
            await self.create_session()
            async with self.session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    location = GeoLocation(
                        latitude=data['location']['lat'],
                        longitude=data['location']['lng'],
                        accuracy=data.get('accuracy', 0),
                        source='cell_tower',
                        confidence=0.75
                    )
                    
                    logger.info(f"[+] Cell tower location: {location.latitude}, {location.longitude}")
                    return location
                    
        except Exception as e:
            logger.error(f"[!] Cell tower geolocation error: {str(e)}")
            return None
    
    async def close_session(self):
        if self.session:
            await self.session.close()


class GeoIntelligenceFusion:
    """Fuse multiple geolocation sources for maximum accuracy"""
    
    def __init__(self):
        self.locations: List[GeoLocation] = []
        self.geolocator = Nominatim(user_agent="hughes-clues-osint")
    
    def add_location(self, location: GeoLocation):
        """Add a location source"""
        if location and location.latitude and location.longitude:
            self.locations.append(location)
    
    def fuse_locations(self) -> Optional[GeoLocation]:
        """Fuse multiple location sources using weighted average"""
        if not self.locations:
            return None
        
        logger.info(f"[*] Fusing {len(self.locations)} location sources")
        
        # Weight by confidence
        total_weight = sum(loc.confidence for loc in self.locations)
        
        if total_weight == 0:
            # Use simple average
            avg_lat = np.mean([loc.latitude for loc in self.locations])
            avg_lon = np.mean([loc.longitude for loc in self.locations])
        else:
            # Weighted average
            avg_lat = sum(loc.latitude * loc.confidence for loc in self.locations) / total_weight
            avg_lon = sum(loc.longitude * loc.confidence for loc in self.locations) / total_weight
        
        # Calculate accuracy (max distance from fused location)
        fused = (avg_lat, avg_lon)
        max_distance = max(
            geodesic(fused, (loc.latitude, loc.longitude)).meters
            for loc in self.locations
        )
        
        fused_location = GeoLocation(
            latitude=avg_lat,
            longitude=avg_lon,
            accuracy=max_distance,
            source='fused',
            confidence=min(total_weight / len(self.locations), 1.0)
        )
        
        # Reverse geocode
        try:
            address = self.geolocator.reverse(f"{avg_lat}, {avg_lon}", language='en')
            if address:
                fused_location.address = address.address
                fused_location.city = address.raw.get('address', {}).get('city')
                fused_location.country = address.raw.get('address', {}).get('country')
        except Exception as e:
            logger.debug(f"[!] Reverse geocoding failed for {avg_lat}, {avg_lon}: {str(e)}")
        
        logger.info(f"[+] Fused location: {avg_lat}, {avg_lon} (accuracy: {max_distance:.0f}m)")
        return fused_location
    
    def calculate_confidence_radius(self) -> float:
        """Calculate confidence radius in meters"""
        if len(self.locations) < 2:
            return 0.0
        
        # Calculate standard deviation of distances
        center = (
            np.mean([loc.latitude for loc in self.locations]),
            np.mean([loc.longitude for loc in self.locations])
        )
        
        distances = [
            geodesic(center, (loc.latitude, loc.longitude)).meters
            for loc in self.locations
        ]
        
        return float(np.std(distances))


class MapGenerator:
    """Generate interactive maps with geolocation data"""
    
    def __init__(self):
        pass
    
    def create_location_map(self, locations: List[GeoLocation], 
                           center: Optional[Tuple[float, float]] = None,
                           output_file: str = "geolocation_map.html"):
        """Create interactive map with all locations"""
        
        if not locations:
            logger.warning("[!] No locations to map")
            return
        
        # Calculate center if not provided
        if not center:
            center = (
                np.mean([loc.latitude for loc in locations]),
                np.mean([loc.longitude for loc in locations])
            )
        
        # Create map
        m = folium.Map(location=center, zoom_start=12)
        
        # Add markers for each location
        colors = {
            'ip': 'red',
            'exif': 'green',
            'wifi': 'blue',
            'cell_tower': 'orange',
            'fused': 'purple',
            'unknown': 'gray'
        }
        
        for loc in locations:
            color = colors.get(loc.source, 'gray')
            
            popup_text = f"""
            <b>Source:</b> {loc.source}<br>
            <b>Coordinates:</b> {loc.latitude:.6f}, {loc.longitude:.6f}<br>
            <b>Accuracy:</b> {loc.accuracy:.0f}m<br>
            <b>Confidence:</b> {loc.confidence:.2f}<br>
            """
            
            if loc.address:
                popup_text += f"<b>Address:</b> {loc.address}<br>"
            if loc.city:
                popup_text += f"<b>City:</b> {loc.city}<br>"
            
            folium.Marker(
                location=[loc.latitude, loc.longitude],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
            
            # Add accuracy circle
            if loc.accuracy > 0:
                folium.Circle(
                    location=[loc.latitude, loc.longitude],
                    radius=loc.accuracy,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.1
                ).add_to(m)
        
        # Save map
        m.save(output_file)
        logger.info(f"[+] Interactive map saved to {output_file}")
        
        return output_file
    
    def create_route_map(self, hops: List[Dict], output_file: str = "traceroute_map.html"):
        """Create map showing traceroute path"""
        
        if not hops:
            return
        
        # Filter hops with valid locations
        valid_hops = [h for h in hops if h.get('location')]
        
        if not valid_hops:
            return
        
        # Calculate center
        center = (
            np.mean([h['location'].latitude for h in valid_hops]),
            np.mean([h['location'].longitude for h in valid_hops])
        )
        
        # Create map
        m = folium.Map(location=center, zoom_start=4)
        
        # Add markers and lines
        coordinates = []
        for hop in valid_hops:
            loc = hop['location']
            coordinates.append([loc.latitude, loc.longitude])
            
            folium.Marker(
                location=[loc.latitude, loc.longitude],
                popup=f"Hop {hop['hop']}: {hop['ip']}<br>{hop.get('isp', 'Unknown ISP')}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(m)
        
        # Draw path
        if len(coordinates) > 1:
            folium.PolyLine(
                coordinates,
                color='red',
                weight=2,
                opacity=0.8
            ).add_to(m)
        
        m.save(output_file)
        logger.info(f"[+] Route map saved to {output_file}")
        
        return output_file


class EliteGeoIntelligence:
    """Master geolocation intelligence orchestrator"""
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.ip_engine = IPGeolocationEngine(api_keys)
        self.exif_extractor = EXIFExtractor()
        self.wifi_locator = WiFiGeolocation(api_keys.get('google_geolocation'))
        self.cell_locator = CellTowerGeolocation(api_keys.get('google_geolocation'))
        self.fusion = GeoIntelligenceFusion()
        self.map_generator = MapGenerator()
        
        # Storage
        self.mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = self.mongo_client['hughes_clues']
        self.geo_collection = self.db['geolocation']
    
    async def analyze_ip(self, ip: str) -> IPIntelligence:
        """Comprehensive IP intelligence"""
        intel = await self.ip_engine.geolocate_ip_multi_source(ip)
        
        if intel.location:
            self.fusion.add_location(intel.location)
        
        # Store in database
        self.geo_collection.insert_one({
            'type': 'ip',
            'ip': ip,
            'intel': intel.__dict__,
            'timestamp': datetime.now().isoformat()
        })
        
        return intel
    
    def analyze_image(self, image_path: str) -> Dict:
        """Extract geolocation from image"""
        exif_data = self.exif_extractor.extract_exif(image_path)
        gps_location = self.exif_extractor.extract_gps_data(exif_data)
        camera_info = self.exif_extractor.extract_camera_info(exif_data)
        
        if gps_location:
            self.fusion.add_location(gps_location)
        
        result = {
            'image': image_path,
            'exif_data': exif_data,
            'location': gps_location,
            'camera_info': camera_info
        }
        
        # Store in database
        self.geo_collection.insert_one({
            'type': 'image',
            'image_path': image_path,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    async def trace_target(self, target: str) -> List[Dict]:
        """Trace route and geolocate each hop"""
        hops = await self.ip_engine.trace_route(target)
        
        # Create map
        if hops:
            self.map_generator.create_route_map(hops, f"traceroute_{target}.html")
        
        return hops
    
    def generate_intelligence_report(self, output_file: str = None) -> str:
        """Generate comprehensive geolocation intelligence report"""
        
        if output_file is None:
            output_file = f"geo_intel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Get fused location
        fused_location = self.fusion.fuse_locations()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_sources': len(self.fusion.locations),
            'individual_locations': [loc.__dict__ for loc in self.fusion.locations],
            'fused_location': fused_location.__dict__ if fused_location else None,
            'confidence_radius': self.fusion.calculate_confidence_radius()
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Create map
        if self.fusion.locations:
            map_file = output_file.replace('.json', '_map.html')
            self.map_generator.create_location_map(self.fusion.locations, output_file=map_file)
        
        logger.info(f"[+] Intelligence report saved to {output_file}")
        return output_file
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.ip_engine.close_session()
        await self.wifi_locator.close_session()
        await self.cell_locator.close_session()
        self.mongo_client.close()


async def main():
    """Demo execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hughes Clues Elite Geolocation Intelligence')
    parser.add_argument('--ip', help='IP address to geolocate')
    parser.add_argument('--image', help='Image file to analyze')
    parser.add_argument('--trace', help='Target to traceroute')
    parser.add_argument('--config', help='Config file with API keys')
    parser.add_argument('--output', help='Output filename')
    
    args = parser.parse_args()
    
    # Load API keys
    api_keys = {}
    if args.config:
        with open(args.config, 'r') as f:
            import yaml
            config = yaml.safe_load(f)
            api_keys = config.get('api_keys', {})
    
    geo_intel = EliteGeoIntelligence(api_keys)
    
    try:
        if args.ip:
            intel = await geo_intel.analyze_ip(args.ip)
            print(f"\n{'='*60}")
            print(f"IP INTELLIGENCE: {args.ip}")
            print(f"{'='*60}")
            if intel.location:
                print(f"Location: {intel.location.city}, {intel.location.country}")
                print(f"Coordinates: {intel.location.latitude}, {intel.location.longitude}")
            print(f"ISP: {intel.isp}")
            print(f"Threat Level: {intel.threat_level}")
        
        if args.image:
            result = geo_intel.analyze_image(args.image)
            if result['location']:
                print(f"\n{'='*60}")
                print(f"IMAGE GEOLOCATION: {args.image}")
                print(f"{'='*60}")
                print(f"Coordinates: {result['location'].latitude}, {result['location'].longitude}")
                print(f"Address: {result['location'].address}")
        
        if args.trace:
            hops = await geo_intel.trace_target(args.trace)
            print(f"\n{'='*60}")
            print(f"TRACEROUTE: {args.trace}")
            print(f"{'='*60}")
            for hop in hops:
                print(f"Hop {hop['hop']}: {hop['ip']} - {hop.get('isp', 'Unknown')}")
        
        # Generate report
        geo_intel.generate_intelligence_report(args.output)
        
    finally:
        await geo_intel.cleanup()


if __name__ == '__main__':
    asyncio.run(main())
