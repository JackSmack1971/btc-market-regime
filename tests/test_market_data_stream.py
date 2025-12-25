"""
Unit tests for MarketDataStream Producer-Consumer pattern.
"""

import unittest
import time
from unittest.mock import MagicMock, patch
from src.streaming.market_data_stream import MarketDataStream


class TestMarketDataStream(unittest.TestCase):
    """Test suite for MarketDataStream class."""
    
    def test_stream_initialization(self):
        """Verify stream initializes without errors."""
        sources_config = {
            'test_metric': {'url': 'http://example.com', 'source': 'test'}
        }
        stream = MarketDataStream(sources_config, days_hist=30, refresh_interval=60)
        
        self.assertIsNotNone(stream.data_buffer)
        self.assertEqual(stream.data_buffer.maxlen, 1)
        self.assertEqual(stream.days_hist, 30)
        self.assertEqual(stream.refresh_interval, 60)
        self.assertFalse(stream._running)
    
    def test_buffer_maxlen(self):
        """Verify deque only keeps latest data."""
        stream = MarketDataStream({}, 30)
        
        stream.data_buffer.append({'data': 1, 'timestamp': time.time()})
        self.assertEqual(len(stream.data_buffer), 1)
        
        stream.data_buffer.append({'data': 2, 'timestamp': time.time()})
        self.assertEqual(len(stream.data_buffer), 1)
        self.assertEqual(stream.data_buffer[-1]['data'], 2)
    
    def test_get_latest_empty(self):
        """Verify get_latest returns None when buffer is empty."""
        stream = MarketDataStream({}, 30)
        latest = stream.get_latest()
        self.assertIsNone(latest)
    
    def test_get_latest_with_data(self):
        """Verify get_latest returns correct data."""
        stream = MarketDataStream({}, 30)
        test_data = {'metrics_map': {}, 'timestamp': time.time()}
        stream.data_buffer.append(test_data)
        
        latest = stream.get_latest()
        self.assertIsNotNone(latest)
        self.assertEqual(latest, test_data)
    
    def test_get_stats(self):
        """Verify get_stats returns correct statistics."""
        stream = MarketDataStream({}, 30)
        stats = stream.get_stats()
        
        self.assertIn('running', stats)
        self.assertIn('fetch_count', stats)
        self.assertIn('error_count', stats)
        self.assertIn('buffer_size', stats)
        self.assertIn('uvloop_enabled', stats)
        self.assertIn('thread_alive', stats)
        
        self.assertFalse(stats['running'])
        self.assertEqual(stats['fetch_count'], 0)
        self.assertEqual(stats['error_count'], 0)
        self.assertEqual(stats['buffer_size'], 0)
    
    @patch('src.streaming.market_data_stream.threading.Thread')
    def test_start_creates_thread(self, mock_thread):
        """Verify start() creates and starts a daemon thread."""
        stream = MarketDataStream({}, 30)
        stream.start()
        
        self.assertTrue(stream._running)
        mock_thread.assert_called_once()
        
        # Verify daemon=True was passed
        call_kwargs = mock_thread.call_args[1]
        self.assertTrue(call_kwargs['daemon'])
        self.assertEqual(call_kwargs['name'], 'MarketDataProducer')
    
    def test_stop_sets_running_false(self):
        """Verify stop() sets _running to False."""
        stream = MarketDataStream({}, 30)
        stream._running = True
        stream.stop()
        
        self.assertFalse(stream._running)
    
    def test_performance_tracking(self):
        """Verify fetch and error counts are tracked."""
        stream = MarketDataStream({}, 30)
        
        self.assertEqual(stream._fetch_count, 0)
        self.assertEqual(stream._error_count, 0)
        
        # Simulate some activity
        stream._fetch_count = 5
        stream._error_count = 1
        
        stats = stream.get_stats()
        self.assertEqual(stats['fetch_count'], 5)
        self.assertEqual(stats['error_count'], 1)


if __name__ == '__main__':
    unittest.main()
