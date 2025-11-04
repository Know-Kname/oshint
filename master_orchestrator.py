#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

MASTER ORCHESTRATOR - Command Center for All Intelligence Operations
Coordinates: Recon | Scraping | AI Analysis | Credentials | Geo | Dark Web | Self-Improvement
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import json
from datetime import datetime
import logging
from pathlib import Path
import sys
import os
from enum import Enum
import importlib.util
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import queue
import threading
from pymongo import MongoClient
from redis import Redis
import yaml
import signal
import psutil
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of intelligence operations"""
    RECONNAISSANCE = "reconnaissance"
    WEB_SCRAPING = "web_scraping"
    AI_ANALYSIS = "ai_analysis"
    CREDENTIAL_HARVEST = "credential_harvest"
    GEOLOCATION = "geolocation"
    NETWORK_EXPLOIT = "network_exploit"
    DARK_WEB = "dark_web"
    SELF_IMPROVE = "self_improve"


class OperationStatus(Enum):
    """Operation status"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Operation:
    """Intelligence operation"""
    op_id: str
    op_type: OperationType
    target: str
    params: Dict[str, Any]
    status: OperationStatus = OperationStatus.QUEUED
    progress: float = 0.0
    result: Optional[Dict] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntelligenceReport:
    """Comprehensive intelligence report"""
    target: str
    report_id: str
    operations_completed: int
    total_operations: int
    reconnaissance: Optional[Dict] = None
    web_intelligence: Optional[Dict] = None
    ai_insights: Optional[Dict] = None
    credentials_found: Optional[Dict] = None
    geolocation_data: Optional[Dict] = None
    dark_web_intel: Optional[Dict] = None
    threat_assessment: Optional[Dict] = None
    risk_score: int = 0
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class ModuleLoader:
    """Dynamically load and manage intelligence modules"""

    def __init__(self, modules_dir: str = None):
        if modules_dir is None:
            # Try multiple possible locations in order of preference
            modules_dir = os.getenv('MODULES_DIR') or \
                         os.path.join(os.getenv('APP_DIR', '/app'), 'modules') or \
                         '/opt/hughes_clues/modules'

        self.modules_dir = Path(modules_dir)
        self.loaded_modules: Dict[str, Any] = {}
        
    def load_module(self, module_name: str) -> Any:
        """Load a module dynamically"""
        
        if module_name in self.loaded_modules:
            return self.loaded_modules[module_name]
        
        module_path = self.modules_dir / f"{module_name}.py"
        
        if not module_path.exists():
            logger.error(f"[!] Module not found: {module_path}")
            return None
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            self.loaded_modules[module_name] = module
            logger.info(f"[+] Loaded module: {module_name}")
            
            return module
            
        except Exception as e:
            logger.error(f"[!] Failed to load module {module_name}: {str(e)}")
            return None


class OperationQueue:
    """Thread-safe operation queue with priorities"""
    
    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.operations: Dict[str, Operation] = {}
        self.lock = threading.Lock()
        
    def add_operation(self, operation: Operation, priority: int = 5):
        """Add operation to queue"""
        with self.lock:
            self.operations[operation.op_id] = operation
            self.queue.put((priority, operation.op_id))
            logger.info(f"[+] Queued operation: {operation.op_id} ({operation.op_type.value})")
    
    def get_next_operation(self) -> Optional[Operation]:
        """Get next operation from queue"""
        try:
            _, op_id = self.queue.get(timeout=1)
            with self.lock:
                operation = self.operations.get(op_id)
                if operation:
                    operation.status = OperationStatus.RUNNING
                    operation.started_at = datetime.now()
                return operation
        except queue.Empty:
            return None
    
    def update_operation(self, op_id: str, status: OperationStatus, 
                        progress: float = None, result: Dict = None, error: str = None):
        """Update operation status"""
        with self.lock:
            if op_id in self.operations:
                op = self.operations[op_id]
                op.status = status
                
                if progress is not None:
                    op.progress = progress
                if result is not None:
                    op.result = result
                if error is not None:
                    op.error = error
                
                if status in [OperationStatus.COMPLETED, OperationStatus.FAILED]:
                    op.completed_at = datetime.now()
                    
                logger.info(f"[*] Operation {op_id} -> {status.value}")
    
    def get_operation(self, op_id: str) -> Optional[Operation]:
        """Get operation by ID"""
        with self.lock:
            return self.operations.get(op_id)
    
    def get_all_operations(self) -> List[Operation]:
        """Get all operations"""
        with self.lock:
            return list(self.operations.values())


class MasterOrchestrator:
    """Central intelligence operations coordinator"""

    def __init__(self, config_file: str = None):
        logger.info("""
╔═══════════════════════════════════════════════════════════╗
║   HUGHES CLUES - MASTER ORCHESTRATOR INITIALIZING        ║
╚═══════════════════════════════════════════════════════════╝
        """)

        if config_file is None:
            # Try multiple possible locations for config
            config_file = os.getenv('CONFIG_FILE') or \
                         os.path.join(os.getenv('APP_DIR', '/app'), 'config.yaml') or \
                         '/opt/hughes_clues/config.yaml'

        # Load configuration
        self.config = self.load_config(config_file)
        
        # Module loader
        self.module_loader = ModuleLoader()
        
        # Operation queue
        self.operation_queue = OperationQueue()
        
        # Worker threads
        self.worker_threads: List[threading.Thread] = []
        self.worker_loops: Dict[int, asyncio.AbstractEventLoop] = {}
        self.is_running = False
        self.max_workers = self.config.get('max_workers', 4)
        
        # Databases
        self.mongo_client = MongoClient(self.config.get('mongodb_uri', 'mongodb://localhost:27017'))
        self.db = self.mongo_client['hughes_clues']
        self.operations_collection = self.db['operations']
        self.reports_collection = self.db['reports']
        
        # Redis for real-time updates and caching
        self.redis = Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            decode_responses=True
        )
        self.cache_ttl = self.config.get('cache_ttl', 3600)  # 1 hour default
        
        # Statistics
        self.stats = {
            'operations_completed': 0,
            'operations_failed': 0,
            'total_execution_time': 0.0,
            'uptime_start': datetime.now()
        }
        
        logger.info("[+] Master Orchestrator initialized")
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"[+] Configuration loaded from {config_file}")
            return config
        except FileNotFoundError:
            logger.warning("[!] Config file not found, using defaults")
            return {}
    
    async def execute_reconnaissance(self, target: str, params: Dict) -> Dict:
        """Execute reconnaissance operation"""
        logger.info(f"[*] Starting reconnaissance on {target}")
        
        try:
            # Import elite_recon_module
            recon_module = self.module_loader.load_module('elite_recon_module')
            if not recon_module:
                raise Exception("Failed to load reconnaissance module")
            
            # Create config
            api_config = recon_module.APIConfig(**self.config.get('api_keys', {}))
            
            # Execute recon
            recon = recon_module.AdvancedReconModule(target, config=api_config)
            results = await recon.run_full_recon_async()
            
            logger.info(f"[+] Reconnaissance complete for {target}")
            return results
            
        except Exception as e:
            logger.error(f"[!] Reconnaissance failed: {str(e)}")
            raise
    
    async def execute_web_scraping(self, target: str, params: Dict) -> Dict:
        """Execute web scraping operation"""
        logger.info(f"[*] Starting web scraping on {target}")
        
        try:
            scraper_module = self.module_loader.load_module('elite_web_scraper')
            if not scraper_module:
                raise Exception("Failed to load scraper module")
            
            # Create config
            config = scraper_module.ScraperConfig(
                headless=params.get('headless', True),
                max_depth=params.get('max_depth', 2)
            )
            
            scraper = scraper_module.EliteWebScraper(config)
            await scraper.initialize()
            
            # Scrape
            await scraper.crawl_recursive(target, config.max_depth)
            
            results = {
                'urls_visited': len(scraper.visited_urls),
                'data_collected': len(scraper.scraped_data),
                'scraped_data': scraper.scraped_data[:100]  # Limit for report
            }
            
            await scraper.cleanup()
            
            logger.info(f"[+] Web scraping complete for {target}")
            return results
            
        except Exception as e:
            logger.error(f"[!] Web scraping failed: {str(e)}")
            raise
    
    async def execute_credential_harvest(self, target: str, params: Dict) -> Dict:
        """Execute credential harvesting"""
        logger.info(f"[*] Starting credential harvest for {target}")
        
        try:
            cred_module = self.module_loader.load_module('elite_credential_harvester')
            if not cred_module:
                raise Exception("Failed to load credential module")
            
            api_keys = self.config.get('api_keys', {})
            harvester = cred_module.EliteCredentialHarvester(api_keys)
            
            # Determine if target is email or domain
            if '@' in target:
                results = await harvester.harvest_email(target)
            else:
                results = await harvester.harvest_domain(target)
            
            await harvester.cleanup()
            
            logger.info(f"[+] Credential harvest complete for {target}")
            return results
            
        except Exception as e:
            logger.error(f"[!] Credential harvest failed: {str(e)}")
            raise
    
    async def execute_geolocation(self, target: str, params: Dict) -> Dict:
        """Execute geolocation intelligence"""
        logger.info(f"[*] Starting geolocation for {target}")
        
        try:
            geo_module = self.module_loader.load_module('elite_geolocation_intel')
            if not geo_module:
                raise Exception("Failed to load geolocation module")
            
            api_keys = self.config.get('api_keys', {})
            geo_intel = geo_module.EliteGeoIntelligence(api_keys)
            
            # Execute based on target type
            if params.get('type') == 'ip':
                intel = await geo_intel.analyze_ip(target)
                results = {'ip_intelligence': intel.__dict__}
            elif params.get('type') == 'image':
                results = geo_intel.analyze_image(target)
            elif params.get('type') == 'trace':
                hops = await geo_intel.trace_target(target)
                results = {'traceroute': hops}
            else:
                intel = await geo_intel.analyze_ip(target)
                results = {'ip_intelligence': intel.__dict__}
            
            await geo_intel.cleanup()
            
            logger.info(f"[+] Geolocation complete for {target}")
            return results
            
        except Exception as e:
            logger.error(f"[!] Geolocation failed: {str(e)}")
            raise
    
    async def execute_dark_web_monitor(self, target: str, params: Dict) -> Dict:
        """Execute dark web monitoring"""
        logger.info(f"[*] Starting dark web monitoring for {target}")
        
        try:
            darkweb_module = self.module_loader.load_module('elite_darkweb_monitor')
            if not darkweb_module:
                raise Exception("Failed to load dark web module")
            
            tor_password = self.config.get('tor_password')
            monitor = darkweb_module.EliteDarkWebMonitor(tor_password)
            
            if not await monitor.initialize():
                raise Exception("Failed to initialize Tor connection")
            
            # Execute monitoring
            keywords = params.get('keywords', [target])
            
            await monitor.discover_onion_sites([target], max_depth=1)
            await monitor.monitor_paste_sites(keywords)
            
            results = {
                'sites_monitored': monitor.intel.sites_monitored,
                'new_sites': monitor.intel.new_sites_discovered,
                'paste_entries': monitor.intel.paste_entries
            }
            
            await monitor.cleanup()
            
            logger.info(f"[+] Dark web monitoring complete")
            return results
            
        except Exception as e:
            logger.error(f"[!] Dark web monitoring failed: {str(e)}")
            raise
    
    async def execute_operation(self, operation: Operation):
        """Execute a single operation"""
        try:
            logger.info(f"[*] Executing operation: {operation.op_id}")
            
            # Route to appropriate handler
            if operation.op_type == OperationType.RECONNAISSANCE:
                result = await self.execute_reconnaissance(operation.target, operation.params)
            elif operation.op_type == OperationType.WEB_SCRAPING:
                result = await self.execute_web_scraping(operation.target, operation.params)
            elif operation.op_type == OperationType.CREDENTIAL_HARVEST:
                result = await self.execute_credential_harvest(operation.target, operation.params)
            elif operation.op_type == OperationType.GEOLOCATION:
                result = await self.execute_geolocation(operation.target, operation.params)
            elif operation.op_type == OperationType.DARK_WEB:
                result = await self.execute_dark_web_monitor(operation.target, operation.params)
            else:
                raise Exception(f"Unknown operation type: {operation.op_type}")
            
            # Update operation
            self.operation_queue.update_operation(
                operation.op_id,
                OperationStatus.COMPLETED,
                progress=100.0,
                result=result
            )
            
            # Update stats
            self.stats['operations_completed'] += 1
            
            # Store in database with proper serialization
            operation_doc = self._serialize_operation(operation)
            self.operations_collection.insert_one({
                'operation': operation_doc,
                'timestamp': datetime.now().isoformat()
            })
            
            # Publish to Redis for real-time updates
            self.redis.publish('operations', json.dumps({
                'op_id': operation.op_id,
                'status': 'completed',
                'result_preview': str(result)[:200]
            }))
            
        except Exception as e:
            logger.error(f"[!] Operation {operation.op_id} failed: {str(e)}")
            
            self.operation_queue.update_operation(
                operation.op_id,
                OperationStatus.FAILED,
                error=str(e)
            )
            
            self.stats['operations_failed'] += 1
    
    def worker_loop(self, worker_id: int):
        """Worker thread loop with persistent event loop"""
        logger.info(f"[*] Worker thread {worker_id} started")

        # Create and reuse event loop for this worker thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.worker_loops[worker_id] = loop

        try:
            while self.is_running:
                operation = self.operation_queue.get_next_operation()

                if operation:
                    try:
                        loop.run_until_complete(self.execute_operation(operation))
                    except Exception as e:
                        logger.error(f"[!] Worker {worker_id} error: {str(e)}")
                else:
                    time.sleep(0.5)
        finally:
            loop.close()
            del self.worker_loops[worker_id]
            logger.info(f"[*] Worker thread {worker_id} stopped")
    
    def start_workers(self):
        """Start worker threads"""
        self.is_running = True

        for i in range(self.max_workers):
            thread = threading.Thread(target=self.worker_loop, args=(i,), name=f"Worker-{i}")
            thread.daemon = True
            thread.start()
            self.worker_threads.append(thread)

        logger.info(f"[+] Started {self.max_workers} worker threads")
    
    def stop_workers(self):
        """Stop worker threads"""
        logger.info("[*] Stopping workers...")
        self.is_running = False
        
        for thread in self.worker_threads:
            thread.join(timeout=5)
        
        logger.info("[+] All workers stopped")
    
    async def run_full_intelligence_pipeline(self, target: str, 
                                            operations: List[OperationType] = None) -> IntelligenceReport:
        """Run complete intelligence pipeline on target"""
        
        logger.info(f"""
╔═══════════════════════════════════════════════════════════╗
║   FULL INTELLIGENCE PIPELINE: {target:^30s}   ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        if operations is None:
            operations = [
                OperationType.RECONNAISSANCE,
                OperationType.WEB_SCRAPING,
                OperationType.CREDENTIAL_HARVEST,
                OperationType.GEOLOCATION
            ]
        
        report_id = f"intel_{target.replace('.', '_')}_{int(time.time())}"
        
        # Queue all operations
        op_ids = []
        for op_type in operations:
            op_id = f"{op_type.value}_{target}_{int(time.time())}"
            
            operation = Operation(
                op_id=op_id,
                op_type=op_type,
                target=target,
                params={}
            )
            
            self.operation_queue.add_operation(operation, priority=5)
            op_ids.append(op_id)
        
        # Wait for all operations to complete
        while True:
            all_operations = [self.operation_queue.get_operation(op_id) for op_id in op_ids]
            
            completed = sum(1 for op in all_operations if op.status == OperationStatus.COMPLETED)
            failed = sum(1 for op in all_operations if op.status == OperationStatus.FAILED)
            
            if completed + failed == len(all_operations):
                break
            
            await asyncio.sleep(2)
        
        # Compile report
        report = IntelligenceReport(
            target=target,
            report_id=report_id,
            operations_completed=completed,
            total_operations=len(operations)
        )
        
        for op_id in op_ids:
            op = self.operation_queue.get_operation(op_id)
            
            if op.status == OperationStatus.COMPLETED and op.result:
                if op.op_type == OperationType.RECONNAISSANCE:
                    report.reconnaissance = op.result
                    report.risk_score = op.result.get('risk_score', 0)
                elif op.op_type == OperationType.WEB_SCRAPING:
                    report.web_intelligence = op.result
                elif op.op_type == OperationType.CREDENTIAL_HARVEST:
                    report.credentials_found = op.result
                elif op.op_type == OperationType.GEOLOCATION:
                    report.geolocation_data = op.result
                elif op.op_type == OperationType.DARK_WEB:
                    report.dark_web_intel = op.result
        
        # Calculate confidence
        report.confidence = completed / len(operations) if operations else 0.0
        
        # Store report with proper serialization
        report_doc = self._serialize_report(report)
        self.reports_collection.insert_one({
            'report': report_doc,
            'timestamp': datetime.now().isoformat()
        })
        
        logger.info(f"[+] Intelligence report generated: {report_id}")
        
        return report
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        process = psutil.Process()

        uptime = (datetime.now() - self.stats['uptime_start']).total_seconds()

        # Calculate success rate safely
        total_operations = self.stats['operations_completed'] + self.stats['operations_failed']
        success_rate = (
            self.stats['operations_completed'] / total_operations
            if total_operations > 0
            else 0.0
        )

        return {
            'uptime_seconds': uptime,
            'operations_completed': self.stats['operations_completed'],
            'operations_failed': self.stats['operations_failed'],
            'success_rate': success_rate,
            'cpu_percent': process.cpu_percent(),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'threads': len(self.worker_threads),
            'queued_operations': self.operation_queue.queue.qsize()
        }
    
    def cache_result(self, key: str, value: Any, ttl: int = None) -> bool:
        """Cache a result in Redis"""
        try:
            ttl = ttl or self.cache_ttl
            self.redis.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            logger.debug(f"[+] Cached result: {key}")
            return True
        except Exception as e:
            logger.error(f"[!] Cache write error: {str(e)}")
            return False

    def get_cached_result(self, key: str) -> Optional[Dict]:
        """Retrieve a cached result from Redis"""
        try:
            data = self.redis.get(key)
            if data:
                logger.debug(f"[+] Cache hit: {key}")
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"[!] Cache read error: {str(e)}")
            return None

    def invalidate_cache(self, pattern: str) -> int:
        """Invalidate cached results by pattern"""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                count = self.redis.delete(*keys)
                logger.debug(f"[+] Invalidated {count} cache entries")
                return count
            return 0
        except Exception as e:
            logger.error(f"[!] Cache invalidation error: {str(e)}")
            return 0

    @staticmethod
    def _serialize_operation(operation: 'Operation') -> Dict:
        """Serialize operation to MongoDB-compatible dict"""
        doc = {
            'op_id': operation.op_id,
            'op_type': operation.op_type.value,
            'target': operation.target,
            'params': operation.params,
            'status': operation.status.value,
            'progress': operation.progress,
            'result': operation.result,
            'error': operation.error,
            'created_at': operation.created_at.isoformat() if operation.created_at else None,
            'started_at': operation.started_at.isoformat() if operation.started_at else None,
            'completed_at': operation.completed_at.isoformat() if operation.completed_at else None,
        }
        return doc

    @staticmethod
    def _serialize_report(report: 'IntelligenceReport') -> Dict:
        """Serialize intelligence report to MongoDB-compatible dict"""
        doc = {
            'target': report.target,
            'report_id': report.report_id,
            'operations_completed': report.operations_completed,
            'total_operations': report.total_operations,
            'reconnaissance': report.reconnaissance,
            'web_intelligence': report.web_intelligence,
            'ai_insights': report.ai_insights,
            'credentials_found': report.credentials_found,
            'geolocation_data': report.geolocation_data,
            'dark_web_intel': report.dark_web_intel,
            'threat_assessment': report.threat_assessment,
            'risk_score': report.risk_score,
            'confidence': report.confidence,
            'timestamp': report.timestamp.isoformat() if report.timestamp else None,
        }
        return doc

    def shutdown(self):
        """Graceful shutdown"""
        logger.info("[*] Initiating graceful shutdown...")
        
        self.stop_workers()
        self.mongo_client.close()
        self.redis.close()
        
        logger.info("[+] Master Orchestrator shutdown complete")


async def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hughes Clues Master Orchestrator')
    parser.add_argument('--target', help='Target for intelligence gathering')
    parser.add_argument('--config', default='/opt/hughes_clues/config.yaml', help='Config file')
    parser.add_argument('--operations', nargs='+', 
                       choices=['recon', 'scrape', 'creds', 'geo', 'darkweb'],
                       help='Operations to run')
    parser.add_argument('--workers', type=int, default=4, help='Number of worker threads')
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = MasterOrchestrator(args.config)
    orchestrator.max_workers = args.workers
    
    # Start workers
    orchestrator.start_workers()
    
    # Handle shutdown
    def signal_handler(signum, frame):
        orchestrator.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.target:
            # Map operation names to enums
            op_map = {
                'recon': OperationType.RECONNAISSANCE,
                'scrape': OperationType.WEB_SCRAPING,
                'creds': OperationType.CREDENTIAL_HARVEST,
                'geo': OperationType.GEOLOCATION,
                'darkweb': OperationType.DARK_WEB
            }
            
            operations = [op_map[op] for op in args.operations] if args.operations else None
            
            # Run full pipeline
            report = await orchestrator.run_full_intelligence_pipeline(args.target, operations)
            
            print(f"\n{'='*60}")
            print(f"INTELLIGENCE REPORT: {args.target}")
            print(f"{'='*60}")
            print(f"Report ID: {report.report_id}")
            print(f"Operations Completed: {report.operations_completed}/{report.total_operations}")
            print(f"Risk Score: {report.risk_score}/100")
            print(f"Confidence: {report.confidence:.2%}")
            
        else:
            # Run as daemon
            logger.info("[*] Running as daemon - Ctrl+C to stop")
            
            while True:
                stats = orchestrator.get_system_stats()
                logger.info(f"Stats: {stats['operations_completed']} completed, "
                          f"{stats['queued_operations']} queued, "
                          f"CPU: {stats['cpu_percent']:.1f}%")
                await asyncio.sleep(10)
    
    finally:
        orchestrator.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
