from django.core.urlresolvers import reverse
from django.test import TransactionTestCase
from django.test.client import Client
#from django.utils import unittest

class AnonymousTest(TransactionTestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, ' id="id_password"', count=1, status_code=200)

# TODO: create account and try to login
