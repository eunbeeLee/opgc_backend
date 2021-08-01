from django.urls import path

from api.profiles.views import UserProfileView

app_name = 'profiles'

urlpatterns = [
    path(r'', UserProfileView.as_view(), name='user_profile'),
]