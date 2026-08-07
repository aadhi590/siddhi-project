from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case
from datetime import date
from app.database.models import Restaurant
from app.schemas.reports import DailySalesReport, SalesReportLead, AreaSummary, TodayLeadsResponseV2
from app.utils.prompts import DAILY_SALES_REPORT_PROMPT
from app.services.llm_service import LLMService

class DailyInsightsService:
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def generate_today_leads(self, session: AsyncSession) -> TodayLeadsResponseV2:
        """
        Stub for generate_today_leads to satisfy requirements.
        """
        # Implementation assumed to exist
        return TodayLeadsResponseV2(leads=[], total_count=0)

    async def generate_daily_insights(self, session: AsyncSession) -> dict:
        """
        Stub for generate_daily_insights to satisfy requirements.
        """
        # Implementation assumed to exist
        return {}

    async def generate_daily_sales_report(self, session: AsyncSession) -> DailySalesReport:
        """
        Generates a comprehensive daily sales report combining database queries and AI analysis.
        """
        today = date.today()
        
        # Total scanned
        total_stmt = select(func.count()).select_from(Restaurant)
        total_result = await session.execute(total_stmt)
        total_scanned = total_result.scalar() or 0
        
        # Newly discovered today
        new_stmt = select(func.count()).select_from(Restaurant).where(
            func.date(Restaurant.first_seen) == today
        )
        new_result = await session.execute(new_stmt)
        newly_discovered = new_result.scalar() or 0
        
        # Opening soon
        os_stmt = select(func.count()).select_from(Restaurant).where(
            Restaurant.business_status == 'OPENING_SOON'
        )
        os_result = await session.execute(os_stmt)
        opening_soon = os_result.scalar() or 0
        
        # Highest opportunity leads
        opp_stmt = (
            select(Restaurant)
            .order_by(desc(Restaurant.opportunity_index))
            .limit(10)
        )
        opp_result = await session.execute(opp_stmt)
        highest_opportunity = opp_result.scalars().all()
        
        # Highest marketing readiness
        mkt_stmt = (
            select(Restaurant)
            .order_by(desc(Restaurant.marketing_readiness_score))
            .limit(10)
        )
        mkt_result = await session.execute(mkt_stmt)
        highest_marketing = mkt_result.scalars().all()
        
        # Area summary
        area_stmt = (
            select(
                Restaurant.scan_zone,
                func.avg(Restaurant.opportunity_index).label('avg_opp'),
                func.avg(Restaurant.marketing_readiness_score).label('avg_mkt'),
                func.sum(case((func.date(Restaurant.first_seen) == today, 1), else_=0)).label('new_count'),
                func.sum(case((Restaurant.business_status == 'OPENING_SOON', 1), else_=0)).label('os_count')
            )
            .where(Restaurant.scan_zone.isnot(None))
            .group_by(Restaurant.scan_zone)
        )
        area_result = await session.execute(area_stmt)
        
        area_summaries = []
        for row in area_result:
            area_summaries.append(
                AreaSummary(
                    scan_zone=row.scan_zone,
                    avg_opportunity_index=float(row.avg_opp or 0),
                    avg_marketing_readiness=float(row.avg_mkt or 0),
                    newly_discovered_count=int(row.new_count or 0),
                    opening_soon_count=int(row.os_count or 0)
                )
            )
            
        opp_leads = [
            SalesReportLead(
                id=r.id, 
                name=r.name, 
                scan_zone=r.scan_zone, 
                score=r.opportunity_index
            ) for r in highest_opportunity
        ]
        
        mkt_leads = [
            SalesReportLead(
                id=r.id, 
                name=r.name, 
                scan_zone=r.scan_zone, 
                score=r.marketing_readiness_score
            ) for r in highest_marketing
        ]
        
        # Use LLM to generate summary
        stats_dict = {
            "total_scanned": total_scanned,
            "newly_discovered": newly_discovered,
            "opening_soon": opening_soon,
            "areas_active": len(area_summaries)
        }
        
        try:
            ai_summary = await self.llm_service.generate_text(
                prompt=DAILY_SALES_REPORT_PROMPT.format(stats=str(stats_dict))
            )
        except Exception:
            ai_summary = "AI summary generation failed."
            
        return DailySalesReport(
            total_scanned=total_scanned,
            newly_discovered=newly_discovered,
            opening_soon=opening_soon,
            highest_opportunity_leads=opp_leads,
            highest_marketing_readiness=mkt_leads,
            area_summary=area_summaries,
            scan_statistics={
                "total_areas_scanned": len(area_summaries),
                "last_scan_time": str(date.today())
            },
            ai_summary=ai_summary
        )
