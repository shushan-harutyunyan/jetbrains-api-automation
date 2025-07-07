"""
Test Cases for JetBrains Account API Testing - Change License Team
/customer/licenses/change-team endpoint
"""
import pytest
import pytest_check as check
import random
from config.api_config import status_codes, config, error_codes


class TestChangeLicenseTeam:
    """Test suite for license team change functionality"""
        
    @pytest.fixture
    def valid_test_data(self, request, test_setup):
        source_team_name, target_team_name, license_count = request.param
        source_team_id = config.TEAM_IDS[source_team_name]
        target_team_id = config.TEAM_IDS[target_team_name]
        
        # Get all available licenses from source team
        available_licenses = test_setup.license_client.get_available_licenses(team_id=str(source_team_id))
        
        # Select specified number of license IDs
        if len(available_licenses) < license_count:
            pytest.skip(f"Not enough available licenses in {source_team_name}. Required: {license_count}, Available: {len(available_licenses)}")
        
        random_license_ids = random.sample(available_licenses, license_count)
        
        test_data = {
            "license_ids": random_license_ids,
            "target_team_id": str(target_team_id),
        }
        return test_data
    
    @pytest.mark.positive
    @pytest.mark.license_team_change
    @pytest.mark.parametrize("valid_test_data", [
        ("Team 1", "Team 2", 3),
        ("Team 2", "Team 1", 2),
    ], indirect=True, ids=["Team 1 to Team 2 (3 licenses)", "Team 2 to Team 1 (2 licenses)"])
    def test_change_license_team_valid_data(self, valid_test_data, test_setup):
        """
        Test Case: Change team for licenses with valid data
        
        Expected Result: Team change should be successful
        Status Code: 200
        """
        response = test_setup.license_client.change_license_team(
            license_ids=valid_test_data["license_ids"],
            target_team_id=valid_test_data["target_team_id"]
        )
        
        check.equal(response.status_code, status_codes.OK, f"Expected successful response, got {response.status_code}")
        
        response_data = response.json()
        check.is_in("licenseIds", response_data, "Response should contain 'licenseIds' field")
        check.is_instance(response_data["licenseIds"], list, "licenseIds should be a list")
        check.equal(set(response_data["licenseIds"]), set(valid_test_data["license_ids"]), 
                   f"Response licenseIds should match input license IDs")

    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.license_team_change
    @pytest.mark.parametrize("target_team", [
        "Team 1", 
        "Team 2"])
    def test_change_license_team_empty_license_list(self, target_team, test_setup):
        """
        Test Case: Change team with empty license list

        Expected Result: Request should be successful
        Status Code: 200
        """
        # Suggestion: Request could be rejected with 400 Bad Request

        response = test_setup.license_client.change_license_team(
            license_ids=[],
            target_team_id=config.TEAM_IDS[target_team]
        )
        # Suggestion: Validation could be added for empty license list
        # check.equal(response.status_code, status_codes.BAD_REQUEST, f"Expected {status_codes.BAD_REQUEST} for empty license list")

        expected_response_data = {"licenseIds": []}
        check.equal(response.status_code, status_codes.OK, f"Expected {status_codes.OK} for empty license list")
        error_data = response.json()
        check.equal(expected_response_data, error_data, f"Expected {expected_response_data}, got {error_data}")

    @pytest.mark.negative
    @pytest.mark.license_team_change
    def test_change_license_team_invalid_target_team(self, available_license_id, test_setup):
        """
        Test Case: Change team with invalid target team

        Expected Result: Request should be rejected with 404 Not Found
        Status Code: 404
        """
        target_team_id = test_setup.test_data.generate_invalid_team_id()
        
        response = test_setup.license_client.change_license_team(
            license_ids=[available_license_id], 
            target_team_id=target_team_id
        )
        check.equal(response.status_code, status_codes.NOT_FOUND, f"Expected {status_codes.NOT_FOUND} for invalid target team")
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.TEAM_NOT_FOUND["code"], f"Expected {error_codes.TEAM_NOT_FOUND['code']} code, got {error_data.get('code')}")
        check.equal(error_data["description"], str(target_team_id), f"Expected {target_team_id} description, got {error_data.get('description')}")

    @pytest.mark.negative
    @pytest.mark.authorization
    @pytest.mark.license_team_change
    @pytest.mark.parametrize("test_setup", ["unauthorized_license_client"], indirect=True)
    def test_change_license_team_missing_authorization(self, available_license_id, test_setup, random_team_id):
        """
        Test Case: Change license team without proper authentication
        
        Expected Result: Request should be rejected with 401 Unauthorized
        Status Code: 401
        """
        response = test_setup.license_client.change_license_team(
            license_ids=[available_license_id],
            target_team_id=random_team_id
        )
        check.equal(response.status_code, status_codes.UNAUTHORIZED, f"Expected {status_codes.UNAUTHORIZED} for unauthorized request")
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.MISSING_TOKEN_HEADER["code"], f"Expected {error_codes.MISSING_TOKEN_HEADER['code']} code, got {error_data.get('code')}")
        check.equal(error_data["description"], error_codes.MISSING_TOKEN_HEADER["description"], f"Expected {error_codes.MISSING_TOKEN_HEADER['description']} description, got {error_data.get('description')}")

    @pytest.mark.negative
    @pytest.mark.authorization
    @pytest.mark.license_team_change
    @pytest.mark.parametrize("test_setup", ["invalid_api_key_license_client"], indirect=True)
    def test_change_license_team_invalid_authorization(self, available_license_id, test_setup, random_team_id):
        """
        Test Case: Change license team with invalid API key
        
        Expected Result: Request should be rejected with 401 Unauthorized
        Status Code: 401
        """
        response = test_setup.license_client.change_license_team(
            license_ids=[available_license_id],
            target_team_id=random_team_id
        )
        
        check.equal(response.status_code, status_codes.UNAUTHORIZED, f"Expected {status_codes.UNAUTHORIZED} for invalid API key")
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.INVALID_TOKEN["code"], f"Expected {error_codes.INVALID_TOKEN['code']} code, got {error_data.get('code')}")
        check.equal(error_data["description"], error_codes.INVALID_TOKEN["description"], f"Expected {error_codes.INVALID_TOKEN['description']} description, got {error_data.get('description')}")
