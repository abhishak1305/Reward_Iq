import httpx
import json
from typing import List, Dict
from backend.core.config import settings

class HRFeedbackCoach:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENROUTER_API_KEY
        self.model = model or settings.OPENROUTER_MODEL
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        # OpenRouter expects a site name/URL in headers
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://rewardiq-frontend.onrender.com",
            "X-Title": "RewardIQ HRM",
            "Content-Type": "application/json"
        }
        self.history = []

    async def _call_openrouter(self, messages: List[Dict]) -> str:
        if not self.api_key:
            return "I am operating in simulated mode without an API key. Please add your OpenRouter API key to the .env file."

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                payload = {
                    "model": self.model,
                    "messages": messages
                }
                response = await client.post(self.base_url, headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data['choices'][0]['message']['content']
        except Exception as e:
            import logging
            logging.error(f"OpenRouter error: {e}")
            return f"**Error:** I encountered an issue connecting to the AI service. Details: {str(e)}"

    async def analyze_feedback(self, employee_name: str, feedback_list: List[Dict]) -> str:
        """
        Uses OpenRouter to process an array of peer feedback and generate an actionable insight.
        """
        if not feedback_list:
            return "You don't have any recent feedback. Keep up the good work and encourage peers to use the 360-degree tool!"

        feedback_text = "\n".join([f"- [{f.get('sentiment')}] {f.get('content', f.get('comment'))}" for f in feedback_list])
        
        system_msg = (
            "You are the RewardIQ Project AI. Your scope is strictly limited to RewardIQ and this HRM project. "
            "Analyze the following peer feedback for {employee_name} and provide a summary of strengths and actionable suggestions. "
            "\n\nIf you want to perform an action (like awarding points), you can output a command in this format: [ACTION: AWARD_POINTS|{employee_name}|{points}|{reason}]\n"
            "If the request is unrelated to RewardIQ, reply with: \"Sorry, I only have knowledge about RewardIQ and this project.\""
        )
        user_msg = f"Analyze the following peer feedback for {employee_name}:\n{feedback_text}"

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ]

        return await self._call_openrouter(messages)

    async def chat(self, user_input: str, context: str = "") -> str:
        """
        Handles conversational memory and follow-up questions.
        Includes optional real-time context (e.g. current leaderboard).
        """
        if not self.history:
            system_msg = (
                "You are the RewardIQ Project AI. Your scope is STRICTLY limited to RewardIQ and this HRM project. "
                "You answer questions about the HRM system, employee rewards, and project-related HR tasks. "
                "\n\nCOMMANDS:\n"
                "You can trigger actions by including the following tags in your response:\n"
                "- Award Points: [ACTION: AWARD_POINTS|Employee Name|Points|Reason]\n"
                "- Get Details: [ACTION: GET_STATS|Employee Name]\n\n"
                "Example: 'I have awarded 50 points to Employee 1. [ACTION: AWARD_POINTS|Employee 1|50|Consistent performance]'\n\n"
                "If the user asks anything outside the scope of RewardIQ or this project, you MUST reply with: "
                "\"Sorry, I only have knowledge about RewardIQ and this project.\"\n\n"
            )
            if context:
                system_msg += f"Current RewardIQ Context:\n{context}\n\n"
            
            self.history.append({
                "role": "system", 
                "content": system_msg
            })
        
        self.history.append({"role": "user", "content": user_input})
        
        # Keep history manageable (last 10 interactions)
        if len(self.history) > 21:
            self.history = [self.history[0]] + self.history[-20:]

        response = await self._call_openrouter(self.history)
        self.history.append({"role": "assistant", "content": response})
        return response
