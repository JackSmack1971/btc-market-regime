import aiohttp
from .notifier import Notifier, AlertLevel
from ..utils import logger

class TelegramNotifier(Notifier):
    """Asynchronous Telegram notification channel."""

    def __init__(self, bot_token: str, chat_id: str):
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self.chat_id = chat_id

    async def send(self, message: str, level: AlertLevel = AlertLevel.INFO) -> bool:
        """POSTs a message to the Telegram Bot API."""
        prefix = "🚨" if level in [AlertLevel.ALERT, AlertLevel.CRITICAL] else "ℹ️"
        payload = {
            "chat_id": self.chat_id,
            "text": f"{prefix} *BTC MARKET ALERT* {prefix}\n\n{message}",
            "parse_mode": "Markdown"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Telegram alert sent successfully")
                        return True
                    else:
                        resp_json = await response.json()
                        logger.error("Telegram API error", status=response.status, msg=resp_json.get("description"))
                        return False
        except Exception as e:
            logger.error("Failed to deliver Telegram alert", error=str(e))
            return False
