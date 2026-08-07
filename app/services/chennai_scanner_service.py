import asyncio
from typing import Optional

from app.core.config import get_settings
from app.core.logging import get_logger
from app.database.session import get_db_session
from app.repositories.restaurant_repository import RestaurantRepository
from app.services.google_places_service import GooglePlacesService
from app.utils.chennai_zones import CHENNAI_ZONES
from app.utils.helpers import generate_uuid

logger = get_logger(__name__)

class ChennaiScannerService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.logger = logger
        self.scan_results: dict[str, dict] = {}

    async def start_chennai_scan(self, zones: Optional[list[str]] = None, keyword: str = "restaurant", max_results_per_zone: int = 20) -> str:
        """Starts a background scan for restaurants in Chennai zones."""
        scan_id = generate_uuid()
        
        target_zones = CHENNAI_ZONES
        if zones:
            target_zones = [z for z in CHENNAI_ZONES if z["name"] in zones]
            
        self.scan_results[scan_id] = {
            "status": "in_progress",
            "zones_total": len(target_zones),
            "zones_completed": 0,
            "results_found": 0,
            "completed": False
        }
        
        asyncio.create_task(self._run_chennai_scan(scan_id, target_zones, keyword, max_results_per_zone))
        return scan_id

    def get_scan_status(self, scan_id: str) -> Optional[dict]:
        """Returns the current status of a scan."""
        return self.scan_results.get(scan_id)

    async def _run_chennai_scan(self, scan_id: str, zones: list[dict], keyword: str, max_results: int) -> None:
        """Executes the scan across multiple zones."""
        try:
            places_service = GooglePlacesService()
            all_found_places = []
            
            for zone in zones:
                try:
                    self.logger.info(f"Scanning zone {zone['name']} for scan_id {scan_id}")
                    results = await places_service.search_nearby(
                        lat=zone["latitude"],
                        lng=zone["longitude"],
                        radius=zone["radius"],
                        keyword=keyword
                    )
                    
                    limited_results = results[:max_results]
                    
                    async for db in get_db_session():
                        repo = RestaurantRepository(db)
                        for place in limited_results:
                            place_id = place.get("place_id")
                            if not place_id:
                                continue
                                
                            existing = await repo.get_by_place_id(place_id)
                            if not existing:
                                details = await places_service.get_place_details(place_id)
                                details["scan_zone"] = zone["name"]
                                new_restaurant = await repo.create(details)
                                all_found_places.append(new_restaurant.id)
                                self.scan_results[scan_id]["results_found"] += 1
                                
                                # Launch enrichment pipeline in background
                                asyncio.create_task(self._process_and_enrich(new_restaurant.id))
                                
                except Exception as e:
                    self.logger.error(f"Error scanning zone {zone['name']}: {str(e)}")
                    
                self.scan_results[scan_id]["zones_completed"] += 1

            self.scan_results[scan_id]["status"] = "completed"
            self.scan_results[scan_id]["completed"] = True
            self.logger.info(f"Scan {scan_id} completed successfully")
            
        except Exception as e:
            self.logger.error(f"Scan {scan_id} failed: {str(e)}")
            if scan_id in self.scan_results:
                self.scan_results[scan_id]["status"] = "failed"
                self.scan_results[scan_id]["error"] = str(e)

    async def _process_and_enrich(self, restaurant_id: int) -> None:
        """Runs the enrichment pipeline for a newly discovered restaurant."""
        self.logger.info(f"Started enrichment for restaurant {restaurant_id}")
        # Note: Implement integration with PhotoService, VisionService, Intelligence Services here.

chennai_scanner = ChennaiScannerService()
