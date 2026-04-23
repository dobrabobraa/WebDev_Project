from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Post, Comment, Like, Profile, Follow, Poll, PollOption, PollVote
from .serializers import (
    RegistrationSerializer, LoginSerializer, PostSerializer,
    CommentSerializer, LikeSerializer,
    UserProfileSerializer, AvatarUploadSerializer,
)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        Profile.objects.get_or_create(user=user)
        return Response({'message': 'Registration successful.', 'user_id': user.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        Profile.objects.get_or_create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_view(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'detail': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful.'})
    except Exception:
        return Response({'detail': 'Invalid refresh token.'}, status=status.HTTP_400_BAD_REQUEST)


class PostListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        posts = (
            Post.objects
            .select_related('author', 'author__profile', 'poll')
            .prefetch_related(
                'comments__author__profile', 'likes', 'hashtags',
                'media', 'poll__options__votes',
            )
            .order_by('-created_at')
        )
        return Response(PostSerializer(posts, many=True, context={'request': request}).data)

    def post(self, request):
        serializer = PostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, pk):
        return get_object_or_404(Post, pk=pk)

    def get(self, request, pk):
        post = self.get_object(pk)
        return Response(PostSerializer(post, context={'request': request}).data)

    def put(self, request, pk):
        post = self.get_object(pk)
        if post.author != request.user:
            return Response({'detail': 'You can edit only your own posts.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if post.author != request.user:
            return Response({'detail': 'You can delete only your own posts.'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        like = Like.objects.filter(post=post, user=request.user).first()
        if like:
            like.delete()
            return Response({'message': 'Like removed.'})
        serializer = LikeSerializer(data={'post': post.id})
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, user=request.user)
        return Response({'message': 'Like added.'}, status=status.HTTP_201_CREATED)


class UserProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        Profile.objects.get_or_create(user=user)
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data)


class ToggleFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target.id == request.user.id:
            return Response({'detail': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        existing = Follow.objects.filter(follower=request.user, following=target).first()
        if existing:
            existing.delete()
            return Response({'message': 'Unfollowed.', 'is_following': False})
        Follow.objects.create(follower=request.user, following=target)
        return Response({'message': 'Followed.', 'is_following': True}, status=status.HTTP_201_CREATED)


class AvatarUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = AvatarUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.avatar:
            try:
                profile.avatar.delete(save=False)
            except Exception:
                pass
        profile.avatar = serializer.validated_data['avatar']
        profile.save()
        url = profile.avatar.url if profile.avatar else None
        if url:
            url = request.build_absolute_uri(url)
        return Response({'message': 'Avatar updated.', 'avatar': url})

    def delete(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.avatar:
            try:
                profile.avatar.delete(save=False)
            except Exception:
                pass
            profile.avatar = None
            profile.save()
        return Response({'message': 'Avatar removed.'})


class PollVoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        poll = getattr(post, 'poll', None)
        if poll is None:
            return Response({'detail': 'This post has no poll.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            option_id = int(request.data.get('option_id'))
        except (TypeError, ValueError):
            return Response({'detail': 'option_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        option = PollOption.objects.filter(poll=poll, pk=option_id).first()
        if option is None:
            return Response({'detail': 'Option does not belong to this poll.'}, status=status.HTTP_400_BAD_REQUEST)

        existing = PollVote.objects.filter(poll=poll, user=request.user).first()
        if existing:
            if existing.option_id == option.id:
                existing.delete()
                return Response({'message': 'Vote removed.', 'my_vote_option_id': None})
            existing.option = option
            existing.save()
            return Response({'message': 'Vote switched.', 'my_vote_option_id': option.id})
        PollVote.objects.create(poll=poll, option=option, user=request.user)
        return Response({'message': 'Vote added.', 'my_vote_option_id': option.id}, status=status.HTTP_201_CREATED)
