from django.contrib.auth.models import User
from tests.images.test_models import UserImageFactory
from tempfile import TemporaryDirectory
from django.test.utils import override_settings
from images.models import UserImage
from tests.account.test_models import UserFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from tests.testutils import CustomTestCase, TestUtils


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class AddImageViewTests(CustomTestCase, APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.user = UserFactory.create()

    def test_add_image_success(self):
        """Add a new image."""

        # Initial assertions
        self.assertEqual(UserImage.objects.count(), 0)
        # Create the image.
        response = self.client.post(
            path=reverse("images_api:add_image"),
            data={
                "image": TestUtils.create_temp_file("test.png"),
            },
            **TestUtils.generate_user_auth_headers(self.user),
        )
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Image was created
        self.assertEqual(UserImage.objects.count(), 1)

        # Check response
        self.assertEqual(
            response.json(),
            [
                {
                    "owner": "shols",
                    "name": "test.png",
                    "image": "/media/test.png",
                    "times_shared": 0,
                    "size": 1049,
                }
            ],
        )

    def test_add_image_with_wrong_extension_results_in_failure(self):
        """Ensure attempt to add a new image with unrecognized file extension results in error."""

        # Initial assertions
        self.assertEqual(UserImage.objects.count(), 0)

        # Create the image.
        response = self.client.post(
            path=reverse("images_api:add_image"),
            data={
                "image": TestUtils.create_temp_file("test.gif"),
            },
            **TestUtils.generate_user_auth_headers(self.user),
        )

        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Image was not created.
        self.assertEqual(UserImage.objects.count(), 0)


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class ShareImageViewTests(CustomTestCase, APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.user_1 = UserFactory.create()
        self.user_2 = UserFactory.create(username="user2")
        self.user_1_image = UserImageFactory.create(owner=self.user_1)

    def test_share_image_success(self):
        """Share an image."""

        # Initial assertions
        # user_2 has no image named file.png
        self.assertFalse(
            UserImage.objects.filter(
                image=self.user_1_image.image.name, owner=self.user_2
            ).exists()
        )

        # Create the image.
        response = self.client.post(
            path=reverse("images_api:share_image"),
            data={"image_name": self.user_1_image.image.name, "target_user": "user2"},
            **TestUtils.generate_user_auth_headers(self.user_1),
        )

        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Image was shared - user2 now has an image named file.png
        self.assertTrue(
            UserImage.objects.filter(
                image=self.user_1_image.image, owner=self.user_2
            ).exists()
        )

        # Check response
        self.assertEqual(
            response.json(),
            {
                "message": f"{self.user_1_image.image.name} has been succesfully shared to user2"
            },
        )

        # Get updated instance from database.
        self.user_1_image.refresh_from_db()

        # Confirm times_shared of user_1_image was updated. from 0 to 1.
        self.assertEqual(self.user_1_image.times_shared, 1)

    def test_share_another_users_image_error(self):
        """Ensure attempt to share an image created by another user rsults in error."""

        # Initial assertions - 1 image initially exists. - Owned by user1
        self.assertEqual(UserImage.objects.count(), 1)

        # Create a third user, so we try to share the image to them.
        UserFactory.create(username="user3")

        # Create the image.
        response = self.client.post(
            path=reverse("images_api:share_image"),
            data={"image_name": self.user_1_image.image.name, "target_user": "user3"},
            **TestUtils.generate_user_auth_headers(
                self.user_2
            ),  # Here we try to share it using user2 credentials
        )

        # Verify response status
        # 404 since user2 does not have such image.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Image was not shared. still just 1 image exists.
        self.assertEqual(UserImage.objects.count(), 1)

    def test_share__image_empty_request_results_in_error(self):
        """Ensure attempt to share an image with incorrect details results in error."""

        # Initial assertions - 1 image initially exists.
        self.assertEqual(UserImage.objects.count(), 1)

        # Create the image.
        response = self.client.post(
            path=reverse("images_api:share_image"),
            data={},
            **TestUtils.generate_user_auth_headers(self.user_1),
        )

        # Verify response status
        # 404 since user2 does not have such image.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Image was not shared. still just 1 image exists.
        self.assertEqual(UserImage.objects.count(), 1)

        # Confirm the response
        self.assertEqual(
            response.json(),
            {
                "target_user": ["This field is required."],
                "image_name": ["This field is required."],
            },
        )


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class SearchImageViewTests(CustomTestCase, APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.user_1 = UserFactory.create()
        self.user_2 = UserFactory.create(username="user2")
        self.user_1_image_public = UserImageFactory.create(owner=self.user_1)
        self.user_1_image_private = UserImageFactory.create(
            owner=self.user_1,
            private=True,
            image=TestUtils.create_temp_file("file2.png"),
        )
        self.user_2_image_public = UserImageFactory.create(
            owner=self.user_2, image=TestUtils.create_temp_file("file3.png")
        )
        self.user_2_image_public_2 = UserImageFactory.create(
            owner=self.user_2, image=TestUtils.create_temp_file("unique_name.png")
        )

    def test_search_images_success(self):
        """Search for images."""

        # Initial assertions --- 4 images(3 public, 1 private)
        self.assertEqual(UserImage.objects.count(), 4)

        # Create the image.
        response = self.client.get(
            path=reverse("images_api:search_image"),
            data={"name": "fil"},
            **TestUtils.generate_user_auth_headers(self.user_1),
        )

        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response
        self.assertEqual(
            response.json(),
            [
                {
                    "owner": "shols",
                    "name": f"{self.user_1_image_public.image.name}",
                    "image": f"/media/{self.user_1_image_public.image.name}",
                    "times_shared": 0,
                    "size": 1049,
                },
                {
                    "owner": "shols",
                    "name": f"{self.user_1_image_private.image.name}",
                    "image": f"/media/{self.user_1_image_private.image.name}",
                    "times_shared": 0,
                    "size": 1049,
                },
                {
                    "owner": "user2",
                    "name": f"{self.user_2_image_public.image.name}",
                    "image": f"/media/{self.user_2_image_public.image.name}",
                    "times_shared": 0,
                    "size": 1049,
                },
            ],
        )

    def test_private_images_do_not_show_when_searched_if_not_owned_by_the_user(self):
        """Search for images."""

        # Initial assertions --- 4 images(3 public, 1 private)
        self.assertEqual(UserImage.objects.count(), 4)

        # Create the image.
        response = self.client.get(
            path=reverse("images_api:search_image"),
            data={"name": "file2.png"},
            **TestUtils.generate_user_auth_headers(
                self.user_2
            ),  # search for priavte image file2.png as user2 who is not the owner
        )
        # Verify response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check response
        self.assertEqual(response.json(), [])
