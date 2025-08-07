import json
from channels.generic.websocket import AsyncWebsocketConsumer
import httpx

class LegalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.chat_history = []

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data["message"]

        self.chat_history.append({"role": "user", "content": user_message})

        # تماس با Claude API
        response_text = await self.ask_claude(self.chat_history)

        self.chat_history.append({"role": "assistant", "content": response_text})

        await self.send(text_data=json.dumps({
            "message": response_text
        }))

    async def ask_claude(self, history):
        headers = {
            "x-api-key": "YOUR_CLAUDE_API_KEY",
            "Content-Type": "application/json"
        }

        body = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1024,
            "temperature": 0.7,
            "system": "You are a helpful, professional Persian legal advisor. Only answer legal questions.",
            "messages": history
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=body
                )
                result = response.json()
                return result["content"][0]["text"]
            except Exception as e:
                return "خطا در ارتباط با سرور مشاور حقوقی. لطفاً بعداً تلاش کنید."
