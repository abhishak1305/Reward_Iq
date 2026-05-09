import asyncio
from sqlalchemy import select, func
from backend.core.database import AsyncSessionLocal
from backend.models.employee import Employee
from backend.models.feedback import Feedback

async def check():
    async with AsyncSessionLocal() as db:
        emps = await db.scalar(select(func.count(Employee.id)))
        fb = await db.scalar(select(func.count(Feedback.id)))
        print(f"DEBUG_EMPS: {emps}")
        print(f"DEBUG_FB: {fb}")

if __name__ == "__main__":
    asyncio.run(check())
