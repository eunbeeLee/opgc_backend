import pytest
from django.urls import reverse
from rest_framework import status

from tests.request_helper import pytest_request


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_user_list(rf, client, user_context):
    url = reverse(viewname="users:user-list")

    response = pytest_request(rf,
                              method='get',
                              url=url)

    assert response.status_code == status.HTTP_200_OK
