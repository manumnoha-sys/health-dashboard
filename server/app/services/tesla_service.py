from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models.tesla_snapshot import TeslaSnapshot
from app.schemas.tesla import TeslaIngestRequest


async def ingest_tesla(db: AsyncSession, payload: TeslaIngestRequest) -> dict:
    rows = [s.model_dump() for s in payload.snapshots]
    stmt = pg_insert(TeslaSnapshot).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=["recorded_at"])
    result = await db.execute(stmt)
    await db.commit()
    accepted = result.rowcount
    return {"accepted": accepted, "duplicate_skipped": len(rows) - accepted}
