from django.urls import path
from .views import (
    register_view, login_view, logout_view,
    PostListCreateView, PostDetailView,
    UserProfileView, ToggleFollowView, AvatarUploadView,
)

urlpatterns = [
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('posts/', PostListCreateView.as_view(), name='posts'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('users/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/follow/', ToggleFollowView.as_view(), name='toggle-follow'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='avatar-upload'),
]
