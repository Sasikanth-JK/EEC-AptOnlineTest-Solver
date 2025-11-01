# EEC Apt Online Test Solver

An automated solution for solving online aptitude tests using Google's Gemini AI and Playwright browser automation.

## Features

- **AI-Powered Solving**: Uses Google Gemini 2.5 Pro or any other model to analyze and answer quiz questions
- **Browser Automation**: Automated login, navigation, and answer selection using Playwright
- **Async Architecture**: Fully asynchronous implementation for better performance
- **Error Handling**: Robust retry mechanisms and error logging
- **Docker Support**: Containerized deployment for easy setup and portability

## Architecture

The application consists of several key components:

- `main.py` - Main orchestrator handling the test flow
- `gemini_utils.py` - AI model initialization and response handling
- `browser_utils.py` - Browser automation utilities
- `config.py` - Configuration management
- `logger.py` - Logging utilities
- `ext_utils.py` - Extension utilities for test completion checking

## Prerequisites

- Python 3.11 or higher
- Google Gemini API key
- Valid test portal credentials

## Installation

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Sasikanth-JK/EEC-AptOnlineTest-Solver.git
   cd EEC-AptOnlineTest-Solver
   ```

2. **Install dependencies**
   
   Using uv (recommended):
   ```bash
   # Install uv if not already installed (linux)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   uv pip install -r requirements.txt
   playwright install chromium

   ## for windows
   pip install uv
   uv pip install -r requirements.txt
   uv run playwright install chromium
   ```
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Configure the application**
   
   Copy the sample environment file (linux):
   ```bash
   cp .env.sample .env
   ```
   Copy the sample environment file (windows):
   ```bash
   copy .env.sample .env
   ```
   
   Edit `.env` with your credentials:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   USER_ID=your_user_id
   PASSWORD=your_password
   PORTAL_URL=https://oxygen.aptonlinetest.co.in/hurricane
   MODEL_NAME=gemini-2.5-pro
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

### Docker Setup

1. **Setup environment file (linux)**
   ```bash
   cp .env.sample .env
   # Edit .env with your actual credentials
   ```
   **Setup environment file (windows)**
   ```bash
   copy .env.sample .env
   # Edit .env with your actual credentials
   ```

2. **Build the Docker image**
   ```bash
   docker build -t eec-test-solver .
   ```

3. **run with environment variables**
   ```bash
   docker run -it -e GEMINI_API_KEY="your_api_key" \
              -e USER_ID="your_user_id" \
              -e PASSWORD="your_password" \
              eec-test-solver
   ```

5. **Or run with environment file**
   ```bash
   docker run -it --env-file .env eec-test-solver
   ```

## Configuration

The application can be configured through:

1. **Environment Variables** (recommended for Docker):
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `USER_ID` - Test portal username
   - `PASSWORD` - Test portal password
   - `PORTAL_URL` - Test portal URL (optional)
   - `MODEL_NAME` - Gemini model to use (optional)

2. **config.py file** (for local development):
   ```python
   class Config:
       GEMINI_API_KEY = "your_gemini_api_key"
       USER_ID = "your_user_id"
       PASSWORD = "your_password"
       PORTAL_URL = "https://oxygen.aptonlinetest.co.in/hurricane"
       MODEL_NAME = "gemini-2.5-pro"
   ```

## How It Works

1. **Authentication**: Logs into the test portal using provided credentials
2. **Test Detection**: Checks if test is already completed
3. **Question Processing**: For each question:
   - Extracts question text and options
   - Sends to Gemini AI for analysis
   - Receives structured JSON response with answer and explanation
   - Selects the recommended option
4. **Navigation**: Automatically moves through all questions
5. **Completion**: Submits the test when all questions are answered

## Security Considerations

- **API Keys**: Never commit API keys to version control
- **Credentials**: Use environment variables for sensitive data
- **Rate Limiting**: Built-in retry mechanisms handle API rate limits

## Logging

The application provides comprehensive logging:
- Question processing status
- AI model responses
- Browser automation actions
- Error handling and retries

## Troubleshooting

### Common Issues

1. **Browser Installation**
   ```bash
   playwright install chromium
   playwright install-deps chromium
   ```

2. **Permission Errors in Docker**
   ```bash
   # Ensure proper file permissions
   chmod +x main.py
   ```

3. **API Rate Limits**
   - The application automatically retries with exponential backoff
   - Adjust delay in `safe_generate` function if needed

### Debug Mode

Enable detailed logging by modifying the logger configuration in `logger.py`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License

Copyright (c) 2025 Sasikanth-JK

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Disclaimer

This tool is designed for educational and testing purposes. Users are responsible for complying with their institution's academic integrity policies and the terms of service of the testing platform.