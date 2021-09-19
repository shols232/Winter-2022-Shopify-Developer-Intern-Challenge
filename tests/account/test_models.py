import factory
from django.contrib.auth.hashers import make_password
from django.test import TestCase

from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    username = 'shols'
    password = make_password("password")

    class Meta:
        model = User
        django_get_or_create = (
            'username',
            'password',
        )

