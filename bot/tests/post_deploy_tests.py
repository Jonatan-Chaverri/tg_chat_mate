from os import getenv

import pytest
import requests


class TestFileStoring:

    DOMAIN = getenv("DOMAIN")
    USER_NAME = "root"
    PASSWORD = getenv("ROOT_PASSWORD", "empty-password")

    @staticmethod
    @pytest.fixture(scope="module")
    def access_token():
        auth_endpoint_url = f"https://{TestFileStoring.DOMAIN}/tg-bot/login"
        payload = {
            "user_name": TestFileStoring.USER_NAME,
            "password": TestFileStoring.PASSWORD,
        }
        response = requests.post(auth_endpoint_url, json=payload, verify=False)
        assert (
            response.status_code == 200
        ), "Valid credentials should be accepted"
        token = response.json()["token"]
        return token

    def test_upload_file_to_db_without_duplicate(self, access_token):
        with open("tests/test_data/api-svgrepo-com.svg", "rb") as f:
            file_data = f.read()

        headers = {
            "Content-Type": "application/octet-stream",
            "X-Filename": "api-svgrepo-com.svg",
            "AuthorizationToken": access_token,
        }

        url = f"https://{self.DOMAIN}/tg-bot/file_upload"
        response = requests.post(
            url, headers=headers, data=file_data, verify=False
        )
        assert response.status_code == 201, "Wrong status code on file upload"
        assert (
            "file_id" in response.json().keys()
        ), "file_id is not in response"
        file_id = response.json()["file_id"]

        # Trying to upload same file again to get same id
        response = requests.post(
            url, headers=headers, data=file_data, verify=False
        )
        assert response.status_code == 201, "Wrong status code on file upload"
        assert (
            "file_id" in response.json().keys()
        ), "file_id is not in response"
        assert (
            file_id == response.json()["file_id"]
        ), "file_id changed for same file"

        # Checking what file exists
        url = f"https://{self.DOMAIN}/tg-bot/file?file_uuid={file_id}"
        response = requests.get(url, verify=False)
        assert response.status_code == 200, "Can't find uploaded file!"


class TestLogin:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        self.DOMAIN = getenv("DOMAIN")
        self.USER_NAME = "root"
        self.PASSWORD = getenv("ROOT_PASSWORD", "empty-password")

    def test_check_login_page(self):
        login_url = f"https://{self.DOMAIN}/login"
        response = requests.get(login_url, verify=False)
        assert response.status_code == 200, "Login page is not accessible"

    def test_try_to_fail_get_token(self):
        auth_endpoint_url = f"https://{self.DOMAIN}/tg-bot/login"
        payload = {
            "user_name": self.USER_NAME,
            "password": self.PASSWORD + "?>asfl",
        }
        response = requests.post(auth_endpoint_url, json=payload, verify=False)
        assert (
            response.status_code == 401
        ), "Invalid credentials should not be accepted"

    def test_try_to_get_token(self):
        auth_endpoint_url = f"https://{self.DOMAIN}/tg-bot/login"
        payload = {"user_name": self.USER_NAME, "password": self.PASSWORD}
        response = requests.post(auth_endpoint_url, json=payload, verify=False)
        assert (
            response.status_code == 200
        ), "Valid credentials should be accepted"
        assert "token" in response.json(), "Response should contain a token"

    def test_token_check_logic(self):
        auth_endpoint_url = f"https://{self.DOMAIN}/tg-bot/login"
        payload = {"user_name": self.USER_NAME, "password": self.PASSWORD}
        response = requests.post(auth_endpoint_url, json=payload, verify=False)
        assert (
            response.status_code == 200
        ), "Valid credentials should be accepted"
        token = response.json()["token"]

        check_token_endpoint = f"https://{self.DOMAIN}/tg-bot/check_token"
        check_token_payload = {"token": token}
        response = requests.post(
            check_token_endpoint, json=check_token_payload, verify=False
        )
        assert (
            response.status_code == 200
        ), "Valid credentials should be accepted"
        assert response.json().get("manager") == self.USER_NAME

    def test_wrong_token_check_logic(self):
        wrong_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"

        check_token_endpoint = f"https://{self.DOMAIN}/tg-bot/check_token"
        check_token_payload = {"token": wrong_token}
        response = requests.post(
            check_token_endpoint, json=check_token_payload, verify=False
        )
        assert (
            response.status_code == 401
        ), "Valid credentials should be accepted"