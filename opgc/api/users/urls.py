from django.conf.urls import url


from api.users.views import UserViewSet

app_name = 'users'

user_list = UserViewSet.as_view({
    'get': 'list',
})

urlpatterns = [
    url(r'^$', user_list, name='user_list'),
]
