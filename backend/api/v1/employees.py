"""Employee management API router."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.security import get_current_user_id, require_admin
from backend.models.employee import Employee
from backend.models.user import User
from backend.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeOut,
    EmployeeWithEmail, EmployeeRankItem,
)

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("/", response_model=list[EmployeeWithEmail])
async def list_employees(
    department: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    q = select(Employee, User.email, User.role).join(User, Employee.user_id == User.id)
    if department:
        q = q.where(Employee.department == department)
    q = q.offset(skip).limit(limit)
    rows = await db.execute(q)

    result = []
    for emp, email, role in rows:
        emp_dict = EmployeeOut.model_validate(emp).model_dump()
        emp_dict["email"] = email
        emp_dict["role"] = role.value
        result.append(EmployeeWithEmail(**emp_dict))
    return result


@router.get("/ranking", response_model=list[EmployeeRankItem])
async def get_rankings(
    limit: int = Query(default=10, le=50),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(Employee)
        .order_by(Employee.reward_points.desc(), Employee.productivity_score.desc())
        .limit(limit)
    )
    employees = (await db.execute(q)).scalars().all()
    return [
        EmployeeRankItem(
            rank=i + 1,
            employee_id=emp.id,
            full_name=emp.full_name,
            department=emp.department,
            reward_points=emp.reward_points,
            productivity_score=emp.productivity_score,
        )
        for i, emp in enumerate(employees)
    ]


@router.get("/me", response_model=EmployeeOut)
async def get_my_profile(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.scalar(select(Employee).where(Employee.user_id == user_id))
    if not emp:
        raise HTTPException(status_code=404, detail="Employee profile not found.")
    return EmployeeOut.model_validate(emp)


@router.get("/{employee_id}", response_model=EmployeeOut)
async def get_employee(
    employee_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")
    return EmployeeOut.model_validate(emp)


@router.post("/", response_model=EmployeeOut, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    emp = Employee(**payload.model_dump())  # type: ignore[call-arg]
    db.add(emp)
    await db.commit()
    await db.refresh(emp)
    return EmployeeOut.model_validate(emp)


@router.patch("/{employee_id}", response_model=EmployeeOut)
async def update_employee(
    employee_id: int,
    payload: EmployeeUpdate,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")
    for field, val in payload.model_dump(exclude_none=True).items():
        setattr(emp, field, val)
    await db.commit()
    await db.refresh(emp)
    return EmployeeOut.model_validate(emp)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int,
    _=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found.")

    # 9.4 Fix: Deactivate the associated User so they can't still authenticate
    user = await db.get(User, emp.user_id)
    if user:
        user.is_active = False

    await db.delete(emp)
    await db.commit()
