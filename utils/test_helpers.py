"""
Test Helper Utils for JetBrains Account API Testing
"""
import random
import string
import uuid
from typing import Dict, Any, List, Optional

from config.api_config import config
from faker import Faker


class TestDataGenerator:
    """ Generate test data """
    
    def __init__(self, use_seed=False):
        self.fake = Faker()
        if use_seed:
            Faker.seed(42)
    
    def generate_email(self, prefix: Optional[str] = None) -> str:
        
        if prefix:
            username = f"{prefix}_{uuid.uuid4().hex[:8]}"
        else:
            username = f"test_{uuid.uuid4().hex[:8]}"
        
        return f"{username}{config.TEST_EMAIL_DOMAIN}"
    
    def generate_user_data(self) -> Dict[str, str]:
        
        return {
            "email": self.generate_email(),
            "firstName": self.fake.first_name(),
            "lastName": self.fake.last_name()
        }
    

    
    def generate_invalid_email_addresses(self) -> List[str]:
        
        return [
            "",  # Empty string
            "invalid-email",  # No @ symbol
            "@domain.com",  # Missing username
            "user@",  # Missing domain
            "user@.com",  # Empty domain name
            "user@domain",  # Missing TLD
            "user name@domain.com",  # Space in username
            "user@domain .com",  # Space in domain
            "user@@domain.com",  # Double @
            "user@domain..com",  # Double dot
            "user@",  # Incomplete
            "user@domain,com",  # Comma instead of dot
            "very-long-email-address-that-exceeds-normal-limits@very-long-domain-name-that-should-not-be-accepted.com",  # Too long
            "user@domain.c",  # TLD too short
            "user@-domain.com",  # Domain starts with hyphen
            "user@domain-.com",  # Domain ends with hyphen
        ]
    
    def generate_boundary_test_data(self) -> Dict[str, Any]:
        
        return {
            
            "very_long_strings": {
                "firstName": "a" * 500,
                "lastName": "b" * 500
            },
            "special_characters": {
                "firstName": "Special@#$%^&*()",
                "lastName": "Chars!@#$%^&*()"
            }
        }
    
    def generate_invalid_license_id(self) -> str:
        #10-character random alphanumeric string

        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    def generate_invalid_team_id(self) -> int:
        # a random integer up to 7 digits

        existing_team_ids = set(config.TEAM_IDS.values())
        
        max_attempts = 100 
        for _ in range(max_attempts):
            team_id = random.randint(1, 9999999)
            if team_id not in existing_team_ids:
                return team_id
        raise ValueError("Failed to generate an invalid team ID")
    
    def generate_invalid_json(self) -> str:
        
        invalid_jsons = [
            '{"key": value}',  # Missing quotes around value
            '{"key": "value",}',  # Trailing comma
            '{key: "value"}',  # Missing quotes around key
            '{"key": "value"',  # Missing closing brace
            '"key": "value"}',  # Missing opening brace
            '{"key": "value" "key2": "value2"}',  # Missing comma
            '{"key": "value\\"}',  # Invalid escape
            '{"key": "value";}',  # Semicolon instead of comma
            '{"key": "value":]',  # Wrong bracket type
        ]
        return random.choice(invalid_jsons)


test_data_generator = TestDataGenerator()
