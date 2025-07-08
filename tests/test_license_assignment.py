"""
Test Cases for JetBrains Account API Testing - License Assignment
/customer/licenses/assign endpoint
"""
import pytest
import pytest_check as check


from config.api_config import status_codes, error_codes
from utils.test_helpers import test_data_generator


class TestLicenseAssignment:
    """Test suite for license assignment functionality"""
        
    @pytest.fixture()
    def valid_test_data(self, available_license_id):
        #Usage: @pytest.mark.parametrize("valid_test_data", [("Team 1", "Team 2", 3), ("Team 2", "Team 1", 2)], indirect=True)
        try:
            user_data = test_data_generator.generate_user_data()
            valid_test_data = {
                "licenseId": available_license_id,
                "email": user_data.get("email"),
                "firstName": user_data.get("firstName"),
                "lastName": user_data.get("lastName")
            }
            return valid_test_data
    # Could be:        
    #     yield test_data
    
    #     try:
    #         license_client.revoke_license(test_data["licenseId"])
    #         print(f"Revoked license: {test_data['licenseId']}")
    #     except Exception as e:
    #         print(f"Failed to revoke license: {e}")    
        except Exception as e:
            error_msg = f"Failed to create valid test data: {str(e)}"
            pytest.fail(error_msg)

    @pytest.mark.positive
    @pytest.mark.license_assignment
    def test_assign_license_valid_user_data(self, valid_test_data, license_client):
        """
        Test Case: Assign license with valid user data

        Expected Result: License should be assigned successfully

        Expected Status Code: 200
        """
        response = license_client.assign_license(
            email=valid_test_data["email"],
            first_name=valid_test_data["firstName"],
            last_name=valid_test_data["lastName"],
            license_id=valid_test_data["licenseId"],
            send_email = False
        )
        # Suggestion: Return a response confirming the assignment was successful
        check.is_true(response.status_code == status_codes.OK, f"Expected successful response, got {response.status_code}")
        check.is_true(len(response.text.strip()) == 0, "Empty response body expected for successful operation")

    @pytest.mark.negative
    @pytest.mark.license_assignment
    @pytest.mark.parametrize("invalid_email", test_data_generator.generate_invalid_email_addresses())
    def test_assign_license_invalid_email_formats(self, valid_test_data, invalid_email, license_client):
        """
        Test Case: Assign license with invalid email formats

        Expected Result: Request should be rejected with appropriate error

        Status Code: 400
        """
        
        response = license_client.assign_license(
            email=invalid_email,
            first_name=valid_test_data["firstName"],
            last_name=valid_test_data["lastName"],
            license_id=valid_test_data["licenseId"],
            send_email=False
        )
        
        check.equal(response.status_code, status_codes.BAD_REQUEST, f"Expected 400 Bad Request, got {response.status_code}")
        
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.INVALID_CONTACT_EMAIL["code"], f"Expected INVALID_CONTACT_EMAIL error, got {error_data.get('code')})")
        check.is_in("description", error_data, "Error response should contain 'description' field")
        check.equal(error_data["description"], invalid_email, f"Expected {invalid_email}, got {error_data.get('description')})")
    
    @pytest.fixture()
    def data_with_empty_field(self, valid_test_data, request):
        #Usage: @pytest.mark.parametrize("data_with_empty_field", [
        #    ("email", status_codes.BAD_REQUEST),
        #    ("firstName", status_codes.BAD_REQUEST),
        #    ("lastName", status_codes.BAD_REQUEST),
        #    ("licenseId", status_codes.NOT_FOUND),
        #], indirect=True, ids=["email", "firstName", "lastName", "licenseId"])
        empty_field_name, expected_status = request.param
        valid_test_data[empty_field_name] = ""
        return valid_test_data, empty_field_name, expected_status
    
    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.license_assignment
    @pytest.mark.parametrize("data_with_empty_field", [
        ("email", status_codes.BAD_REQUEST),
        ("firstName", status_codes.BAD_REQUEST),
        ("lastName", status_codes.BAD_REQUEST),
        ("licenseId", status_codes.NOT_FOUND),
    ], indirect=True, ids=["email", "firstName", "lastName", "licenseId"])
    def test_assign_license_empty_required_fields(self, data_with_empty_field, license_client):
        """
        Test Case: Assign license with empty required fields

        Expected Result: Request should be rejected with expected status code
        """
        test_data, empty_field_name, expected_status = data_with_empty_field

        response = license_client.assign_license(
            email=test_data["email"],
            first_name=test_data["firstName"],
            last_name=test_data["lastName"],
            license_id=test_data["licenseId"],
            send_email=False
        )
        
        check.equal(response.status_code, expected_status, 
                   f"Expected {expected_status} for empty {empty_field_name}, got {response.status_code}")

    @pytest.fixture()
    def data_with_exceeding_character_limit(self, valid_test_data, request):
        #Usage: @pytest.mark.parametrize("data_with_exceeding_character_limit", [
        #    "firstName",
        #    "lastName"
        #    ], indirect=True, ids=["firstName", "lastName"])
        exceeding_field_name = request.param
        boundary_data = test_data_generator.generate_boundary_test_data()
        very_long_strings = boundary_data.get("very_long_strings", {})
        exceeding_field_value = very_long_strings.get(exceeding_field_name, "")
        
        test_data = valid_test_data.copy()
        test_data[exceeding_field_name] = exceeding_field_value
        expected_status = status_codes.BAD_REQUEST
        expected_field_code = error_codes.INVALID_CONTACT_NAME["code"]
        expected_description = "Value is too long."
        return test_data, exceeding_field_name, expected_field_code, expected_description, expected_status
    
    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.license_assignment
    @pytest.mark.parametrize("data_with_exceeding_character_limit", [
        "firstName",
        "lastName"
        ], indirect=True, ids=["firstName", "lastName"])
    def test_assign_license_exceeding_character_limit_fields(self, data_with_exceeding_character_limit, license_client):
        """
        Test Case: Assign license with very long field value

        Expected Result: Should reject long field value with appropriate error code and description
        """
        test_data, exceeding_field_name, expected_field_code, expected_description, expected_status = data_with_exceeding_character_limit
        
        response = license_client.assign_license(
            email=test_data["email"],
            first_name=test_data["firstName"],
            last_name=test_data["lastName"],
            license_id=test_data["licenseId"],
            send_email=False
        )
        check.equal(response.status_code, expected_status, f"Expected {expected_status} for {exceeding_field_name} field exceeding character limit, got {response.status_code}")
        error_data = response.json()
        check.equal(error_data["code"], expected_field_code, f"Expected {expected_field_code} for {exceeding_field_name} field exceeding character limit, got {response.json()['code']}")
        check.equal(error_data["description"], expected_description, f"Expected {expected_description} for {exceeding_field_name} field exceeding character limit, got {response.json()['description']}")

    @pytest.fixture()
    def data_with_special_character_in_fields(self, valid_test_data, request):
        #Usage: @pytest.mark.parametrize("data_with_special_character_in_fields", [
        #    "firstName",
        #    "lastName"
        #    ], indirect=True, ids=["firstName", "lastName"])
        field_name = request.param
        boundary_data = test_data_generator.generate_boundary_test_data()
        special_characters = boundary_data.get("special_characters", {})
        field_value = special_characters.get(field_name, "")
        
        #test_data = valid_test_data.copy()
        valid_test_data[field_name] = field_value
        expected_status = status_codes.BAD_REQUEST
        expected_field_code = error_codes.INVALID_CONTACT_NAME["code"]
        expected_description = "Please, don't use special characters."
        return valid_test_data, field_name, expected_field_code, expected_description, expected_status
    
    @pytest.mark.negative
    @pytest.mark.boundary
    @pytest.mark.license_assignment
    @pytest.mark.parametrize("data_with_special_character_in_fields", [
        "firstName",
        "lastName"
        ], indirect=True, ids=["firstName", "lastName"])    
    def test_assign_license_special_characters_in_fields(self, data_with_special_character_in_fields, license_client):
        """
        Test Case: Assign license with special characters in fields

        Expected Result: Should reject special characters with appropriate error code and description
        """
        test_data, field_name, expected_field_code, expected_description, expected_status = data_with_special_character_in_fields
        
        response = license_client.assign_license(
            email=test_data["email"],
            first_name=test_data["firstName"],
            last_name=test_data["lastName"],
            license_id=test_data["licenseId"],
            #send_email=False
        )
        check.equal(response.status_code, expected_status, f"Expected {expected_status} for {field_name} field with special characters, got {response.status_code}")
        error_data = response.json()
        check.equal(error_data["code"], expected_field_code, f"Expected {expected_field_code} for {field_name} field with special characters, got {response.json()['code']}")
        check.equal(error_data["description"], expected_description, f"Expected {expected_description} for {field_name} field with special characters, got {response.json()['description']}")

    @pytest.mark.negative
    @pytest.mark.authorization
    @pytest.mark.license_assignment
    def test_assign_license_missing_authorization(self, valid_test_data, unauthorized_license_client):
        """
        Test Case: Assign license without proper authentication

        Expected Result: Request should be rejected with 401 Unauthorized

        Status Code: 401
        """
        response = unauthorized_license_client.assign_license(
            email=valid_test_data["email"],
            first_name=valid_test_data["firstName"],
            last_name=valid_test_data["lastName"],
            license_id=valid_test_data["licenseId"],
            send_email=False
        )
        check.equal(response.status_code, status_codes.UNAUTHORIZED, f"Expected {status_codes.UNAUTHORIZED} status, got {response.status_code}")
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.MISSING_TOKEN_HEADER["code"], f"Expected {error_codes.MISSING_TOKEN_HEADER['code']} code, got {error_data.get('code')}")
        check.equal(error_data["description"], error_codes.MISSING_TOKEN_HEADER["description"], f"Expected {error_codes.MISSING_TOKEN_HEADER['description']} description, got {error_data.get('description')}")

    @pytest.mark.negative
    @pytest.mark.authorization
    @pytest.mark.license_assignment
    def test_assign_license_invalid_authorization(self, valid_test_data, invalid_api_key_license_client):
        """
        Test Case: Assign license with invalid API key

        Expected Result: Request should be rejected with 401 Unauthorized

        Status Code: 401
        """
        response = invalid_api_key_license_client.assign_license(
            email=valid_test_data["email"],
            first_name=valid_test_data["firstName"],
            last_name=valid_test_data["lastName"],
            license_id=valid_test_data["licenseId"],
            send_email=False
        )
        check.equal(response.status_code, status_codes.UNAUTHORIZED, f"Expected {status_codes.UNAUTHORIZED} status, got {response.status_code}")
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.INVALID_TOKEN["code"], f"Expected {error_codes.INVALID_TOKEN['code']} code, got {error_data.get('code')}")
        check.equal(error_data["description"], error_codes.INVALID_TOKEN["description"], f"Expected {error_codes.INVALID_TOKEN['description']} description, got {error_data.get('description')}")

    @pytest.mark.negative
    @pytest.mark.license_assignment
    def test_assign_license_invalid_license_id(self, valid_test_data, license_client):
        """
        Test Case: Assign license with invalid license ID

        Expected Result: Request should be rejected with 404 Not Found

        Status Code: 404
        """
        invalid_license_id = test_data_generator.generate_invalid_license_id()
        
        response = license_client.assign_license(
            email=valid_test_data["email"],
            first_name=valid_test_data["firstName"],
            last_name=valid_test_data["lastName"],
            license_id=invalid_license_id,
            send_email=False
        )
        
        check.equal(response.status_code, status_codes.NOT_FOUND, f"Expected {status_codes.NOT_FOUND} status, got {response.status_code}")
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.LICENSE_NOT_FOUND["code"], f"Expected {error_codes.LICENSE_NOT_FOUND['code']} code, got {error_data.get('code')}")
        check.equal(error_data["description"], invalid_license_id, f"Expected {invalid_license_id} description, got {error_data.get('description')}")

    @pytest.mark.negative
    @pytest.mark.license_assignment
    def test_assign_license_invalid_json(self, license_client):
        """
        Test Case: Send invalid JSON in request body

        Expected Result: Request should be rejected with 400 Bad Request

        Status Code: 400
        """
        invalid_json = test_data_generator.generate_invalid_json()
        
        response = license_client.assign_license(raw_json=invalid_json)
        
        check.equal(response.status_code, status_codes.BAD_REQUEST, f"Expected {status_codes.BAD_REQUEST} status, got {response.status_code}")
        
    
    @pytest.mark.negative
    @pytest.mark.license_assignment
    def test_assign_license_duplicate_assignment(self, valid_test_data, license_client):
        """
        Test Case: Assign an already assigned license to a different user

        Expected Result: Request should be rejected with 400 Bad Request
        
        Status Code: 400
        """
        
        # Get an already assigned license ID
        try:
            assigned_license_id = license_client.get_assigned_license()
        except Exception as e:
            pytest.skip(f"No assigned licenses available for duplicate test: {str(e)}")
        
        # Try to assign it to a different user
        response = license_client.assign_license(
            email=valid_test_data["email"],
            first_name=valid_test_data["firstName"],
            last_name=valid_test_data["lastName"],
            license_id=assigned_license_id,
            send_email=False
        )
        
        check.equal(response.status_code, status_codes.BAD_REQUEST, f"Expected {status_codes.BAD_REQUEST} for duplicate assignment, got {response.status_code}")
        error_data = response.json()
        check.is_in("code", error_data, "Error response should contain 'code' field")
        check.equal(error_data["code"], error_codes.LICENSE_IS_NOT_AVAILABLE_TO_ASSIGN["code"], f"Expected {error_codes.LICENSE_IS_NOT_AVAILABLE_TO_ASSIGN['code']} code, got {error_data.get('code')}")
        check.equal(error_data["description"], error_codes.LICENSE_IS_NOT_AVAILABLE_TO_ASSIGN["description"], f"Expected {error_codes.LICENSE_IS_NOT_AVAILABLE_TO_ASSIGN['description']} description, got {error_data.get('description')}")
