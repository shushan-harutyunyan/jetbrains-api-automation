# JetBrains Account API Automation Framework

## Overview

This is a comprehensive QA automation framework for JetBrains Account API testing, implemented in **Python** using modern testing practices and tools. The framework provides robust testing capabilities for license management and team administration APIs.

## Features

### Core Capabilities
- **Comprehensive API Testing**: Full coverage of positive, negative, and boundary test cases
- **Robust HTTP Client**: Built on requests with retry mechanisms, proper error handling, and automatic retries
- **Environment Variable Configuration**: Secure configuration management with python-dotenv support
- **Modern Testing Framework**: pytest with parallel execution support and automatic test timing
- **Advanced Test Data Generation**: Faker-based test data with boundary value testing
- **Detailed Reporting**: HTML and JSON test reports with comprehensive results
- **Soft Assertions**: pytest-check for multiple assertions per test without early failures

### Test Coverage
- **License Assignment API** (`/customer/licenses/assign`)
  - Positive scenarios: Valid license assignment without email notification
  - Negative scenarios: Invalid fields, missing fields, authentication errors
  - Boundary testing: Very long names, special characters
  - Edge cases: Duplicate assignments, malformed JSON

- **Change License Team API** (`/customer/changeLicensesTeam`)
  - Positive scenarios: Valid team changes with proper license IDs
  - Negative scenarios: Invalid license IDs, non-existent teams, empty lists

## Setup Instructions

### 1. Environment Setup
```bash
# Clone the repository (choose one option)

# Option A: HTTPS (works everywhere, may require authentication)
git clone https://github.com/shushan-harutyunyan/jetbrains-api-automation.git

# Option B: SSH (requires SSH key setup, no password prompts)
git clone git@github.com:shushan-harutyunyan/jetbrains-api-automation.git

# Navigate to project directory
cd jetbrains-api-automation

# Note: For SSH cloning, ensure you have SSH keys configured:
# https://docs.github.com/en/authentication/connecting-to-github-with-ssh

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

**Option A: Copy template file (recommended)**
```bash
# Copy the template file
cp .env.example .env

# Edit .env file with your actual values
# JETBRAINS_API_KEY=your_actual_api_key_here
# JETBRAINS_CUSTOMER_CODE=your_actual_customer_code_here
```

**Option B: Create .env file manually**
```bash
# Create .env file with your actual values
cat > .env << EOF
JETBRAINS_API_KEY=your_actual_api_key_here
JETBRAINS_CUSTOMER_CODE=your_actual_customer_code_here
DEBUG=false
EOF
```

**Option C: Export in shell**
```bash
export JETBRAINS_API_KEY="your_actual_api_key_here"
export JETBRAINS_CUSTOMER_CODE="your_actual_customer_code_here"
```

**Option D: Set when running tests**
```bash
JETBRAINS_API_KEY="your_key" JETBRAINS_CUSTOMER_CODE="your_code" python -m pytest
```

### 3. Run Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_license_assignment.py

# Run with verbose output
python -m pytest -v

# Run with parallel execution
python -m pytest -n auto
```

## Project Structure

```
jetbrains-api-automation/
├── config/
│   └── api_config.py             # API configuration and constants
├── utils/
│   ├── api_client.py             # HTTP client with auth & retry
│   └── test_helpers.py           # Test utilities and data generators
├── tests/
│   ├── conftest.py               # pytest fixtures and configuration
│   ├── test_license_assignment.py # License assignment tests
│   └── test_change_license_team.py # License team change tests
├── logs/                         # Test execution logs
├── reports/                      # Test reports
├── requirements.txt              # Python dependencies
├── pytest.ini                   # pytest configuration
├── run_tests.py                  # Test runner script
└── README.md                     # This file
```


## Running Tests

### Basic Test Execution
```bash
# Run all tests
python -m pytest

# Run tests with detailed output
python -m pytest -v -s

# Run tests in parallel
python -m pytest -n auto
```

### Test Selection
```bash
# Run license assignment tests only
python -m pytest tests/test_license_assignment.py

# Run team change tests only
python -m pytest tests/test_change_license_team.py

# Run specific test method
python -m pytest tests/test_file.py::TestClass::test_method_name -v
```

### Test Reports
```bash
# Generate HTML report
python -m pytest --html=reports/report.html --self-contained-html

# JSON reports are automatically generated (configured in pytest.ini)
```

## Dependencies

### Core Dependencies
- **pytest**: Main testing framework
- **requests**: HTTP client for API calls
- **python-dotenv**: Environment variable management
- **faker**: Test data generation

### Testing Enhancement
- **pytest-check**: Soft assertions (multiple assertions per test)
- **pytest-xdist**: Parallel test execution
- **pytest-html**: HTML test reports
- **pytest-json-report**: JSON test reports


### Environment Variables
- `JETBRAINS_API_KEY`: Your JetBrains API key (required)
- `JETBRAINS_CUSTOMER_CODE`: Your customer code (required)
- `DEBUG`: Set to 'true' for verbose logging (optional)

### Key Features
- **Automatic test timing**: Each test shows execution duration
- **Parametrized fixtures**: Flexible client configurations
- **Retry logic**: Automatic retries for rate limiting and server errors
- **Clean error handling**: Proper exception handling and reporting
