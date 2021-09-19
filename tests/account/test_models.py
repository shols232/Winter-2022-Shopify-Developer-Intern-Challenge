import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.test import TestCase


class UserFactory(factory.django.DjangoModelFactory):
    username = 'shols'
    password = make_password("password")

    class Meta:
        model = User
        django_get_or_create = (
            'username',
            'password',
        )
