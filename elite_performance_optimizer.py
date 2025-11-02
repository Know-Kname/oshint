#!/usr/bin/env python3
"""
Performance Optimization Module for Hughes Clues
Implements caching, parallel processing, and advanced data structures
"""

import asyncio
import functools
import threading
import time
from typing import Any, Callable, Dict, List, Set, TypeVar, Union
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis
import uvloop
import logging

# Type hints
T = TypeVar('T')
CacheKey = Union[str, int, tuple]
CacheValue = Any

class PerformanceOptimizer:
    """Optimization wrapper for intensive operations"""
    
    def __init__(self, cache_ttl: int = 3600, max_workers: int = None):
        self.cache_ttl = cache_ttl
        self.max_workers = max_workers or (threading.cpu_count() * 2)
        
        # Initialize caches
        self._memory_cache: Dict[CacheKey, CacheValue] = {}
        self._cache_timestamps: Dict[CacheKey, float] = {}
        self._cache_lock = threading.Lock()
        
        # Thread and process pools
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers // 2)
        
        # Async Redis connection
        self.redis = None
        
        # Metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'average_execution_time': [],
        }
    
    async def init_redis(self, redis_url: str):
        """Initialize Redis connection"""
        self.redis = await aioredis.from_url(redis_url)
    
    def memoize(self, ttl: int = None):
        """Memoization decorator with TTL"""
        def decorator(func: Callable):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                # Create cache key
                key = f"{func.__name__}:{hash(str(args))}-{hash(str(kwargs))}"
                
                # Check memory cache
                with self._cache_lock:
                    if key in self._memory_cache:
                        if time.time() - self._cache_timestamps[key] < (ttl or self.cache_ttl):
                            self.metrics['cache_hits'] += 1
                            return self._memory_cache[key]
                
                # Check Redis cache if available
                if self.redis:
                    cached = await self.redis.get(key)
                    if cached:
                        self.metrics['cache_hits'] += 1
                        return cached
                
                # Execute function
                self.metrics['cache_misses'] += 1
                start_time = time.time()
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Update metrics
                self.metrics['average_execution_time'].append(execution_time)
                
                # Cache result
                with self._cache_lock:
                    self._memory_cache[key] = result
                    self._cache_timestamps[key] = time.time()
                
                if self.redis:
                    await self.redis.set(key, result, ex=(ttl or self.cache_ttl))
                
                return result
            return wrapper
        return decorator
    
    async def parallel_map(self, func: Callable[[T], Any], items: List[T], 
                          use_processes: bool = False) -> List[Any]:
        """Execute function on items in parallel"""
        executor = self.process_pool if use_processes else self.thread_pool
        loop = asyncio.get_event_loop()
        
        # Wrap function for asyncio
        async def run_in_executor(item):
            return await loop.run_in_executor(executor, func, item)
        
        # Execute in parallel
        return await asyncio.gather(*[run_in_executor(item) for item in items])
    
    def optimize_data_structure(self, data: List[Dict]) -> csr_matrix:
        """Convert data to optimized sparse matrix"""
        # Extract text features
        vectorizer = TfidfVectorizer(max_features=1000)
        text_data = [str(item) for item in data]
        return vectorizer.fit_transform(text_data)
    
    async def batch_process(self, items: List[Any], batch_size: int, 
                           process_func: Callable[[List[Any]], Any]) -> List[Any]:
        """Process items in optimized batches"""
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_result = await process_func(batch)
            results.extend(batch_result)
        return results
    
    def get_metrics(self) -> Dict:
        """Return performance metrics"""
        avg_time = np.mean(self.metrics['average_execution_time']) if self.metrics['average_execution_time'] else 0
        return {
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_ratio': self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) 
                             if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0,
            'average_execution_time': avg_time,
            'total_executions': len(self.metrics['average_execution_time'])
        }
    
    def clear_cache(self):
        """Clear all caches"""
        with self._cache_lock:
            self._memory_cache.clear()
            self._cache_timestamps.clear()
        
        if self.redis:
            asyncio.create_task(self.redis.flushdb())
    
    async def cleanup(self):
        """Cleanup resources"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        if self.redis:
            await self.redis.close()

# Initialize uvloop for better async performance
try:
    uvloop.install()
except ImportError:
    logging.warning("uvloop not available, falling back to default event loop")