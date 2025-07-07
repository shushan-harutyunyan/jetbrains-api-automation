"""
Shared pytest fixtures for all test suites
"""
import sys
from pathlib import Path
import time
import random

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from utils.api_client import LicenseAPIClient
from config.api_config import config
from utils.test_helpers import test_data_generator


@pytest.fixture()
def available_license_id():
    try:
        license_client = LicenseAPIClient()
        license_id = license_client.get_available_license()
        return license_id
    except IndexError:
        error_msg = "Failed to access license from list - list appears to be empty"
        pytest.skip(error_msg)
    except Exception as e:
        error_msg = f"Failed to get available license: {str(e)}"
        pytest.fail(error_msg)


@pytest.fixture()
def available_licenses_from_team(request):
    # Usage: @pytest.mark.parametrize("available_licenses_from_team", [(team_id, count)], indirect=True)
    try:
        team_id, license_count = request.param
        license_client = LicenseAPIClient()
        
        available_licenses = license_client.get_available_licenses(team_id=str(team_id))
        
        if len(available_licenses) < license_count:
            pytest.skip(f"Not enough available licenses in team {team_id}. Required: {license_count}, Available: {len(available_licenses)}")
        
        selected_licenses = available_licenses[:license_count]
        return selected_licenses
        
    except (ValueError, TypeError) as e:
        error_msg = f"Invalid parameters for available_licenses_from_team: {request.param}. Expected (team_id, license_count)"
        pytest.fail(error_msg)
    except IndexError:
        error_msg = f"Failed to access licenses from team {team_id} - list appears to be empty"
        pytest.skip(error_msg)
    except Exception as e:
        error_msg = f"Failed to get available licenses from team {team_id}: {str(e)}"
        pytest.fail(error_msg)


@pytest.fixture()
def random_team_id():
    return random.choice(list(config.TEAM_IDS.values()))


@pytest.fixture()
def license_client():
    license_client = LicenseAPIClient()
    return license_client

@pytest.fixture()
def unauthorized_license_client():
    license_client = LicenseAPIClient()
    license_client.session.headers = {}
    return license_client

@pytest.fixture()
def invalid_api_key_license_client():
    license_client = LicenseAPIClient()
    license_client.session.headers.update({"X-Api-Key": "invalid_api_key_12345"})
    return license_client


@pytest.fixture()
def test_setup(request, license_client, unauthorized_license_client, invalid_api_key_license_client):
    # Usage: @pytest.mark.parametrize("test_setup", ["license_client", "unauthorized_license_client"], indirect=True)
    class TestSetup:
        def __init__(self, client_type="license_client", license_client=None, unauthorized_license_client=None, invalid_api_key_license_client=None):
            self.test_data = test_data_generator
            
            # Create the appropriate client based on parameter
            if client_type == "license_client":
                self.license_client = license_client
            elif client_type == "unauthorized_license_client":
                self.license_client = unauthorized_license_client
            elif client_type == "invalid_api_key_license_client":
                self.license_client = invalid_api_key_license_client
            else:
                raise ValueError(f"Unknown client_type: {client_type}. Valid options: 'license_client', 'unauthorized_license_client', 'invalid_api_key_license_client'")
    
    # Get client type from parameter, default to "license_client"
    client_type = getattr(request, 'param', 'license_client')
    return TestSetup(client_type, license_client, unauthorized_license_client, invalid_api_key_license_client)


@pytest.fixture(autouse=True)
def auto_test_logging():
    test_start = time.time()
    yield
    test_end = time.time()
    print(f"⏱️  Test completed in {test_end - test_start:.2f}s")