import os
import time
import jwt
import requests

from dotenv import load_dotenv

load_dotenv()


class GitHubAuthService:

    def __init__(self):
        self.app_id = os.getenv(
            "GITHUB_APP_ID"
        )
        private_key_path = os.getenv(
            "GITHUB_PRIVATE_KEY_PATH"
        )
        with open(private_key_path, "r") as file:
            self.private_key = file.read()

    def generate_jwt(self):
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + 600,
            "iss": self.app_id
        }
        encoded_jwt = jwt.encode(
            payload,
            self.private_key,
            algorithm="RS256"
        )
        return encoded_jwt

    def get_installation_token(
        self,
        installation_id: int
    ):
        jwt_token = self.generate_jwt()
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
        response = requests.post(
            url,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return data["token"]