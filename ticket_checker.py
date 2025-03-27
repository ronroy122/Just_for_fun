"""
Ticket Availability Checker for TripAdvisor Concert Listings

This script automatically monitors TripAdvisor concert ticket listings and alerts
when tickets in a specified category become available. It uses Selenium WebDriver
to analyze the page structure and detect changes in ticket availability.

Author: Your Name
Date: March 2025
"""

import time
import logging
import os
from datetime import datetime
import webbrowser
import argparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Define ANSI color codes for terminal output
class Colors:
    WHITE = '\033[37m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

# Create screenshot directory if it doesn't exist
DEBUG_SCREENSHOTS_DIR = "debug_screenshots"
os.makedirs(DEBUG_SCREENSHOTS_DIR, exist_ok=True)

# Custom logging handler with color support
class ColorHandler(logging.StreamHandler):
    """Custom logging handler that adds color to terminal output based on message level."""

    def emit(self, record):
        msg = self.format(record)

        # Check message content for availability status
        if "Category" in msg and ("available" in msg.lower() or "found" in msg.lower()):
            if "no " in msg.lower() or "not " in msg.lower() or "unavailable" in msg.lower():
                # Yellow for unavailable tickets
                msg = f"{Colors.YELLOW}{msg}{Colors.RESET}"
            else:
                # Green for available tickets
                msg = f"{Colors.GREEN}{msg}{Colors.RESET}"
        elif record.levelno >= logging.ERROR:
            # Red for errors
            msg = f"{Colors.RED}{msg}{Colors.RESET}"
        elif record.levelno >= logging.WARNING:
            # Yellow for warnings
            msg = f"{Colors.YELLOW}{msg}{Colors.RESET}"
        else:
            # White for regular messages
            msg = f"{Colors.WHITE}{msg}{Colors.RESET}"

        stream = self.stream
        stream.write(msg + self.terminator)
        self.flush()

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Add file handler
file_handler = logging.FileHandler("ticket_checker.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

# Add color handler for terminal
color_handler = ColorHandler()
color_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(color_handler)

def setup_driver(headless=True):
    """
    Initialize and return a Chrome WebDriver instance with ChromeDriverManager.

    Args:
        headless (bool): Whether to run the browser in headless mode (without GUI)

    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance

    Raises:
        WebDriverException: If there's an issue initializing the WebDriver
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")  # New headless mode for recent Chrome versions
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")

    # Disable cache to ensure fresh content on every check
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disable-cache")
    chrome_options.add_argument("--disk-cache-size=0")

    # Prevent automation detection
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    try:
        # Use ChromeDriverManager to automatically install the correct driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Hide WebDriver usage to prevent detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except WebDriverException as e:
        logger.error(f"Failed to initialize WebDriver: {e}")
        raise

def play_notification():
    """
    Play an audio alert when tickets are found.
    Uses Beep on Windows or ASCII bell on other platforms.
    """
    try:
        # For Windows
        import winsound
        winsound.Beep(1000, 1000)  # 1000Hz frequency for 1 second
        winsound.Beep(1200, 1000)  # 1200Hz frequency for 1 second
    except:
        # For other platforms
        print('\a')  # ASCII Bell

def take_screenshot(driver, prefix="screenshot"):
    """
    Take a screenshot of the current browser window.

    Args:
        driver: Selenium WebDriver instance
        prefix (str): Prefix for the screenshot filename

    Returns:
        str: Path to the saved screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{DEBUG_SCREENSHOTS_DIR}/{prefix}_{timestamp}.png"
    driver.save_screenshot(filename)
    logger.debug(f"Screenshot saved: {filename}")
    return filename

def check_tickets(url, category_num="3", timeout=30, visible=False, debug=False):
    """
    Check if tickets in a specific category are available on the TripAdvisor page.

    This function uses multiple methods to detect ticket availability:
    1. Checking for the absence of "Unavailable: Category X" text
    2. Looking for active booking options with the desired category
    3. Analyzing page elements that mention the category without unavailability indicators

    Args:
        url (str): TripAdvisor listing URL to check
        category_num (str): Category number to check (without the "Category" prefix)
        timeout (int): Maximum time to wait for page loading in seconds
        visible (bool): Whether to show the browser window during checks
        debug (bool): Whether to print detailed debug information and save screenshots

    Returns:
        bool: True if tickets appear to be available, False otherwise
    """
    driver = setup_driver(headless=not visible)

    try:
        logger.info(f"Checking availability for Category {category_num} tickets...")
        driver.get(url)

        # Force a complete refresh to bypass cache
        driver.execute_script("location.reload(true);")

        # Wait for the page to load
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Additional wait for dynamic elements
        time.sleep(2)

        # Save screenshot if in debug mode
        if debug:
            screenshot_path = take_screenshot(driver, f"page_category_{category_num}")
            logger.debug(f"Saved initial page screenshot to {screenshot_path}")

        # === Method 1: Check for "Unavailable" messages ===
        unavailable_text = f"Unavailable: Category {category_num}"

        unavailable_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{unavailable_text}')]")

        if unavailable_elements:
            if debug:
                logger.debug(f"Found text '{unavailable_text}' - tickets are unavailable")
            logger.info(f"No Category {category_num} tickets available at this time.")
            return False

        # === Method 2: Look for active booking options ===
        booking_options = driver.find_elements(By.CSS_SELECTOR,
            ".bookableItem, [class*='booking-option'], [class*='price-option'], .popular")

        for option in booking_options:
            option_text = option.text

            # Check if the option references our category
            if f"Category {category_num}" in option_text:
                # Look for booking buttons
                buttons = option.find_elements(By.CSS_SELECTOR,
                    "button, .button, [class*='btn'], [class*='reserve'], a[href*='book']")

                if buttons:
                    if debug:
                        logger.debug(f"Found booking option for Category {category_num} with active button")
                    logger.info(f"Category {category_num} tickets available for booking!")
                    return True

        # === Method 3: Look for category mentions without unavailability ===
        category_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), 'Category {category_num}')]")

        for element in category_elements:
            element_text = element.text

            # If the element mentions our category without "Unavailable"
            if "Unavailable" not in element_text and f"Category {category_num}" in element_text:
                # Look for booking buttons in the element's vicinity
                parent = element
                for _ in range(5):  # Check 5 levels of parent elements
                    try:
                        parent = parent.find_element(By.XPATH, "./..")
                        buttons = parent.find_elements(By.CSS_SELECTOR,
                            "button, .button, [class*='btn'], [class*='reserve'], a[href*='book']")

                        if buttons:
                            if debug:
                                logger.debug(f"Found element mentioning Category {category_num} with nearby booking button")
                            logger.info(f"Category {category_num} tickets appear to be available!")
                            return True
                    except:
                        break

        # Additional check for category mentions in the page
        page_text = driver.find_element(By.TAG_NAME, "body").text

        if debug:
            logger.debug(f"Is 'Category {category_num}' in page: {f'Category {category_num}' in page_text}")
            logger.debug(f"Is '{unavailable_text}' in page: {unavailable_text in page_text}")

        if f"Category {category_num}" in page_text and unavailable_text not in page_text:
            # Check if there are any booking buttons on the page
            reserve_buttons = driver.find_elements(By.XPATH,
                "//button[contains(text(), 'Reserve')] | //a[contains(text(), 'Book')]")

            if reserve_buttons:
                logger.info(f"Category {category_num} is mentioned without unavailability indication and booking buttons exist")
                logger.info(f"Category {category_num} tickets may be available - worth checking!")
                return True

        # If we get here, no tickets were found
        logger.info(f"No Category {category_num} tickets available.")
        return False

    except Exception as e:
        logger.error(f"Error checking tickets: {str(e)}")
        if debug:
            take_screenshot(driver, "error")
        return False

    finally:
        # Close the browser
        driver.quit()

def check_multiple_categories(url, categories, timeout=30, visible=False, debug=False):
    """
    Check multiple ticket categories for availability.

    Args:
        url (str): TripAdvisor listing URL to check
        categories (list): List of category numbers to check
        timeout (int): Maximum time to wait for page loading in seconds
        visible (bool): Whether to show the browser window during checks
        debug (bool): Whether to print detailed debug information

    Returns:
        dict: Dictionary with category numbers as keys and availability (bool) as values
    """
    results = {}
    available_categories = []

    for category in categories:
        logger.info(f"Checking Category {category}...")
        is_available = check_tickets(url, category, timeout, visible, debug)
        results[category] = is_available

        if is_available:
            available_categories.append(category)

    return results, available_categories

def main():
    """
    Main function that handles command-line arguments and runs the ticket checking loop.
    """
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='TripAdvisor Concert Ticket Availability Checker')
    parser.add_argument('--interval', type=int, default=60,
                      help='Check interval in seconds (default: 60)')
    parser.add_argument('--categories', type=str, default="3,4",
                      help='Comma-separated list of ticket category numbers to check (default: "3,4")')
    parser.add_argument('--visible', action='store_true',
                      help='Show browser window during checks')
    parser.add_argument('--debug', action='store_true',
                      help='Enable detailed debug output and screenshots')
    parser.add_argument('--test', action='store_true',
                      help='Perform a single check and exit')
    parser.add_argument('--url', type=str,
                      default="https://www.tripadvisor.com/AttractionProductReview-g190454-d19350909-Vienna_Vivaldi_s_The_Four_Seasons_Mozart_in_the_Musikverein-Vienna.html",
                      help='URL of the TripAdvisor listing to check')
    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")

    url = args.url
    interval = args.interval
    # Parse comma-separated categories into a list
    categories = [cat.strip() for cat in args.categories.split(',')]

    logger.info(f"Starting to check for Categories {', '.join(categories)} tickets every {interval} seconds...")
    logger.info(f"Press Ctrl+C to stop the program")

    # Test mode - just run once
    if args.test:
        logger.info("Running in TEST mode - will perform a single check")
        results, available_categories = check_multiple_categories(
            url, categories, visible=True, debug=True
        )

        if available_categories:
            logger.info(f"Tickets available in categories: {', '.join(available_categories)}!")
            play_notification()
            webbrowser.open(url)
        else:
            logger.info("No tickets available in any of the selected categories.")
        return

    # Normal mode - periodic checking
    try:
        while True:
            # Perform the check for all categories
            results, available_categories = check_multiple_categories(
                url, categories, visible=args.visible, debug=args.debug
            )

            if available_categories:
                # Tickets found - alert the user
                play_notification()

                # Open the booking page
                webbrowser.open(url)

                # Wait for user input before continuing
                input(f"Tickets found in categories {', '.join(available_categories)}! "
                      f"Press Enter to continue checking, or Ctrl+C to exit...")

            # Wait before the next check
            logger.info(f"Waiting {interval} seconds before next check...")
            time.sleep(interval)

    except KeyboardInterrupt:
        # User stopped the program (Ctrl+C)
        logger.info("Program stopped by user")

if __name__ == "__main__":
    main()
