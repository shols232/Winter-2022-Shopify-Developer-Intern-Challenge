import factory
from tests.testutils import TestUtils
from django.test.utils import override_settings
from tests.account.test_models import UserFactory
from django.test import TestCase
from images.models import UserImage
from tempfile import TemporaryDirectory


class UserImageFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(UserFactory)
    image = TestUtils.create_temp_file('file.png')
    private = False

    class Meta:
        model = UserImage
        django_get_or_create = (
            "owner",
            "image",
            "private",
        )


@override_settings(MEDIA_ROOT=TemporaryDirectory().name)
@override_settings(DEFAULT_FILE_STORAGE="django.core.files.storage.FileSystemStorage")
class UserImageModelTests(TestCase):
    def setUp(self):
        self.user_image = UserImageFactory.create()

    def test__str__(self):
        self.assertEqual(str(self.user_image), "ImageName: file.png - Owner: shols")
