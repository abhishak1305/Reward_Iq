"""
Database seed script -- generates realistic dummy data for development.
Run with: python -m backend.seed
"""

import asyncio
import random
from datetime import date, time, timedelta

from backend.core.database import AsyncSessionLocal, create_all_tables
from backend.core.security import hash_password
from backend.models.user import User, UserRole
from backend.models.employee import Employee
from backend.models.attendance import Attendance, AttendanceStatus
from backend.models.reward import Reward, RewardType
from backend.models.bonus import Bonus, BonusStatus
from backend.models.feedback import Feedback
from backend.models.notification import Notification
from backend.ai.sentiment import analyze_sentiment

DEPARTMENTS = ["Engineering", "Marketing", "Sales", "HR", "Finance", "Design"]
POSITIONS = {
    "Engineering": ["Senior Developer", "Junior Developer", "DevOps Engineer", "QA Engineer"],
    "Marketing": ["Marketing Manager", "Content Writer", "SEO Specialist"],
    "Sales": ["Sales Manager", "Account Executive", "Business Analyst"],
    "HR": ["HR Manager", "Recruiter", "People Operations"],
    "Finance": ["Finance Manager", "Accountant", "Financial Analyst"],
    "Design": ["UI/UX Designer", "Graphic Designer", "Product Designer"],
}

FEEDBACK_TEXTS = [
    "Excellent teamwork and always delivers on time. Great asset to the team!",
    "Needs to improve communication skills but technical work is solid.",
    "Outstanding performance this quarter. Consistently exceeds expectations.",
    "Sometimes late to meetings but overall good contribution.",
    "Creative problem solver. Brings innovative ideas to every project.",
    "Struggles with deadlines. Needs more mentorship and support.",
    "Very collaborative and supportive of junior team members.",
    "High-quality output consistently. One of our top performers.",
    "Shows great initiative and leadership potential.",
    "Attendance has been inconsistent. Performance could be better.",
]


async def seed():
    await create_all_tables()

    async with AsyncSessionLocal() as db:
        # Check if already seeded by looking at employee count
        from sqlalchemy import func
        from sqlalchemy import select as sa_select
        employee_count = await db.scalar(sa_select(func.count()).select_from(Employee))
        
        if employee_count > 0:
            print(f"[SKIP] {employee_count} employees already exist. Database already seeded.")
            return

        # Ensure admin exists
        existing_admin = await db.scalar(sa_select(User).where(User.email == "admin@rewardiq.com"))
        if not existing_admin:
            admin = User(  # type: ignore[call-arg]
                email="admin@rewardiq.com",
                password_hash=hash_password("Admin@123"),
                role=UserRole.admin,
            )
            db.add(admin)
            await db.flush()
            print("[OK] Admin created: admin@rewardiq.com")
        else:
            admin = existing_admin
            print("[INFO] Using existing admin.")

        # -- Employees --------------------------------------------------------
        employee_users = []
        employees = []
        for i in range(1, 21):
            dept = random.choice(DEPARTMENTS)
            position = random.choice(POSITIONS[dept])
            user = User(  # type: ignore[call-arg]
                email=f"employee{i}@rewardiq.com",
                password_hash=hash_password("Employee@123"),
                role=UserRole.employee,
            )
            db.add(user)
            await db.flush()

            emp = Employee(  # type: ignore[call-arg]
                user_id=user.id,
                full_name=f"Employee {i}",
                department=dept,
                position=position,
                hire_date=date.today() - timedelta(days=random.randint(30, 1000)),
                reward_points=random.randint(0, 1500),
                productivity_score=round(random.uniform(45, 98), 2),
            )
            db.add(emp)
            await db.flush()
            employee_users.append(user)
            employees.append(emp)

        print(f"[OK] {len(employees)} employees created")

        # -- Attendance (last 30 days) -----------------------------------------
        statuses = list(AttendanceStatus)
        weights = [0.70, 0.05, 0.10, 0.05, 0.10]  # present, absent, late, half_day, remote
        today = date.today()

        for emp in employees:
            for days_ago in range(30):
                d = today - timedelta(days=days_ago)
                if d.weekday() >= 5:
                    continue  # skip weekends
                status = random.choices(statuses, weights=weights)[0]
                check_in = time(9, random.randint(0, 45)) if status != AttendanceStatus.absent else None
                check_out = time(17, random.randint(0, 45)) if check_in else None
                db.add(Attendance(  # type: ignore[call-arg]
                    employee_id=emp.id,
                    date=d,
                    check_in=check_in,
                    check_out=check_out,
                    status=status,
                ))

        print("[OK] Attendance records created")

        # -- Rewards ----------------------------------------------------------
        reward_types = list(RewardType)
        for emp in employees:
            for _ in range(random.randint(1, 5)):
                rtype = random.choice(reward_types)
                db.add(Reward(  # type: ignore[call-arg]
                    employee_id=emp.id,
                    awarded_by=admin.id,
                    reward_type=rtype,
                    points=random.randint(10, 200),
                    title=f"{rtype.value.replace('_', ' ').title()} Award",
                    description="Awarded for outstanding performance.",
                ))

        print("[OK] Rewards created")

        # -- Bonuses ----------------------------------------------------------
        for emp in random.sample(employees, 8):
            status = random.choice(list(BonusStatus))
            db.add(Bonus(  # type: ignore[call-arg]
                employee_id=emp.id,
                amount=round(random.uniform(500, 5000), 2),
                reason="Exceptional quarterly performance",
                status=status,
                requested_by=admin.id,
                approved_by=admin.id if status in [BonusStatus.approved, BonusStatus.paid] else None,
            ))

        print("[OK] Bonuses created")

        # -- Feedback ---------------------------------------------------------
        for emp in employees:
            for _ in range(random.randint(2, 5)):
                text = random.choice(FEEDBACK_TEXTS)
                sent = analyze_sentiment(text)
                db.add(Feedback(  # type: ignore[call-arg]
                    employee_id=emp.id,
                    submitted_by=admin.id,
                    content=text,
                    category=random.choice(["performance", "teamwork", "attendance", "general"]),
                    sentiment_score=sent.score,
                    sentiment_label=sent.label,
                ))

        print("[OK] Feedback + sentiment created")

        # -- Notifications ----------------------------------------------------
        for user in employee_users[:5]:
            db.add(Notification(  # type: ignore[call-arg]
                user_id=user.id,
                title="You received a reward!",
                message="Congratulations! You've been awarded Reward Points for your performance.",
                category="reward",
            ))

        db.add(Notification(  # type: ignore[call-arg]
            user_id=admin.id,
            title="Monthly analytics ready",
            message="This month's performance analytics are now available.",
            category="info",
        ))

        await db.commit()
        print("[OK] All seed data committed successfully!")
        print("")
        print("Login credentials:")
        print("   Admin:    admin@rewardiq.com / Admin@123")
        print("   Employee: employee1@rewardiq.com / Employee@123")


if __name__ == "__main__":
    asyncio.run(seed())
