from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from tests.account.test_models import UserFactory
from tests.testutils import CustomTestCase


class LoginViewTests(CustomTestCase, APITestCase):
    def setUp(self):
        self.user = UserFactory.create()

    def test_officer_login_success(self):
        """Log a user in."""
        response = self.client.post(
            path=reverse("account_api:login"),
            data={
                "username": "shols",
                "password": "password",
            },
        )

        # Check side effects
        self.assertEqual(Token.objects.count(), 1)
        auth_token = Token.objects.first()
        self.assertEqual(auth_token.user, self.user)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(list(response.json().keys()), ["token"])

    def test_user_login_error(self):
        """Make sure invalid credentials do NOT return an auth token."""
        invalid_data_dicts = [
            {
                "method": "POST",
                "status": status.HTTP_400_BAD_REQUEST,
                "response": {
                    "username": ["This field is required."],
                    "password": ["This field is required."],
                },
                "label": "No data",
                "data": None,
            },
            {
                "method": "POST",
                "status": status.HTTP_400_BAD_REQUEST,
                "response": {"non_field_errors": ["Unable to log in with provided credentials."]},
                "label": "Invalid credentials",
                "data": {"username": "invalid", "password": "user"},
            },
        ]

        self.assert_invalid_data_response(url=reverse("account_api:login"), invalid_data_dicts=invalid_data_dicts)


class RegisterUserViewTests(CustomTestCase, APITestCase):
    def test_register_success(self):
        """Test succesful creation of Officer"""
        # No user exists.
        self.assertEqual(User.objects.count(), 0)

        # Create the user
        response = self.client.post(
            path=reverse("account_api:register"),
            data={
                "username": "levi",
                "password": "Ackerman",
            },
        )

        # confirm response status code.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Ensure it was created -- should be 1!
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(username="levi")

        # Check side effects
        self.assertEqual(Token.objects.count(), 1)
        auth_token = Token.objects.first()
        self.assertEqual(auth_token.user, user)

    def test_register_with_no_credentials_results_in_error(self):
        """Ensure registration with no details results in error."""

        # Initial assertions -- 0 Users in database.
        self.assertEqual(User.objects.count(), 0)

        # Create the officer
        response = self.client.post(
            path=reverse("account_api:register"),
            data={},
        )

        # Ensure it couldn't be created -- Should still be 0!
        self.assertEqual(User.objects.count(), 0)

        # Confirm error response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {
                "password": ["This field is required."],
                "username": ["This field is required."],
            },
        )

    def test_users_cannot_create_account_with_already_existing_username(self):
        """Ensure users can NOT register with already existing username."""
        # Create a user.
        UserFactory()  # default username is shols.

        # Initial asserions -- 1 User in database.
        self.assertEqual(User.objects.count(), 1)

        # Create another user with same username.
        response = self.client.post(
            path=reverse("account_api:register"),
            data={
                "username": "shols",
                "password": "Ymir.Fritz",
            },
        )

        # Ensure it couldn't be created due to duplicate username. -- still 1!
        self.assertEqual(User.objects.count(), 1)

        # Confirm error response.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(
            response.json(),
            {"username": ["A user with that username already exists."]},
        )
