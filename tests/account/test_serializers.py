from account.serializers import CreateUserSerializer
from tests.testutils import CustomTestCase


class SendSMSMSerializerTests(CustomTestCase):
    VALID_DATA_DICTS = [
        {
            "username": "shols",
            "password": "testing321",
        },
    ]

    INVALID_DATA_DICTS = [
        {
            "data": {
                "username": "",
                "password": "some password",
            },
            "error": ("username", ["This field may not be blank."]),
            "label": "Blank username.",
        },
        {
            "data": {
                "username": "thorfin",
            },
            "error": ("password", ["This field is required."]),
            "label": "Required password.",
        },
    ]

    def setUp(self):
        self.required_fields = ["username", "password"]

    def test_fields(self):
        serializer = CreateUserSerializer()
        self.assert_fields_required(True, serializer, self.required_fields)
        self.assertEqual(
            len(serializer.fields),
            len(self.required_fields),
        )

    def test_valid_data(self):
        serializer = CreateUserSerializer
        self.assert_valid_data(form=serializer, valid_data_dicts=self.VALID_DATA_DICTS)

    def test_invalid_data(self):
        serializer = CreateUserSerializer
        self.assert_invalid_data(form=serializer, invalid_data_dicts=self.INVALID_DATA_DICTS)
