from __future__ import annotations

from typing import Any, Sequence
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase


class CustomTestCase(TestCase):
    def assert_fields_required(
        self, required: bool, form: Any, list_fields: Sequence[str]
    ) -> None:
        """
        Check if a list of fields are required or not required in a form.

        :param required: True|False
        :param form: form to be checked
        :param list_fields: list of fields to check
        """
        for field in list_fields:
            if required:
                self.assertTrue(form.fields[field].required, "FIELD:%s" % field)
            else:
                self.assertFalse(form.fields[field].required, "FIELD:%s" % field)

    def assert_invalid_data(
        self,
        form: Any,
        invalid_data_dicts: Sequence[dict[str, Any]],
        instance: Any = None,
        **form_attributes: Any
    ) -> None:
        """
        Check invalid data errors in a form.

        :param form:
        :param invalid_data_dicts:
        :return:
        """
        for invalid_dict in invalid_data_dicts:
            if instance is not None:
                form_data = form(
                    instance=instance, data=invalid_dict["data"], **form_attributes
                )
            else:
                form_data = form(data=invalid_dict["data"], **form_attributes)
            self.assertFalse(form_data.is_valid())
            self.assertEqual(
                form_data.errors[invalid_dict["error"][0]],
                invalid_dict["error"][1],
                msg=invalid_dict["label"],
            )

    def assert_valid_data(
        self,
        form: Any,
        valid_data_dicts: Sequence[dict[str, Any]],
        instance: Any = None,
        **form_attributes: Any
    ) -> None:
        """
        Check valid data in a form.

        :param form:
        :param valid_data_dicts:
        :param form_attributes:
        :param instance:
        :return:
        """
        for valid_data in valid_data_dicts:
            if instance is not None:
                form_data = form(instance=instance, data=valid_data, **form_attributes)
            else:
                form_data = form(data=valid_data, **form_attributes)
            self.assertTrue(form_data.is_valid(), msg=form_data.errors)

    def assert_invalid_data_response(
        self, url: str, invalid_data_dicts: Sequence[dict[str, Any]]
    ) -> None:
        """
        Check invalid data response status.

        :param url:
        :param invalid_data_dicts:
        :return:
        """
        for invalid_dict in invalid_data_dicts:
            if invalid_dict["method"] == "POST":
                response = self.client.post(
                    url, data=invalid_dict["data"], format="json"
                )
            elif invalid_dict["method"] == "GET":
                response = self.client.get(
                    url, data=invalid_dict["data"], format="json"
                )
            error_msg = "{}-{}-{}".format(
                invalid_dict["label"], response.status_code, response.content
            )
            self.assertEqual(
                response.status_code, invalid_dict["status"], msg=error_msg
            )
            self.assertEqual(response.data, invalid_dict["response"], msg=error_msg)


class TestUtils:
    @staticmethod
    def generate_user_auth_headers(user: User) -> dict[str, str]:
        """Generate the authentication headers for a logged in partner."""
        token, _ = Token.objects.get_or_create(user=user)
        return {"HTTP_AUTHORIZATION": "Token {}".format(token)}

    @staticmethod
    def create_temp_file(image_name: str):
        print(SimpleUploadedFile(f"{image_name}", open('tests/test_image.png', 'rb').read(), content_type="image/png"))
        return SimpleUploadedFile(f"{image_name}", open('tests/test_image.png', 'rb').read(), content_type="image/png")
