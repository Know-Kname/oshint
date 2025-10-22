#!/usr/bin/env python3
"""
╦ ╦╦ ╦╔═╗╦ ╦╔═╗╔═╗  ╔═╗╦  ╦ ╦╔═╗╔═╗ - ELITE EDITION
╠═╣║ ║║ ╦╠═╣║╣ ╚═╗  ║  ║  ║ ║║╣ ╚═╝
╩ ╩╚═╝╚═╝╩ ╩╚═╝╚═╝  ╚═╝╩═╝╚═╝╚═╝╚═╝

Elite Self-Improvement Engine
Autonomous Code Optimization | GPT-4 Integration | Performance Monitoring | A/B Testing
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import json
from datetime import datetime
import ast
import astor
import subprocess
import sys
import os
from pathlib import Path
import time
import cProfile
import pstats
import io
import re
from collections import defaultdict
import logging
import git
from anthropic import Anthropic
from openai import AsyncOpenAI
import docker
import tempfile
import shutil
import hashlib
from pymongo import MongoClient
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance measurement data"""
    module_name: str
    function_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    error_count: int
    iterations: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CodeImprovement:
    """Code improvement suggestion"""
    module: str
    function: str
    original_code: str
    improved_code: str
    improvement_type: str
    expected_gain: float
    tested: bool = False
    deployed: bool = False
    actual_gain: Optional[float] = None
    confidence_score: float = 0.0


@dataclass
class TestResult:
    """A/B test result"""
    test_id: str
    variant_a_metrics: PerformanceMetrics
    variant_b_metrics: PerformanceMetrics
    improvement_percentage: float
    statistical_significance: float
    winner: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PerformanceMonitor:
    """Monitor and profile code performance"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.profiler = None
        
    def profile_function(self, func, *args, **kwargs) -> Tuple[Any, PerformanceMetrics]:
        """Profile a function's performance"""
        import tracemalloc
        import psutil
        
        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        
        # Start time
        start_time = time.time()
        start_cpu = process.cpu_percent()
        
        # Execute function
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
            logger.error(f"[!] Function execution error: {error}")
        
        # End measurements
        end_time = time.time()
        end_cpu = process.cpu_percent()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        metrics = PerformanceMetrics(
            module_name=func.__module__,
            function_name=func.__name__,
            execution_time=end_time - start_time,
            memory_usage=peak / 1024 / 1024,  # MB
            cpu_usage=(start_cpu + end_cpu) / 2,
            success_rate=1.0 if success else 0.0,
            error_count=0 if success else 1,
            iterations=1
        )
        
        self.metrics.append(metrics)
        
        logger.info(f"[*] Profiled {func.__name__}: {metrics.execution_time:.4f}s, {metrics.memory_usage:.2f}MB")
        
        return result, metrics
    
    def profile_code_block(self, code: str, globals_dict: Dict = None) -> PerformanceMetrics:
        """Profile a code block"""
        if globals_dict is None:
            globals_dict = {}
        
        profiler = cProfile.Profile()
        
        start_time = time.time()
        
        try:
            profiler.enable()
            exec(code, globals_dict)
            profiler.disable()
            success = True
        except Exception as e:
            logger.error(f"[!] Code execution error: {str(e)}")
            success = False
        
        end_time = time.time()
        
        # Get stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        metrics = PerformanceMetrics(
            module_name='code_block',
            function_name='exec',
            execution_time=end_time - start_time,
            memory_usage=0.0,
            cpu_usage=0.0,
            success_rate=1.0 if success else 0.0,
            error_count=0 if success else 1,
            iterations=1
        )
        
        return metrics
    
    def benchmark_function(self, func, iterations: int = 100, *args, **kwargs) -> PerformanceMetrics:
        """Benchmark function over multiple iterations"""
        
        execution_times = []
        memory_usages = []
        errors = 0
        
        for i in range(iterations):
            try:
                _, metrics = self.profile_function(func, *args, **kwargs)
                execution_times.append(metrics.execution_time)
                memory_usages.append(metrics.memory_usage)
            except Exception as e:
                errors += 1
                logger.debug(f"[!] Iteration {i} failed: {str(e)}")
        
        avg_metrics = PerformanceMetrics(
            module_name=func.__module__,
            function_name=func.__name__,
            execution_time=np.mean(execution_times) if execution_times else 0.0,
            memory_usage=np.mean(memory_usages) if memory_usages else 0.0,
            cpu_usage=0.0,
            success_rate=(iterations - errors) / iterations,
            error_count=errors,
            iterations=iterations
        )
        
        logger.info(f"[+] Benchmark {func.__name__}: avg {avg_metrics.execution_time:.4f}s over {iterations} runs")
        
        return avg_metrics


class CodeAnalyzer:
    """Analyze code for optimization opportunities"""
    
    def __init__(self):
        self.issues: List[Dict] = []
    
    def analyze_file(self, file_path: str) -> List[Dict]:
        """Analyze Python file for inefficiencies"""
        logger.info(f"[*] Analyzing {file_path}")
        
        with open(file_path, 'r') as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            logger.error(f"[!] Syntax error in {file_path}: {str(e)}")
            return []
        
        issues = []
        
        for node in ast.walk(tree):
            # Check for inefficient loops
            if isinstance(node, ast.For):
                if self.has_nested_loop(node):
                    issues.append({
                        'type': 'nested_loop',
                        'severity': 'medium',
                        'line': node.lineno,
                        'suggestion': 'Consider list comprehension or vectorization'
                    })
            
            # Check for repeated function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                    if func_name in ['append', 'extend'] and self.in_loop(node, tree):
                        issues.append({
                            'type': 'repeated_append',
                            'severity': 'low',
                            'line': node.lineno,
                            'suggestion': 'Consider building list at once or using list comprehension'
                        })
            
            # Check for missing async/await opportunities
            if isinstance(node, ast.FunctionDef):
                if self.has_io_operations(node) and not node.name.startswith('async'):
                    issues.append({
                        'type': 'missing_async',
                        'severity': 'high',
                        'line': node.lineno,
                        'function': node.name,
                        'suggestion': 'Convert to async function for I/O operations'
                    })
        
        self.issues.extend(issues)
        logger.info(f"[+] Found {len(issues)} optimization opportunities")
        
        return issues
    
    def has_nested_loop(self, node: ast.For) -> bool:
        """Check if loop is nested"""
        for child in ast.walk(node):
            if child != node and isinstance(child, (ast.For, ast.While)):
                return True
        return False
    
    def in_loop(self, node: ast.AST, tree: ast.AST) -> bool:
        """Check if node is inside a loop"""
        # Simplified check - would need parent tracking in real implementation
        return False
    
    def has_io_operations(self, func_node: ast.FunctionDef) -> bool:
        """Check if function has I/O operations"""
        io_functions = {'open', 'read', 'write', 'requests', 'urlopen', 'connect'}
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in io_functions:
                    return True
                if isinstance(node.func, ast.Attribute) and node.func.attr in io_functions:
                    return True
        
        return False


class AICodeOptimizer:
    """Use AI models to generate code improvements"""
    
    def __init__(self, api_keys: Dict[str, str]):
        self.openai_client = AsyncOpenAI(api_key=api_keys.get('openai')) if api_keys.get('openai') else None
        self.anthropic_client = Anthropic(api_key=api_keys.get('anthropic')) if api_keys.get('anthropic') else None
    
    async def optimize_code(self, code: str, context: str = "") -> CodeImprovement:
        """Use AI to optimize code"""
        
        prompt = f"""You are an expert Python programmer. Optimize this code for better performance, memory usage, and readability.

Original code:
```python
{code}
```

Context: {context}

Provide:
1. Optimized version of the code
2. Explanation of improvements
3. Expected performance gain (as percentage)

Return ONLY valid Python code in your response, followed by a line starting with "GAIN:" showing expected improvement percentage."""
        
        try:
            if self.anthropic_client:
                logger.info("[*] Requesting code optimization from Claude...")
                
                message = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                response_text = message.content[0].text
                
            elif self.openai_client:
                logger.info("[*] Requesting code optimization from GPT-4...")
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000
                )
                
                response_text = response.choices[0].message.content
            
            else:
                logger.error("[!] No AI API configured")
                return None
            
            # Parse response
            improved_code = self.extract_code(response_text)
            expected_gain = self.extract_gain(response_text)
            
            improvement = CodeImprovement(
                module='',
                function='',
                original_code=code,
                improved_code=improved_code,
                improvement_type='ai_optimization',
                expected_gain=expected_gain,
                confidence_score=0.8
            )
            
            logger.info(f"[+] AI optimization complete - expected gain: {expected_gain}%")
            
            return improvement
            
        except Exception as e:
            logger.error(f"[!] AI optimization error: {str(e)}")
            return None
    
    def extract_code(self, response: str) -> str:
        """Extract code from AI response"""
        # Look for code between ```python and ```
        pattern = r'```python\n(.*?)```'
        match = re.search(pattern, response, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Fallback: return everything before GAIN:
        if 'GAIN:' in response:
            return response.split('GAIN:')[0].strip()
        
        return response.strip()
    
    def extract_gain(self, response: str) -> float:
        """Extract expected performance gain from response"""
        pattern = r'GAIN:\s*(\d+(?:\.\d+)?)'
        match = re.search(pattern, response)
        
        if match:
            return float(match.group(1))
        
        return 10.0  # Default estimate


class ABTester:
    """A/B test code improvements"""
    
    def __init__(self, sandbox_dir: str = "/tmp/hughes_clues_sandbox"):
        self.sandbox_dir = Path(sandbox_dir)
        self.sandbox_dir.mkdir(exist_ok=True)
        self.monitor = PerformanceMonitor()
    
    def ab_test_code(self, original_code: str, improved_code: str, 
                     test_data: Any = None, iterations: int = 50) -> TestResult:
        """A/B test two code variants"""
        
        logger.info("[*] Starting A/B test...")
        
        test_id = hashlib.md5(f"{original_code}{improved_code}{time.time()}".encode()).hexdigest()[:8]
        
        # Prepare test environment
        globals_dict = {'test_data': test_data} if test_data else {}
        
        # Test variant A (original)
        logger.info("[*] Testing variant A (original)...")
        metrics_a_list = []
        for i in range(iterations):
            metrics = self.monitor.profile_code_block(original_code, globals_dict.copy())
            metrics_a_list.append(metrics)
        
        avg_time_a = np.mean([m.execution_time for m in metrics_a_list])
        
        # Test variant B (improved)
        logger.info("[*] Testing variant B (improved)...")
        metrics_b_list = []
        for i in range(iterations):
            metrics = self.monitor.profile_code_block(improved_code, globals_dict.copy())
            metrics_b_list.append(metrics)
        
        avg_time_b = np.mean([m.execution_time for m in metrics_b_list])
        
        # Calculate improvement
        improvement_pct = ((avg_time_a - avg_time_b) / avg_time_a) * 100 if avg_time_a > 0 else 0.0
        
        # Statistical significance (simplified t-test)
        from scipy import stats
        t_stat, p_value = stats.ttest_ind(
            [m.execution_time for m in metrics_a_list],
            [m.execution_time for m in metrics_b_list]
        )
        
        significance = 1 - p_value
        
        winner = 'B' if avg_time_b < avg_time_a else 'A'
        
        result = TestResult(
            test_id=test_id,
            variant_a_metrics=metrics_a_list[0],  # Representative sample
            variant_b_metrics=metrics_b_list[0],
            improvement_percentage=improvement_pct,
            statistical_significance=significance,
            winner=winner
        )
        
        logger.info(f"[+] A/B test complete - Winner: {winner}, Improvement: {improvement_pct:.2f}%, Significance: {significance:.4f}")
        
        return result
    
    def docker_test(self, code: str) -> bool:
        """Test code in isolated Docker container"""
        logger.info("[*] Testing code in Docker sandbox...")
        
        try:
            client = docker.from_env()
            
            # Create temporary test file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                test_file = f.name
            
            # Run in container
            container = client.containers.run(
                'python:3.11-slim',
                f'python {os.path.basename(test_file)}',
                volumes={os.path.dirname(test_file): {'bind': '/app', 'mode': 'ro'}},
                working_dir='/app',
                detach=True,
                remove=True
            )
            
            # Wait for completion
            result = container.wait()
            logs = container.logs().decode('utf-8')
            
            # Clean up
            os.unlink(test_file)
            
            success = result['StatusCode'] == 0
            
            if success:
                logger.info("[+] Docker test passed")
            else:
                logger.warning(f"[!] Docker test failed: {logs}")
            
            return success
            
        except Exception as e:
            logger.error(f"[!] Docker test error: {str(e)}")
            return False


class EliteSelfImprovementEngine:
    """Master self-improvement orchestrator"""
    
    def __init__(self, api_keys: Dict[str, str], repo_path: str = "/opt/hughes_clues"):
        self.api_keys = api_keys
        self.repo_path = Path(repo_path)
        self.monitor = PerformanceMonitor()
        self.analyzer = CodeAnalyzer()
        self.optimizer = AICodeOptimizer(api_keys)
        self.tester = ABTester()
        
        # Git repo
        try:
            self.repo = git.Repo(repo_path)
            logger.info("[+] Git repository initialized")
        except:
            self.repo = None
            logger.warning("[!] Git repository not found")
        
        # Storage
        self.mongo_client = MongoClient('mongodb://localhost:27017')
        self.db = self.mongo_client['hughes_clues']
        self.improvements_collection = self.db['improvements']
        
        self.improvement_history: List[CodeImprovement] = []
    
    async def analyze_module(self, module_path: str) -> List[Dict]:
        """Analyze module for improvements"""
        logger.info(f"[*] Analyzing module: {module_path}")
        
        issues = self.analyzer.analyze_file(module_path)
        
        return issues
    
    async def optimize_function(self, function_code: str, context: str = "") -> Optional[CodeImprovement]:
        """Optimize a specific function"""
        
        improvement = await self.optimizer.optimize_code(function_code, context)
        
        if not improvement:
            return None
        
        # A/B test the improvement
        test_result = self.tester.ab_test_code(
            improvement.original_code,
            improvement.improved_code,
            iterations=50
        )
        
        improvement.tested = True
        improvement.actual_gain = test_result.improvement_percentage
        
        # Only deploy if statistically significant improvement
        if test_result.winner == 'B' and test_result.statistical_significance > 0.95:
            logger.info(f"[+] Improvement validated! Actual gain: {improvement.actual_gain:.2f}%")
            self.improvement_history.append(improvement)
            
            # Store in database
            self.improvements_collection.insert_one({
                'improvement': improvement.__dict__,
                'test_result': test_result.__dict__,
                'timestamp': datetime.now().isoformat()
            })
            
            return improvement
        else:
            logger.info(f"[!] Improvement not significant enough - not deploying")
            return None
    
    def deploy_improvement(self, improvement: CodeImprovement, file_path: str):
        """Deploy improved code to production"""
        logger.info(f"[*] Deploying improvement to {file_path}")
        
        try:
            # Read current file
            with open(file_path, 'r') as f:
                current_code = f.read()
            
            # Create backup
            backup_path = f"{file_path}.backup.{int(time.time())}"
            shutil.copy(file_path, backup_path)
            logger.info(f"[*] Backup created: {backup_path}")
            
            # Replace old code with improved code
            new_code = current_code.replace(
                improvement.original_code,
                improvement.improved_code
            )
            
            # Write improved version
            with open(file_path, 'w') as f:
                f.write(new_code)
            
            # Git commit if repo available
            if self.repo:
                self.repo.index.add([file_path])
                self.repo.index.commit(
                    f"Self-improvement: {improvement.improvement_type} - {improvement.actual_gain:.2f}% gain"
                )
                logger.info("[+] Changes committed to Git")
            
            improvement.deployed = True
            logger.info("[+] Improvement deployed successfully!")
            
        except Exception as e:
            logger.error(f"[!] Deployment error: {str(e)}")
    
    async def continuous_improvement_loop(self, module_paths: List[str], interval_hours: int = 24):
        """Continuously monitor and improve modules"""
        logger.info("[*] Starting continuous improvement loop...")
        
        while True:
            for module_path in module_paths:
                try:
                    # Analyze module
                    issues = await self.analyze_module(module_path)
                    
                    # For each high-severity issue, attempt optimization
                    for issue in issues:
                        if issue['severity'] == 'high':
                            # Extract function code around the issue
                            with open(module_path, 'r') as f:
                                lines = f.readlines()
                            
                            # Get context (simplified - would need proper AST extraction)
                            start = max(0, issue['line'] - 10)
                            end = min(len(lines), issue['line'] + 20)
                            function_code = ''.join(lines[start:end])
                            
                            # Optimize
                            improvement = await self.optimize_function(
                                function_code,
                                context=issue['suggestion']
                            )
                            
                            # Deploy if successful
                            if improvement and improvement.actual_gain > 10:
                                self.deploy_improvement(improvement, module_path)
                
                except Exception as e:
                    logger.error(f"[!] Improvement loop error: {str(e)}")
            
            # Wait before next cycle
            logger.info(f"[*] Sleeping for {interval_hours} hours...")
            await asyncio.sleep(interval_hours * 3600)
    
    def generate_improvement_report(self, output_file: str = None) -> str:
        """Generate self-improvement report"""
        
        if output_file is None:
            output_file = f"self_improvement_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_improvements': len(self.improvement_history),
            'total_performance_gain': sum(i.actual_gain for i in self.improvement_history if i.actual_gain),
            'improvements': [i.__dict__ for i in self.improvement_history],
            'metrics': [m.__dict__ for m in self.monitor.metrics]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"[+] Improvement report saved to {output_file}")
        return output_file


async def main():
    """Demo execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hughes Clues Elite Self-Improvement Engine')
    parser.add_argument('--module', help='Module to analyze')
    parser.add_argument('--function', help='Function code to optimize')
    parser.add_argument('--continuous', action='store_true', help='Run continuous improvement loop')
    parser.add_argument('--config', help='Config file with API keys')
    
    args = parser.parse_args()
    
    # Load API keys
    api_keys = {}
    if args.config:
        with open(args.config, 'r') as f:
            import yaml
            config = yaml.safe_load(f)
            api_keys = config.get('api_keys', {})
    
    engine = EliteSelfImprovementEngine(api_keys)
    
    if args.module:
        issues = await engine.analyze_module(args.module)
        print(f"\n{'='*60}")
        print(f"MODULE ANALYSIS: {args.module}")
        print(f"{'='*60}")
        for issue in issues:
            print(f"Line {issue['line']}: [{issue['severity']}] {issue['type']}")
            print(f"  Suggestion: {issue['suggestion']}")
    
    if args.function:
        improvement = await engine.optimize_function(args.function)
        if improvement:
            print(f"\n{'='*60}")
            print("OPTIMIZATION RESULT")
            print(f"{'='*60}")
            print(f"Expected gain: {improvement.expected_gain}%")
            print(f"Actual gain: {improvement.actual_gain}%")
            print(f"\nImproved code:\n{improvement.improved_code}")
    
    if args.continuous:
        modules = [
            '/opt/hughes_clues/modules/elite_recon_module.py',
            '/opt/hughes_clues/modules/elite_web_scraper.py'
        ]
        await engine.continuous_improvement_loop(modules)
    
    engine.generate_improvement_report()


if __name__ == '__main__':
    asyncio.run(main())
