from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from backend.ai.gemini_coach import HRFeedbackCoach
from backend.core.security import get_current_user_id
from backend.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ai/chat", tags=["AI Chatbot"])

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=1000)
    action: str = "chat"
    user: str = "Employee User"
    feedback: Optional[List[Dict[str, Any]]] = None

# Store memory per user
coaches: Dict[str, HRFeedbackCoach] = {}

from backend.models.reward import Reward, RewardType

async def handle_actions(response: str, db: AsyncSession, admin_id: int):
    """Parses [ACTION: ...] tags and executes them."""
    import re
    action_match = re.search(r"\[ACTION: (.*?)\]", response)
    if not action_match:
        return response
    
    action_str = action_match.group(1)
    parts = action_str.split("|")
    action_type = parts[0]
    
    if action_type == "AWARD_POINTS":
        # Format: AWARD_POINTS|Name|Points|Reason
        if len(parts) >= 4:
            name, points, reason = parts[1], parts[2], parts[3]
            # Find employee
            emp = await db.scalar(select(Employee).where(Employee.full_name.ilike(f"%{name}%")))
            if emp:
                try:
                    pts = int(points)
                    emp.reward_points += pts
                    # Log reward
                    db.add(Reward(  # type: ignore[call-arg]
                        employee_id=emp.id,
                        awarded_by=admin_id,
                        reward_type=RewardType.performance_bonus,
                        points=pts,
                        title="AI Recommended Reward",
                        description=reason
                    ))
                    await db.commit()
                    return response.replace(f"[ACTION: {action_str}]", f"✅ (Success: Awarded {pts} pts to {emp.full_name})")
                except Exception as e:
                    return response.replace(f"[ACTION: {action_str}]", f"❌ (Error: {str(e)})")
    
    return response

@router.post("")
async def chat_with_ai(request: ChatRequest, user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    try:
        uid = str(user_id)
        if uid not in coaches:
            coaches[uid] = HRFeedbackCoach()
        coach_instance = coaches[uid]

        if request.action == "analyze":
            raw_response = coach_instance.analyze_feedback(request.user, request.feedback or [])
            final_response = await handle_actions(raw_response, db, user_id)
            return {"response": final_response}
        else:
            # Gather context
            top_3 = (await db.execute(
                select(Employee.full_name, Employee.reward_points)
                .order_by(Employee.reward_points.desc())
                .limit(3)
            )).all()
            total_count = await db.scalar(select(func.count(Employee.id)))
            
            context = f"- Total Employees in RewardIQ: {total_count}\n"
            context += "- Top 3 on Leaderboard:\n"
            for i, emp in enumerate(top_3):
                context += f"  {i+1}. {emp.full_name} ({emp.reward_points} pts)\n"

            raw_response = coach_instance.chat(request.message, context=context)
            final_response = await handle_actions(raw_response, db, user_id)
            return {"response": final_response}
    except Exception as e:
        import logging
        logging.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


