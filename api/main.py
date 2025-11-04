"""
Hughes Clues FastAPI Application
REST API for Intelligence Gathering
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import logging
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from master_orchestrator import MasterOrchestrator, OperationType
except ImportError as e:
    print(f"[!] Warning: Could not import MasterOrchestrator: {str(e)}")
    MasterOrchestrator = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Hughes Clues Intelligence API",
    version="1.0.0",
    description="OSINT Intelligence Gathering Framework API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = None


# Pydantic models
class ReconRequest(BaseModel):
    """Reconnaissance request model"""
    target: str
    workers: Optional[int] = 4
    timeout: Optional[int] = 300


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


@app.on_event("startup")
async def startup():
    """Initialize orchestrator on startup"""
    global orchestrator
    try:
        logger.info("[*] Initializing orchestrator...")
        if MasterOrchestrator is None:
            logger.warning("[!] MasterOrchestrator not available")
            return

        orchestrator = MasterOrchestrator()
        orchestrator.start_workers()
        logger.info("[+] Orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"[!] Failed to initialize orchestrator: {str(e)}")
        # Don't raise - allow API to start without orchestrator


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global orchestrator
    if orchestrator:
        logger.info("[*] Shutting down orchestrator...")
        try:
            orchestrator.shutdown()
            logger.info("[+] Orchestrator shutdown complete")
        except Exception as e:
            logger.error(f"[!] Error during shutdown: {str(e)}")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hughes-clues-api",
        "version": "1.0.0"
    }


@app.get("/status")
async def status():
    """Get orchestrator status"""
    if orchestrator is None:
        return {"status": "error", "message": "Orchestrator not initialized"}

    try:
        stats = orchestrator.get_system_stats()
        return {
            "status": "operational",
            "workers_active": stats.get('workers_active', 0),
            "operations_queued": stats.get('operations_queued', 0),
            "operations_completed": stats.get('operations_completed', 0),
            "operations_failed": stats.get('operations_failed', 0),
            "success_rate": stats.get('success_rate', 0),
        }
    except Exception as e:
        logger.error(f"[!] Error getting status: {str(e)}")
        return {"status": "error", "message": str(e)}


@app.post("/intelligence/reconnaissance")
async def run_reconnaissance(request: ReconRequest):
    """
    Run reconnaissance on target

    Args:
        request: ReconRequest with target domain/IP

    Returns:
        Intelligence report with findings
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    if not request.target:
        raise HTTPException(status_code=400, detail="Target cannot be empty")

    try:
        logger.info(f"[*] Starting reconnaissance on {request.target}")

        report = await orchestrator.run_full_intelligence_pipeline(
            request.target,
            [OperationType.RECONNAISSANCE]
        )

        logger.info(f"[+] Reconnaissance complete for {request.target}")

        # Convert report to dict if needed
        report_dict = report.__dict__ if hasattr(report, '__dict__') else report

        return {
            "status": "success",
            "target": request.target,
            "risk_score": report_dict.get('risk_score', 0) if isinstance(report_dict, dict) else getattr(report, 'risk_score', 0),
            "confidence": report_dict.get('confidence', 0) if isinstance(report_dict, dict) else getattr(report, 'confidence', 0),
            "report": str(report_dict)[:500] + "..." if len(str(report_dict)) > 500 else str(report_dict),
        }
    except Exception as e:
        logger.error(f"[!] Reconnaissance failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Reconnaissance failed: {str(e)}")


@app.post("/intelligence/full-pipeline")
async def run_full_pipeline(request: ReconRequest):
    """
    Run full intelligence pipeline on target

    Args:
        request: ReconRequest with target

    Returns:
        Complete intelligence report
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    if not request.target:
        raise HTTPException(status_code=400, detail="Target cannot be empty")

    try:
        logger.info(f"[*] Starting full intelligence pipeline for {request.target}")

        # Run all operation types
        report = await orchestrator.run_full_intelligence_pipeline(request.target)

        logger.info(f"[+] Full pipeline complete for {request.target}")

        report_dict = report.__dict__ if hasattr(report, '__dict__') else report

        return {
            "status": "success",
            "target": request.target,
            "risk_score": report_dict.get('risk_score', 0) if isinstance(report_dict, dict) else getattr(report, 'risk_score', 0),
            "confidence": report_dict.get('confidence', 0) if isinstance(report_dict, dict) else getattr(report, 'confidence', 0),
        }
    except Exception as e:
        logger.error(f"[!] Pipeline failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@app.get("/targets")
async def list_targets():
    """List all analyzed targets"""
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    try:
        # This would query MongoDB for all reports
        # For now, return empty list as placeholder
        return {"targets": [], "count": 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Hughes Clues Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "reconnaissance": "/intelligence/reconnaissance (POST)",
            "full_pipeline": "/intelligence/full-pipeline (POST)",
            "targets": "/targets (GET)",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
