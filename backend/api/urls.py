from django.urls import path
from .views import (
    register_view, login_view, logout_view,
    PostListCreateView, PostDetailView,
    CommentListCreateView, ToggleLikeView,
    UserProfileView, ToggleFollowView, AvatarUploadView,
    PollVoteView,
)

urlpatterns = [
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('posts/', PostListCreateView.as_view(), name='posts'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comments'),
    path('posts/<int:post_id>/like/', ToggleLikeView.as_view(), name='toggle-like'),
    path('posts/<int:post_id>/vote/', PollVoteView.as_view(), name='poll-vote'),
    path('users/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('users/<str:username>/follow/', ToggleFollowView.as_view(), name='toggle-follow'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='avatar-upload'),
]
