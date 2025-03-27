"""
Unit tests for the ticket_checker.py script.

This module contains basic tests to verify the functionality of the ticket checker.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import logging

# Disable logging during tests
logging.disable(logging.CRITICAL)

# Import the module to test
import ticket_checker

class TestTicketChecker(unittest.TestCase):
    """Tests for the ticket_checker module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create debug screenshot directory if it doesn't exist
        os.makedirs(ticket_checker.DEBUG_SCREENSHOTS_DIR, exist_ok=True)
    
    @patch('ticket_checker.webdriver.Chrome')
    @patch('ticket_checker.Service')
    @patch('ticket_checker.ChromeDriverManager')
    def test_setup_driver(self, mock_chrome_driver_manager, mock_service, mock_chrome):
        """Test the setup_driver function."""
        # Setup mocks
        mock_chrome_driver_manager.return_value.install.return_value = '/path/to/chromedriver'
        mock_service.return_value = 'mocked_service'
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        
        # Call the function
        driver = ticket_checker.setup_driver(headless=True)
        
        # Verify Chrome was initialized with the right parameters
        mock_chrome.assert_called_once()
        self.assertEqual(driver, mock_driver)
        
        # Verify the driver is configured to hide automation
        mock_driver.execute_script.assert_called_once()
    
    @patch('ticket_checker.setup_driver')
    @patch('ticket_checker.WebDriverWait')
    def test_check_tickets_unavailable(self, mock_wait, mock_setup_driver):
        """Test the check_tickets function when tickets are unavailable."""
        # Setup mocks
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver
        
        # Mock the elements that would indicate tickets are unavailable
        unavailable_element = MagicMock()
        mock_driver.find_elements.return_value = [unavailable_element]  # "Unavailable" message found

        # Call the function
        result = ticket_checker.check_tickets(
            url="https://example.com/test",
            category_num="3",
            debug=False
        )

        # Verify result is False (tickets unavailable)
        self.assertFalse(result)

        # Verify driver was created and quit
        mock_setup_driver.assert_called_once()
        mock_driver.quit.assert_called_once()

    @patch('ticket_checker.setup_driver')
    @patch('ticket_checker.WebDriverWait')
    @patch('ticket_checker.time.sleep')  # Mock sleep to avoid delays
    def test_check_tickets_available(self, mock_sleep, mock_wait, mock_setup_driver):
        """Test the check_tickets function when tickets are available."""
        # Setup mocks
        mock_driver = MagicMock()
        mock_setup_driver.return_value = mock_driver

        # Configure mock responses for the different find_elements calls
        def find_elements_side_effect(*args, **kwargs):
            # Check which call is being made based on the selector
            selector = args[1] if len(args) > 1 else kwargs.get('value', '')

            if "Unavailable: Category" in str(selector):
                # First call - checking for "Unavailable" message
                return []  # No unavailable message found
            elif ".bookableItem" in str(selector) or "booking-option" in str(selector):
                # Second call - checking for booking options
                mock_option = MagicMock()
                mock_option.text = "Category 3 - Some details"

                # Set up buttons to be found
                mock_button = MagicMock()
                mock_option.find_elements.return_value = [mock_button]

                return [mock_option]
            else:
                return []

        mock_driver.find_elements.side_effect = find_elements_side_effect

        # Call the function
        result = ticket_checker.check_tickets(
            url="https://example.com/test",
            category_num="3",
            debug=False
        )

        # Verify result is True (tickets available)
        self.assertTrue(result)

        # Verify driver was created and quit
        mock_setup_driver.assert_called_once()
        mock_driver.quit.assert_called_once()

    @patch('builtins.input', return_value='')
    @patch('ticket_checker.check_multiple_categories')
    @patch('ticket_checker.webbrowser')
    @patch('ticket_checker.play_notification')
    def test_main_with_tickets_found(self, mock_play, mock_browser, mock_check_multi, mock_input):
        """Test the main function when tickets are found."""
        # Setup mocks
        mock_check_multi.return_value = ({"3": True, "4": False}, ["3"])  # Category 3 tickets found

        # Mock the command line arguments
        with patch('sys.argv', ['ticket_checker.py', '--test']):
            # Run the main function
            ticket_checker.main()

        # Verify notifications and browser were triggered
        mock_play.assert_called_once()
        mock_browser.open.assert_called_once()

    def test_check_multiple_categories(self):
        """Test the check_multiple_categories function."""
        # Mock the check_tickets function
        with patch('ticket_checker.check_tickets') as mock_check:
            # Configure the mock to return different values for different categories
            mock_check.side_effect = lambda url, cat, *args, **kwargs: cat == "3"  # Only category 3 is available

            # Call the function with multiple categories
            results, available = ticket_checker.check_multiple_categories(
                "https://example.com", ["2", "3", "4"], debug=False
            )

            # Check results
            self.assertEqual(results, {"2": False, "3": True, "4": False})
            self.assertEqual(available, ["3"])

    def test_colors_class(self):
        """Test that the Colors class has the necessary color codes."""
        self.assertTrue(hasattr(ticket_checker.Colors, 'RED'))
        self.assertTrue(hasattr(ticket_checker.Colors, 'GREEN'))
        self.assertTrue(hasattr(ticket_checker.Colors, 'YELLOW'))
        self.assertTrue(hasattr(ticket_checker.Colors, 'WHITE'))
        self.assertTrue(hasattr(ticket_checker.Colors, 'RESET'))

if __name__ == '__main__':
    unittest.main()