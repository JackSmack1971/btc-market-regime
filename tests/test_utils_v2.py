import unittest
import time
from unittest.mock import MagicMock, patch
from src.utils import (
    CircuitBreaker, retry_with_backoff, MaxRetriesExceeded,
    AppError, NetworkError, TimeoutError
)
from src.utils.alerts import TelegramAlertManager
from src.utils.health import HealthTracker, HealthEntry

class TestUtils(unittest.TestCase):
    # ========== CIRCUIT BREAKER TESTS ==========
    def test_circuit_breaker_happy_path(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
        self.assertTrue(cb.is_available("service_a"))
        
        cb.report_failure("service_a")
        self.assertTrue(cb.is_available("service_a"))
        
        cb.report_failure("service_a") # Reaches threshold
        self.assertFalse(cb.is_available("service_a"))
        
        time.sleep(0.15)
        self.assertTrue(cb.is_available("service_a")) # HALF-OPEN
        
        cb.report_success("service_a")
        self.assertEqual(cb.failures["service_a"], 0)
        self.assertEqual(cb.state["service_a"], "CLOSED")

    def test_circuit_breaker_different_services(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.report_failure("service_a")
        self.assertFalse(cb.is_available("service_a"))
        self.assertTrue(cb.is_available("service_b"))

    # ========== RETRY DECORATOR TESTS ==========
    def test_retry_success_first_try(self):
        mock_func = MagicMock(return_value="success")
        mock_func.__name__ = "mock_func"
        decorated = retry_with_backoff(max_attempts=3, base_delay=0.01)(mock_func)
        
        result = decorated("arg")
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)

    def test_retry_success_after_failure(self):
        mock_func = MagicMock(side_effect=[ValueError("fail"), "success"])
        mock_func.__name__ = "mock_func"
        # Mocking time.sleep to speed up tests
        with patch('time.sleep'):
            decorated = retry_with_backoff(max_attempts=3, base_delay=0.01)(mock_func)
            result = decorated()
            self.assertEqual(result, "success")
            self.assertEqual(mock_func.call_count, 2)

    def test_retry_max_retries_exceeded(self):
        mock_func = MagicMock(side_effect=ValueError("constant fail"))
        mock_func.__name__ = "mock_func"
        with patch('time.sleep'):
            decorated = retry_with_backoff(max_attempts=2, base_delay=0.01)(mock_func)
            with self.assertRaises(MaxRetriesExceeded):
                decorated()
            self.assertEqual(mock_func.call_count, 2)

    def test_retry_specific_exceptions(self):
        # Should NOT retry for TypeError
        mock_func = MagicMock(side_effect=TypeError("not handled"))
        mock_func.__name__ = "mock_func"
        decorated = retry_with_backoff(max_attempts=3, exceptions=(ValueError,))(mock_func)
        
        with self.assertRaises(TypeError):
            decorated()
        self.assertEqual(mock_func.call_count, 1)

    # ========== EXCEPTION HIERARCHY TESTS ==========
    def test_exception_inheritance(self):
        self.assertTrue(issubclass(NetworkError, AppError))
        self.assertTrue(issubclass(TimeoutError, AppError))
        self.assertTrue(issubclass(AppError, Exception))

class TestAlerts(unittest.TestCase):
    def test_telegram_manager_disabled(self):
        with patch('os.getenv', return_value=None):
            manager = TelegramAlertManager(token=None, chat_id=None)
            self.assertFalse(manager.enabled)
            # Should not crash and return True (mocked)
            self.assertTrue(manager.send_message("test"))

    @patch('requests.post')
    def test_telegram_manager_send_success(self, mock_post):
        mock_post.return_value.status_code = 200
        manager = TelegramAlertManager(token="tag", chat_id="123")
        self.assertTrue(manager.enabled)
        self.assertTrue(manager.send_message("hello"))
        self.assertEqual(mock_post.call_count, 1)

    @patch('requests.post')
    def test_telegram_manager_send_failure(self, mock_post):
        mock_post.side_effect = Exception("network fail")
        manager = TelegramAlertManager(token="tag", chat_id="123")
        self.assertFalse(manager.send_message("hello"))

class TestHealth(unittest.TestCase):
    def test_health_tracker_logic(self):
        tracker = HealthTracker()
        # Empty state
        self.assertTrue(tracker.get_summary().empty)
        self.assertEqual(tracker.get_latest_status(), {})
        
        # Log attempt
        tracker.log_attempt("btc_price", "primary", True, 150.5)
        tracker.log_attempt("mvrv", "backup", False, 500.0, "timeout")
        
        summary = tracker.get_summary()
        self.assertEqual(len(summary), 2)
        
        status = tracker.get_latest_status()
        self.assertEqual(status["btc_price"]["last_success"], True)
        self.assertEqual(status["mvrv"]["last_error"], "timeout")

if __name__ == "__main__":
    unittest.main()
