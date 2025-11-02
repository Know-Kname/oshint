#!/usr/bin/env python3
"""
Hughes Clues Test Script
Tests core functionality and new enhancements
"""

import asyncio
import logging
from master_orchestrator import MasterOrchestrator, OperationType
from elite_performance_optimizer import PerformanceOptimizer
from elite_analysis_engine import AdvancedAnalyzer, AnalysisConfig
import json
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_intelligence_pipeline(target: str = "example.com"):
    """Test the full intelligence pipeline"""
    
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return False
    
    try:
        # Initialize components
        orchestrator = MasterOrchestrator(config_path)
        optimizer = PerformanceOptimizer()
        analyzer = AdvancedAnalyzer()
        
        # Start services
        orchestrator.start_workers()
        await optimizer.init_redis("redis://localhost")
        
        # Run intelligence pipeline
        operations = [
            OperationType.RECONNAISSANCE,
            OperationType.WEB_SCRAPING,
            OperationType.CREDENTIAL_HARVEST,
            OperationType.GEOLOCATION
        ]
        
        logger.info(f"Starting intelligence pipeline for {target}")
        report = await orchestrator.run_full_intelligence_pipeline(target, operations)
        
        # Analyze results
        if report.reconnaissance:
            patterns = analyzer.analyze_patterns([report.reconnaissance])
            anomalies, scores = analyzer.detect_anomalies([report.reconnaissance])
            risk_assessment = analyzer.calculate_advanced_risk_score(report.reconnaissance)
            
            # Export analysis
            analysis_file = f"analysis_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            analysis_data = {
                'patterns': patterns,
                'anomalies': {
                    'indices': anomalies,
                    'scores': scores
                },
                'risk_assessment': risk_assessment
            }
            
            with open(analysis_file, 'w') as f:
                json.dump(analysis_data, f, indent=2)
            
            logger.info(f"Analysis exported to {analysis_file}")
        
        # Get performance metrics
        metrics = optimizer.get_metrics()
        logger.info("Performance Metrics:")
        logger.info(f"Cache Hit Ratio: {metrics['cache_hit_ratio']:.2%}")
        logger.info(f"Average Execution Time: {metrics['average_execution_time']:.2f}s")
        
        # Cleanup
        await optimizer.cleanup()
        orchestrator.shutdown()
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

def main():
    """Main test execution"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║   HUGHES CLUES - SYSTEM TEST                             ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run tests
    target = "example.com"  # Change this to your target
    success = asyncio.run(test_intelligence_pipeline(target))
    
    if success:
        print("\n✅ System test completed successfully!")
    else:
        print("\n❌ System test failed!")

if __name__ == "__main__":
    main()