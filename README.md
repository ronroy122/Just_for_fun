# Concert Ticket Availability Checker

A Python application that automatically monitors TripAdvisor for concert ticket availability in Vienna's Musikverein. When tickets become available in your chosen category, it alerts you immediately and opens the booking page.

![Ticket Checker Demo](https://media.githubusercontent.com/media/yourusername/concert-ticket-checker/main/docs/demo.gif)

## Features

- **Automatic Monitoring**: Checks for ticket availability at specified intervals
- **Smart Detection**: Uses multiple verification methods to ensure accurate availability detection
- **Real-time Alerts**: Plays a sound alert when tickets become available
- **Auto-navigation**: Opens the booking page automatically when tickets are found
- **User-friendly Interface**: Color-coded terminal output for better readability
- **Robust Logging**: Detailed logging for troubleshooting and history
- **Customizable**: Adjustable check intervals and category selection

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/concert-ticket-checker.git
cd concert-ticket-checker
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python ticket_checker.py
```
This will check for both Category 3 and Category 4 tickets every 60 seconds (1 minute).

### Command Line Options
```bash
python ticket_checker.py --interval 120 --categories 2,3,4 --debug
```

Available options:
- `--interval`: Time between checks in seconds (default: 60)
- `--categories`: Comma-separated list of ticket categories to check (default: "3,4")
- `--visible`: Show browser window during checks
- `--debug`: Enable detailed debug output and screenshots
- `--test`: Perform a single check and exit (useful for testing)
- `--url`: URL of the TripAdvisor listing to check (in case you want to monitor a different concert)

## Example Workflow

1. Start the checker to monitor Categories 2, 3 and 4 tickets every minute:
   ```bash
   python ticket_checker.py --categories 2,3,4
   ```

2. The program will:
   - Check the TripAdvisor page for ticket availability
   - Log the results to console and log file
   - Continue checking at the specified interval

3. When tickets become available:
   - You'll hear an alert sound
   - The booking page will open in your default browser
   - You'll be prompted to continue monitoring or exit

## How It Works

The application uses Selenium WebDriver to open and analyze the TripAdvisor page. It employs multiple methods to detect ticket availability:

1. **Absence Detection**: Checking for the absence of "Unavailable: Category X" text
2. **Option Detection**: Looking for active booking options with the desired category
3. **Context Analysis**: Analyzing page elements that mention the category without unavailability indicators

When available tickets are detected, the application alerts you immediately so you can proceed with booking.

## Technical Skills Demonstrated

This project demonstrates several important technical skills for data science and software development:

### 1. Web Scraping & Automation
- **Selenium WebDriver**: Programmatic control of a browser for dynamic content scraping
- **DOM Parsing**: Identifying and extracting specific elements from web pages
- **Automated Navigation**: Programmatic interaction with web interfaces

### 2. Software Engineering Practices
- **Modular Design**: Well-organized, maintainable code structure
- **Error Handling**: Robust exception handling for reliability
- **Testing**: Unit tests to verify functionality
- **Logging**: Comprehensive logging for debugging and tracking

### 3. Python Programming
- **CLI Development**: Command-line interface with argparse
- **File I/O**: Managing files and directories
- **External Libraries**: Effective use of third-party packages
- **Cross-platform Support**: Compatible with different operating systems

### 4. Data Analysis Concepts
- **Data Extraction**: Isolating relevant information from complex sources
- **Pattern Recognition**: Identifying specific patterns that indicate availability
- **Alert Systems**: Creating notification systems for important events

## Requirements

- Python 3.6+
- Chrome browser
- Selenium WebDriver
- Other dependencies listed in requirements.txt

## Project Structure

- `ticket_checker.py`: Main application script
- `test_ticket_checker.py`: Unit tests
- `requirements.txt`: Required Python packages
- `debug_screenshots/`: Directory for debug screenshots (created automatically)
- `ticket_checker.log`: Log file with detailed operation history

## Running Tests

To run the unit tests:
```bash
python -m unittest test_ticket_checker.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/concert-ticket-checker/issues).

## Future Improvements

Potential enhancements for future versions:
- Email or SMS notifications when tickets become available
- Support for multiple ticket categories simultaneously
- GUI interface for easier configuration
- Support for additional ticket vendors beyond TripAdvisor

## Acknowledgments

- This project was created to solve the practical problem of monitoring concert ticket availability
- Inspired by the need to attend Vienna's famous classical music concerts
