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
        
        available_licenses = license_client.get_team_available_licenses(team_id=str(team_id))
        
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


@pytest.fixture(scope="session")
def license_client():
    """ Session-scoped license client for all tests"""
    license_client = LicenseAPIClient()
    return license_client
    #Could use yield to close the session after ALL tests complete:
    #yield license_client
    #license_client.session.close()

@pytest.fixture(scope="session")
def license_client_team_1():
    """ Session-scoped license client for Team 1 with team-specific API key """
    license_client = LicenseAPIClient()
    
    team_1_api_key = config.API_KEY_TEAM_1
    if not team_1_api_key:
        pytest.skip("JETBRAINS_API_KEY_TEAM_1 environment variable not set")
    
    license_client.session.headers.update({"X-Api-Key": team_1_api_key})
    return license_client

@pytest.fixture(scope="session")
def license_client_team_2():
    """ Session-scoped license client for Team 2 with team-specific API key """
    license_client = LicenseAPIClient()
    
    team_2_api_key = config.API_KEY_TEAM_2
    if not team_2_api_key:
        pytest.skip("JETBRAINS_API_KEY_TEAM_2 environment variable not set")
    
    license_client.session.headers.update({"X-Api-Key": team_2_api_key})
    return license_client    

@pytest.fixture(scope="session")
def unauthorized_license_client():
    """nSession-scoped unauthorized client """
    license_client = LicenseAPIClient()
    license_client.session.headers = {}
    return license_client

@pytest.fixture(scope="session")
def invalid_api_key_license_client():
    """ Session-scoped invalid API key client """
    license_client = LicenseAPIClient()
    license_client.session.headers.update({"X-Api-Key": "invalid_api_key_12345"})
    return license_client


@pytest.fixture(autouse=True)
def auto_test_logging():
    test_start = time.time()
    yield
    test_end = time.time()
    print(f"⏱️  Test completed in {test_end - test_start:.2f}s")