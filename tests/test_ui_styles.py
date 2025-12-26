"""
Comprehensive unit tests for src/ui/styles.py

Test Coverage:
- inject_bloomberg_styles(): CSS injection and content validation
- Streamlit integration mocking
- CSS selector presence validation
"""

import unittest
from unittest.mock import Mock, patch, call
import re


class TestInjectBloombergStyles(unittest.TestCase):
    """Comprehensive tests for inject_bloomberg_styles function."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.mock_st_html = Mock()
    
    def tearDown(self):
        """Cleanup after tests."""
        self.mock_st_html.reset_mock()
    
    # ========== HAPPY PATH TESTS ==========
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_calls_st_html(self, mock_html):
        """Test inject_bloomberg_styles successfully calls st.html()."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify st.html was called exactly once
        self.assertEqual(mock_html.call_count, 1, 
                        "st.html should be called exactly once")
        
        # Assert: Verify it was called with a string argument
        call_args = mock_html.call_args[0][0]
        self.assertIsInstance(call_args, str,
                            "st.html should be called with a string")
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_injects_valid_css(self, mock_html):
        """Test that injected CSS contains style tags."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify CSS contains <style> tags
        injected_css = mock_html.call_args[0][0]
        self.assertIn('<style>', injected_css,
                     "Injected content should contain <style> tag")
        self.assertIn('</style>', injected_css,
                     "Injected content should contain closing </style> tag")
    
    # ========== EDGE CASE TESTS ==========
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_contains_jetbrains_mono_font(self, mock_html):
        """Test CSS includes JetBrains Mono font import."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify JetBrains Mono is imported
        injected_css = mock_html.call_args[0][0]
        self.assertIn('JetBrains+Mono', injected_css,
                     "CSS should import JetBrains Mono font")
        self.assertIn('@import url', injected_css,
                     "CSS should use @import for fonts")
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_contains_tabular_nums(self, mock_html):
        """Test CSS enforces tabular-nums for typography engineering."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify tabular-nums is present
        injected_css = mock_html.call_args[0][0]
        self.assertIn('tabular-nums', injected_css,
                     "CSS should include tabular-nums for alignment")
        self.assertIn('font-variant-numeric', injected_css,
                     "CSS should use font-variant-numeric property")
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_contains_flash_effects(self, mock_html):
        """Test CSS includes 200ms flash effect keyframes."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify flash animations are defined
        injected_css = mock_html.call_args[0][0]
        self.assertIn('@keyframes value-flash', injected_css,
                     "CSS should define value-flash keyframes")
        self.assertIn('200ms', injected_css,
                     "Flash effect should be 200ms duration")
        self.assertIn('animation:', injected_css,
                     "CSS should apply animations")
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_contains_semantic_colors(self, mock_html):
        """Test CSS includes Bloomberg Red and Finance Green colors."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify semantic colors are present
        injected_css = mock_html.call_args[0][0]
        
        # Bloomberg Red: #FF433D
        self.assertIn('rgba(255, 67, 61', injected_css,
                     "CSS should include Bloomberg Red (rgba)")
        
        # Finance Green: #4AF6C3
        self.assertIn('rgba(74, 246, 195', injected_css,
                     "CSS should include Finance Green (rgba)")
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_contains_anti_jitter_rules(self, mock_html):
        """Test CSS includes anti-jitter engineering (fixed widths)."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify fixed min-width rules
        injected_css = mock_html.call_args[0][0]
        self.assertIn('min-width', injected_css,
                     "CSS should use min-width to prevent jitter")
        self.assertIn('180px', injected_css,
                     "CSS should set metric container min-width to 180px")
    
    @patch('src.ui.styles.st.html')
    def test_inject_bloomberg_styles_css_selector_count(self, mock_html):
        """Test CSS contains expected number of selectors."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Count CSS rule blocks (rough estimate)
        injected_css = mock_html.call_args[0][0]
        selector_pattern = r'\{[^}]+\}'
        selector_count = len(re.findall(selector_pattern, injected_css))
        
        # Should have at least 20 CSS rule blocks
        self.assertGreater(selector_count, 20,
                          f"CSS should have >20 rule blocks, found {selector_count}")
    
    # ========== ERROR SCENARIO TESTS ==========
    
    @patch('src.ui.styles.st.html', side_effect=Exception("Streamlit HTML injection failed"))
    def test_inject_bloomberg_styles_handles_st_html_failure(self, mock_html):
        """Test function behavior when st.html() raises exception."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act & Assert: Verify exception is raised (no error handling in function)
        with self.assertRaises(Exception) as context:
            inject_bloomberg_styles()
        
        self.assertIn("Streamlit HTML injection failed", str(context.exception),
                     "Exception should propagate from st.html()")
    
    @patch('src.ui.styles.st')
    def test_inject_bloomberg_styles_validates_streamlit_import(self, mock_st):
        """Test function requires streamlit module to be available."""
        # Arrange
        mock_st.html = Mock()
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify streamlit was accessed
        self.assertTrue(mock_st.html.called,
                       "Function should call streamlit.html")


class TestCSSContentValidation(unittest.TestCase):
    """Tests for CSS content correctness and Bloomberg Terminal standards."""
    
    @patch('src.ui.styles.st.html')
    def test_css_includes_performance_optimizations(self, mock_html):
        """Test CSS includes GPU acceleration and font rendering optimizations."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify performance optimizations
        injected_css = mock_html.call_args[0][0]
        
        self.assertIn('translateZ(0)', injected_css,
                     "Should use translateZ(0) for GPU acceleration")
        self.assertIn('backface-visibility', injected_css,
                     "Should set backface-visibility for performance")
        self.assertIn('-webkit-font-smoothing', injected_css,
                     "Should optimize font rendering")
    
    @patch('src.ui.styles.st.html')
    def test_css_includes_streamlit_specific_selectors(self, mock_html):
        """Test CSS targets Streamlit-specific data-testid attributes."""
        # Arrange
        from src.ui.styles import inject_bloomberg_styles
        
        # Act
        inject_bloomberg_styles()
        
        # Assert: Verify Streamlit-specific selectors
        injected_css = mock_html.call_args[0][0]
        
        self.assertIn('[data-testid="stMetricValue"]', injected_css,
                     "Should target stMetricValue")
        self.assertIn('[data-testid="stMetric"]', injected_css,
                     "Should target stMetric")
        self.assertIn('.block-container', injected_css,
                     "Should target block-container")


if __name__ == '__main__':
    unittest.main()
