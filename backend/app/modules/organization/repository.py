from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organization import OrganizationProfile


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_profile(self) -> OrganizationProfile | None:
        result = await self.session.execute(
            select(OrganizationProfile).order_by(OrganizationProfile.created_at.asc()).limit(1)
        )
        return result.scalar_one_or_none()

    async def add_profile(self, profile: OrganizationProfile) -> OrganizationProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile
