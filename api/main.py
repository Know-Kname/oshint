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


@app.post("/people/search-by-name")
async def search_person_by_name(full_name: str, city: str = None, state: str = None):
    """
    Search for person by name and optional location

    Args:
        full_name: Full name of person
        city: Optional city
        state: Optional state

    Returns:
        Person profile with collected information
    """
    try:
        # Import here to avoid circular dependencies
        from elite_people_intel import PeopleIntelligence

        intel = PeopleIntelligence()
        profile = await intel.search_by_name(full_name, city, state)
        await intel.close_session()

        return {
            "status": "success",
            "profile": {
                "full_name": profile.full_name,
                "age": profile.age,
                "location": f"{profile.current_city or ''}, {profile.current_state or ''}".strip(', '),
                "phone_numbers": profile.phone_numbers,
                "email_addresses": profile.email_addresses,
                "social_media": profile.social_media,
                "confidence_score": profile.confidence_score,
                "sources": profile.sources
            }
        }
    except Exception as e:
        logger.error(f"[!] People search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/people/search-by-phone")
async def search_person_by_phone(phone_number: str):
    """
    Search for person by phone number

    Args:
        phone_number: Phone number in any format

    Returns:
        Person profile
    """
    try:
        from elite_people_intel import PeopleIntelligence

        intel = PeopleIntelligence()
        profile = await intel.search_by_phone(phone_number)
        await intel.close_session()

        return {
            "status": "success",
            "profile": {
                "full_name": profile.full_name,
                "phone_numbers": profile.phone_numbers,
                "email_addresses": profile.email_addresses,
                "location": f"{profile.current_city or ''}, {profile.current_state or ''}".strip(', '),
                "confidence_score": profile.confidence_score,
                "sources": profile.sources
            }
        }
    except Exception as e:
        logger.error(f"[!] Phone search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/people/search-by-email")
async def search_person_by_email(email: str):
    """
    Search for person by email address

    Args:
        email: Email address

    Returns:
        Person profile
    """
    try:
        from elite_people_intel import PeopleIntelligence

        intel = PeopleIntelligence()
        profile = await intel.search_by_email(email)
        await intel.close_session()

        return {
            "status": "success",
            "profile": {
                "full_name": profile.full_name,
                "email_addresses": profile.email_addresses,
                "social_media": profile.social_media,
                "data_breaches": profile.data_breaches,
                "confidence_score": profile.confidence_score,
                "sources": profile.sources
            }
        }
    except Exception as e:
        logger.error(f"[!] Email search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/people/search-by-username")
async def search_person_by_username(username: str):
    """
    Search for person by username across platforms

    Args:
        username: Username to search

    Returns:
        Person profile with found accounts
    """
    try:
        from elite_people_intel import PeopleIntelligence

        intel = PeopleIntelligence()
        profile = await intel.search_by_username(username)
        await intel.close_session()

        return {
            "status": "success",
            "profile": {
                "username": username,
                "social_media": profile.social_media,
                "usernames": list(profile.usernames),
                "sources": profile.sources
            }
        }
    except Exception as e:
        logger.error(f"[!] Username search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/people/search-comprehensive")
async def search_person_comprehensive(
    name: str = None,
    phone: str = None,
    email: str = None,
    username: str = None,
    city: str = None,
    state: str = None
):
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
        Aggregated person profile
    """
    try:
        from elite_people_intel import PeopleIntelligence

        intel = PeopleIntelligence()
        profile = await intel.search_comprehensive(
            name=name,
            phone=phone,
            email=email,
            username=username,
            city=city,
            state=state
        )
        await intel.close_session()

        # Generate report
        report_text = intel.generate_report(profile, format='text')

        return {
            "status": "success",
            "profile": {
                "full_name": profile.full_name,
                "age": profile.age,
                "date_of_birth": profile.date_of_birth,
                "current_location": f"{profile.current_city or ''}, {profile.current_state or ''}".strip(', '),
                "phone_numbers": profile.phone_numbers,
                "email_addresses": profile.email_addresses,
                "social_media": profile.social_media,
                "employers": profile.employers,
                "education": profile.education,
                "data_breaches": profile.data_breaches,
                "confidence_score": profile.confidence_score,
                "sources": profile.sources
            },
            "report": report_text
        }
    except Exception as e:
        logger.error(f"[!] Comprehensive search failed: {str(e)}")
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
            "people_search_by_name": "/people/search-by-name (POST)",
            "people_search_by_phone": "/people/search-by-phone (POST)",
            "people_search_by_email": "/people/search-by-email (POST)",
            "people_search_by_username": "/people/search-by-username (POST)",
            "people_search_comprehensive": "/people/search-comprehensive (POST)",
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
