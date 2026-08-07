from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.intelligence import ChennaiScanRequest, ChennaiScanResponse
from app.services.chennai_scanner_service import chennai_scanner

router = APIRouter(prefix="/scan", tags=["Chennai Scanner"])

@router.post("/chennai", response_model=ChennaiScanResponse)
async def start_chennai_scan(request: ChennaiScanRequest) -> ChennaiScanResponse:
    """
    Start a Chennai-specific area scan.
    """
    try:
        return await chennai_scanner.start_chennai_scan(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chennai/{scan_id}", response_model=dict[str, Any])
async def get_scan_status(scan_id: str) -> dict[str, Any]:
    """
    Get status of a running scan.
    """
    try:
        return await chennai_scanner.get_status(scan_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
