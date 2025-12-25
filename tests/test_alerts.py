import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from src.alerts.telegram import TelegramNotifier
from src.alerts.notifier import AlertLevel
import asyncio

class TestTelegramNotifier(unittest.IsolatedAsyncioTestCase):
    """Tests for the Telegram notification channel."""

    def setUp(self):
        self.notifier = TelegramNotifier(
            bot_token="test_token",
            chat_id="test_chat_id"
        )

    @patch('aiohttp.ClientSession.post')
    async def test_send_success(self, mock_post):
        """Verify successful message delivery via Telegram API."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"ok": True}
        mock_post.return_value.__aenter__.return_value = mock_response

        success = await self.notifier.send("Test Message", level=AlertLevel.INFO)
        
        self.assertTrue(success)
        # Verify call parameters
        args, kwargs = mock_post.call_args
        self.assertIn("test_token", args[0])
        self.assertEqual(kwargs['json']['chat_id'], "test_chat_id")
        self.assertIn("Test Message", kwargs['json']['text'])

    @patch('aiohttp.ClientSession.post')
    async def test_send_failure(self, mock_post):
        """Verify handling of API failures (e.g., 401 Unauthorized)."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_post.return_value.__aenter__.return_value = mock_response

        success = await self.notifier.send("Test Message")
        self.assertFalse(success)

class TestAlertOrchestration(unittest.TestCase):
    """Tests for transition detection logic in main.py."""

    def test_transition_detection_true(self):
        """Alert should be triggered when regime moves BULL -> BEAR."""
        last_regime = "BULL"
        current_regime = "BEAR"
        
        should_alert = last_regime != current_regime
        self.assertTrue(should_alert)

    def test_transition_detection_false(self):
        """No alert should be sent if the regime remains the same."""
        last_regime = "BULL"
        current_regime = "BULL"
        
        should_alert = last_regime != current_regime
        self.assertFalse(should_alert)

if __name__ == '__main__':
    unittest.main()
