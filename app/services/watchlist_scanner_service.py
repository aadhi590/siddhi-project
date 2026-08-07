import asyncio
from typing import Dict, Any
from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import get_db_session
from app.database.models import Restaurant, WatchArea
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.watchlist_repository import WatchAreaRepository
from app.services.google_places_service import GooglePlacesService
from app.utils.helpers import generate_uuid, now_utc

logger = get_logger(__name__)

class WatchlistScannerService:
    def __init__(self):
        self.settings = get_settings()
        self.logger = logger
        self.scan_results: Dict[str, Dict[str, Any]] = {}

    async def start_watchlist_scan(self, keyword: str = "restaurant", max_results: int = 20) -> str:
        """
        Starts a background scan of all enabled watch areas.
        """
        scan_id = generate_uuid()
        
        async for session in get_db_session():
            watch_repo = WatchAreaRepository(session)
            areas = await watch_repo.get_enabled()
            break
            
        if not areas:
            self.logger.warning("No enabled watch areas found for scanning")
            return scan_id

        self.scan_results[scan_id] = {
            "status": "in_progress",
            "start_time": now_utc(),
            "keyword": keyword,
            "total_areas": len(areas),
            "areas_processed": 0,
            "restaurants_found": 0,
            "errors": []
        }

        asyncio.create_task(
            self._run_watchlist_scan(scan_id, areas, keyword, max_results)
        )
        
        return scan_id

    def get_scan_status(self, scan_id: str) -> dict | None:
        """
        Returns the current status of a running scan.
        """
        return self.scan_results.get(scan_id)

    async def _run_watchlist_scan(self, scan_id: str, areas: list, keyword: str, max_results: int):
        """
        Internal task to process watch area scans.
        """
        self.logger.info(f"Starting watchlist scan {scan_id} for {len(areas)} areas")
        
        places_service = GooglePlacesService(self.settings)
        total_found = 0
        
        for area in areas:
            try:
                self.logger.info(f"Scanning area {area.name} for keyword {keyword}")
                places = await places_service.search_nearby(
                    latitude=area.latitude,
                    longitude=area.longitude,
                    radius=area.radius,
                    keyword=keyword,
                    max_results=max_results
                )
                
                if not places:
                    continue
                    
                area_found = 0
                async for session in get_db_session():
                    rest_repo = RestaurantRepository(session)
                    watch_repo = WatchAreaRepository(session)
                    
                    for place in places:
                        place_id = place.get("place_id")
                        if not place_id:
                            continue
                            
                        existing = await rest_repo.get_by_place_id(place_id)
                        if not existing:
                            details = await places_service.get_place_details(place_id)
                            if details:
                                details["scan_zone"] = area.name
                                await rest_repo.create(details)
                                area_found += 1
                                
                    if area_found > 0:
                        await watch_repo.update_scan_stats(area.id, area_found)
                    break
                    
                total_found += area_found
                self.logger.info(f"Area {area.name} scan complete: found {area_found} new restaurants")
                
            except Exception as e:
                self.logger.error(f"Error scanning area {area.name}: {str(e)}")
                if scan_id in self.scan_results:
                    self.scan_results[scan_id]["errors"].append(f"Area {area.name}: {str(e)}")
                    
            if scan_id in self.scan_results:
                self.scan_results[scan_id]["areas_processed"] += 1
                self.scan_results[scan_id]["restaurants_found"] = total_found
                
        if scan_id in self.scan_results:
            self.scan_results[scan_id]["status"] = "completed"
            self.scan_results[scan_id]["end_time"] = now_utc()
            
        self.logger.info(f"Completed watchlist scan {scan_id}: total {total_found} found")

watchlist_scanner = WatchlistScannerService()
