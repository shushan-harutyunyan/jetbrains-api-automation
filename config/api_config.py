"""
JetBrains Account API Testing Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class APIConfig:
    """ API Configuration for JetBrains Account API Testing"""
    
    BASE_URL: str = "https://account.jetbrains.com/api/v1"
    
    API_KEY: str = os.getenv("JETBRAINS_API_KEY", "")
    CUSTOMER_CODE: str = os.getenv("JETBRAINS_CUSTOMER_CODE", "")
    
    if not API_KEY:
        raise ValueError("JETBRAINS_API_KEY environment variable is required")
    if not CUSTOMER_CODE:
        raise ValueError("JETBRAINS_CUSTOMER_CODE environment variable is required")
    
    TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1
    
    TEST_EMAIL_DOMAIN: str = "@jetbrains-test.com"
    
    TEAM_IDS: dict = {
        "Team 1": 2573297,
        "Team 2": 2717496
    }


class EndpointsConfig:
    """ API Endpoints Configuration """
    
    # License endpoints
    ASSIGN_LICENSE = "/customer/licenses/assign"
    CHANGE_LICENSE_TEAM = "/customer/changeLicensesTeam"
    GET_LICENSES = "/customer/licenses"
    REVOKE_LICENSE = "/customer/licenses/revoke"


class HTTPStatusCodes:
    """ HTTP Status codes for responses """
    
    # Success codes
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # Client error codes
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    TOO_MANY_REQUESTS = 429
    
    # Server error codes
    INTERNAL_SERVER_ERROR = 500
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class ErrorCodes:
    """API Error codes and descriptions for responses"""
    
    # Authentication errors
    MISSING_TOKEN_HEADER = {
        "code": "MISSING_TOKEN_HEADER",
        "description": "X-Api-Key header is required"
    }
    INVALID_TOKEN = {
        "code": "INVALID_TOKEN",
        "description": "The token provided is invalid"
    }
    
    # Validation errors
    INVALID_CONTACT_EMAIL = {
        "code": "INVALID_CONTACT_EMAIL",
        "description": None
    }
    
    
    # License errors
    LICENSE_NOT_FOUND = {
        "code": "LICENSE_NOT_FOUND",
        "description": None
    }
    LICENSE_IS_NOT_AVAILABLE_TO_ASSIGN = {
        "code": "LICENSE_IS_NOT_AVAILABLE_TO_ASSIGN",
        "description": "ALLOCATED"
    }
    
    
    # Team errors
    TEAM_NOT_FOUND = {
        "code": "TEAM_NOT_FOUND",
        "description": None
    }

config = APIConfig()
endpoints = EndpointsConfig()
status_codes = HTTPStatusCodes()
error_codes = ErrorCodes() 