"""
JetBrains Account API Client
"""
from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.api_config import config, endpoints, status_codes


class APIClient:
    """ JetBrains Account API Client """
    
    def __init__(self):
        """ Initialize the API client """
        self.base_url = config.BASE_URL
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """ Setup HTTP session with retry strategy """
        retry_strategy = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.RETRY_DELAY,
            status_forcelist=[
                status_codes.TOO_MANY_REQUESTS,
                status_codes.INTERNAL_SERVER_ERROR,
                status_codes.BAD_GATEWAY,
                status_codes.SERVICE_UNAVAILABLE,
                status_codes.GATEWAY_TIMEOUT
            ],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        # Create HTTP adapter with retry strategy and mount to session
        # This applies automatic retry logic to all HTTP/HTTPS requests
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "accept": "*/*",
            "X-Api-Key": config.API_KEY,
            "X-Customer-Code": config.CUSTOMER_CODE,
            "User-Agent": "JetBrains-API-Automation-Tests/1.0"
        })
    

    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> requests.Response:
        """ Make HTTP request to the API """
        url = f"{self.base_url}{endpoint}"
        
        # Merge additional headers with default headers
        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)
        
        request_kwargs = {
            'timeout': config.TIMEOUT,
            'headers': request_headers,
            **kwargs
        }
        
        if json_data:
            request_kwargs['json'] = json_data
        if params:
            request_kwargs['params'] = params
        
        try:
            response = self.session.request(method, url, **request_kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise
    
    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """ Make GET request """
        return self._make_request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """ Make POST request """
        return self._make_request("POST", endpoint, json_data=json_data, **kwargs)
    
    def put(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """ Make PUT request """
        return self._make_request("PUT", endpoint, json_data=json_data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """ Make DELETE request """
        return self._make_request("DELETE", endpoint, **kwargs)
    
    def patch(self, endpoint: str, json_data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """ Make PATCH request """
        return self._make_request("PATCH", endpoint, json_data=json_data, **kwargs)


class LicenseAPIClient(APIClient):
    """ Specialized API client for License management operations """
    
    def assign_license(
        self,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        license_id: Optional[str] = None,
        product_code: str = "II",
        send_email: bool = False,
        team_id: int = 1,
        include_offline_activation_code: bool = True,
        raw_json: Optional[str] = None
    ) -> requests.Response:
        """ Assign license to a user """
        # If raw_json is provided, send it directly
        if raw_json:
            return self.post(endpoints.ASSIGN_LICENSE, data=raw_json)
        
        # Validate required parameters when raw_json is not provided
        if any(param is None for param in [email, first_name, last_name, license_id]):
            raise ValueError("email, first_name, last_name, and license_id are required when raw_json is not provided")
        
        # Construct the normal payload
        payload = {
            "contact": {
                "email": email,
                "firstName": first_name,
                "lastName": last_name
            },
            "includeOfflineActivationCode": include_offline_activation_code,
            "license": {
                "productCode": product_code,
                "team": team_id
            },
            "licenseId": license_id,
            "sendEmail": send_email
        }
        
        return self.post(endpoints.ASSIGN_LICENSE, json_data=payload)
    
    def change_license_team(
        self,
        license_ids: list,
        target_team_id: int,
        source_team_id: Optional[int] = None
    ) -> requests.Response:
        """ Change team for licenses """
        payload = {
            "licenseIds": license_ids,
            "targetTeamId": target_team_id
        }
        
        if source_team_id:
            payload["sourceTeamId"] = source_team_id
        
        return self.post(endpoints.CHANGE_LICENSE_TEAM, json_data=payload)
    
    def get_licenses(
        self, 
        team_id: Optional[str] = None, 
        assigned: Optional[bool] = None
    ) -> requests.Response:
        """ Get licenses """
        params = {}
        if team_id:
            params["teamId"] = team_id
        if assigned is not None:
            params["assigned"] = str(assigned).lower()
        
        return self.get(endpoints.GET_LICENSES, params=params)
    
    def get_available_licenses(self, team_id: Optional[str] = None) -> list:
        """ Get list of unassigned license IDs """
        response = self.get_licenses(team_id=team_id, assigned=False)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get licenses: {response.status_code} - {response.text}")
        
        try:
            licenses_data = response.json()
            
            # response.json() returns list of dicts
            unassigned_licenses = [
                license.get('licenseId') 
                for license in licenses_data 
                if license.get('licenseId') and license.get('isAvailableToAssign', False)
            ]
            
            if not unassigned_licenses:
                raise Exception("unassigned license list is empty")
            
            return unassigned_licenses
            
        except ValueError as e:
            raise Exception(f"Failed to parse licenses response: {e}")
    
    def get_assigned_licenses(self, team_id: Optional[str] = None) -> list:
        """ Get list of assigned license IDs """
        response = self.get_licenses(team_id=team_id, assigned=True)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get licenses: {response.status_code} - {response.text}")
        
        try:
            licenses_data = response.json()
            
            # response.json() returns list of dicts
            assigned_licenses = [
                license.get('licenseId') 
                for license in licenses_data 
                if license.get('licenseId') and not license.get('isAvailableToAssign', True)
            ]
            
            if not assigned_licenses:
                raise Exception("assigned license list is empty")
            
            return assigned_licenses
            
        except ValueError as e:
            raise Exception(f"Failed to parse licenses response: {e}")

    def get_available_license(self, team_id: Optional[str] = None) -> str:
        """ Get a single available license ID """
        unassigned_licenses = self.get_available_licenses(team_id)
        available_license = unassigned_licenses[0]
        return available_license

    def get_assigned_license(self, team_id: Optional[str] = None) -> str:
        """ Get a single assigned license ID """
        assigned_licenses = self.get_assigned_licenses(team_id)
        assigned_license = assigned_licenses[0]
        return assigned_license

    def revoke_license(self, license_id: str) -> requests.Response:
        """ Revoke a license """
        payload = {"licenseId": license_id}
        return self.post(endpoints.REVOKE_LICENSE, json_data=payload)


