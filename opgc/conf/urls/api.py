from django.urls import path, include

urlpatterns = [
    # path('users/', include('api.users.urls')),
    path('githubs/', include('api.githubs.urls')),
    path('ranks/', include('api.ranks.urls')),
    path('notices/', include('api.notices.urls')),
]
