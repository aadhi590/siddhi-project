from fastapi import APIRouter, HTTPException, Depends
from app.schemas.scan import ScanRequest, ScanLocationRequest, ScanResponse, ScanStatusResponse, WatchlistScanRequest, WatchlistScanResponse
from app.background.scanner import scanner
from app.services.google_places_service import GooglePlacesService
from app.core.dependencies import get_places_service
from app.services.watchlist_scanner_service import watchlist_scanner

router = APIRouter(prefix="/scan", tags=["Scan"])

@router.post("/", response_model=ScanResponse)
async def trigger_scan(request: ScanRequest, places_service: GooglePlacesService = Depends(get_places_service)):
    lat, lng = await places_service.geocode_location(request.location)
    if lat is None or lng is None:
        raise HTTPException(status_code=400, detail="Could not geocode location")
        
    scan_id = await scanner.start_scan(
        latitude=lat,
        longitude=lng,
        radius=request.radius,
        keyword=request.keyword,
        max_results=request.max_results
    )
    return ScanResponse(scan_id=scan_id, message="Scan started successfully")

@router.post("/location", response_model=ScanResponse)
async def trigger_scan_by_location(request: ScanLocationRequest):
    scan_id = await scanner.start_scan(
        latitude=request.latitude,
        longitude=request.longitude,
        radius=request.radius,
        keyword=request.keyword,
        max_results=request.max_results
    )
    return ScanResponse(scan_id=scan_id, message="Scan started successfully")

@router.get("/{scan_id}", response_model=ScanStatusResponse)
async def get_scan_status(scan_id: str):
    status = scanner.get_scan_status(scan_id)
    if not status:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanStatusResponse(scan_id=scan_id, **status)

@router.post("/watchlist", response_model=WatchlistScanResponse)
async def start_watchlist_scan(request: WatchlistScanRequest):
    scan_id = await watchlist_scanner.start_scan(
        area_ids=request.area_ids,
        keyword=request.keyword,
        max_results_per_area=request.max_results_per_area
    )
    return WatchlistScanResponse(scan_id=scan_id, message="Watchlist scan started successfully")

@router.get("/watchlist/{scan_id}", response_model=ScanStatusResponse)
async def get_watchlist_scan_status(scan_id: str):
    status = watchlist_scanner.get_scan_status(scan_id)
    if not status:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanStatusResponse(scan_id=scan_id, **status)
