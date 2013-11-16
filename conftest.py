"""
configuration for the tests
"""

import pytest

from django.conf import settings

# this is to create a Domain entries in the database, so they can be used for unit tests:
BASEDOMAIN = "nsupdate.info"
TEST_HOST = 'test.' + BASEDOMAIN  # unit tests can update this host ONLY
TEST_SECRET = "secret"
TEST_HOST2 = 'test2.' + BASEDOMAIN
TEST_SECRET2 = "somethingelse"
NAMESERVER_IP = "85.10.192.104"
NAMESERVER_UPDATE_ALGORITHM = "HMAC_SHA512"
# no problem, you can ONLY update the TEST_HOST with this key, nothing else:
NAMESERVER_UPDATE_KEY = "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ=="
NAMESERVER_PUBLIC = True

USERNAME = 'test'
USERNAME2 = 'test2'
PASSWORD = 'pass'

from django.utils.translation import activate


# Note: fixture must be "function" scope (default), see https://github.com/pelme/pytest_django/issues/33
@pytest.fixture(autouse=True)
def db_init(db):  # note: db is a predefined fixture and required here to have the db available
    """
    Init the database contents for testing, so we have a service domain, ...
    """
    from django.contrib.auth.models import User
    from nsupdate.main.models import Host, Domain
    # create a fresh test user
    u = User.objects.create_user(USERNAME, settings.DEFAULT_FROM_EMAIL, PASSWORD)
    u.save()
    u2 = User.objects.create_user(USERNAME2, 'test@example.org', PASSWORD)
    u2.save()
    # this is for updating:
    Domain.objects.create(
        domain=TEST_HOST,  # special: single-host update secret!
        nameserver_ip=NAMESERVER_IP,
        nameserver_update_algorithm=NAMESERVER_UPDATE_ALGORITHM,
        nameserver_update_key=NAMESERVER_UPDATE_KEY,
        public=NAMESERVER_PUBLIC,
    )
    # this is for querying:
    d = Domain.objects.create(
        domain=BASEDOMAIN,
        nameserver_ip=NAMESERVER_IP,
        nameserver_update_algorithm=NAMESERVER_UPDATE_ALGORITHM,
        nameserver_update_key='invalid=',  # we don't send updates there (and the real key is really secret)
        public=NAMESERVER_PUBLIC,
    )
    # a Host for api / session update tests
    h = Host(subdomain='test', domain=d, created_by=u)
    h.generate_secret(secret=TEST_SECRET)
    h = Host(subdomain='test2', domain=d, created_by=u2)
    h.generate_secret(secret=TEST_SECRET2)


def pytest_runtest_setup(item):
    activate('en')
