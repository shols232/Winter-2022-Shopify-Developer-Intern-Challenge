from tests.testutils import CustomTestCase
from images.serializers import ShareImageSerializer

class ShareImageSerializerTests(CustomTestCase):
    VALID_DATA_DICTS = [
        {
            "target_user": "user1",
            "image_name": "some_image.jpg",
        },
        {
            "target_user": "user2",
            "image_name": "some_new_img.png",
        },
        {
            "target_user": "user3",
            "image_name": "some_new_img.jpeg",
        },
    ]

    INVALID_DATA_DICTS = [
        {
            "data": {
                "target_user": "",
                "image_name": "valid_image.png",
            },
            "error": ("target_user", ["This field may not be blank."]),
            "label": "Blank recipients.",
        },
        {
            "data": {
                "image_name": "another_image.png",
            },
            "error": ("target_user", ["This field is required."]),
            "label": "Required recipients.",
        },
    ]

    def setUp(self):
        self.required_fields = ["target_user", "image_name"]

    def test_fields(self):
        serializer = ShareImageSerializer()
        self.assert_fields_required(True, serializer, self.required_fields)
        self.assertEqual(
            len(serializer.fields),
            len(self.required_fields),
        )

    def test_valid_data(self):
        serializer = ShareImageSerializer
        self.assert_valid_data(form=serializer, valid_data_dicts=self.VALID_DATA_DICTS)

    def test_invalid_data(self):
        serializer = ShareImageSerializer
        self.assert_invalid_data(
            form=serializer, invalid_data_dicts=self.INVALID_DATA_DICTS
        )
