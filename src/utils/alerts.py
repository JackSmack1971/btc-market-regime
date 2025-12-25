import requests
import os
from typing import Optional
from ..utils import logger

class TelegramAlertManager:
    """Sends notifications to Telegram via the Bot API."""
    
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        # Allow passing directly or pulling from environment/config
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.token and self.chat_id)
        
        if not self.enabled:
            logger.warning("Telegram alerts disabled: Missing token or chat_id")

    def send_message(self, message: str) -> bool:
        """Sends a text message to the configured chat.
        
        Args:
            message: The content to send.
            
        Returns:
            bool: True if sent successfully, False otherwise.
        """
        if not self.enabled:
            logger.info("MOCKED TELEGRAM ALERT", message=message)
            return True
            
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info("Telegram alert sent successfully")
            return True
        except Exception as e:
            logger.error("Failed to send Telegram alert", error=str(e))
            return False

# Global alert instance
alert_manager = TelegramAlertManager()
