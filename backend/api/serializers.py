from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Sum, Count
from rest_framework import serializers
from .models import Profile, Follow


def _avatar_url(user, request=None):
    try:
        avatar = user.profile.avatar
    except Profile.DoesNotExist:
        return None
    if not avatar:
        return None
    try:
        url = avatar.url
    except ValueError:
        return None
    if request is not None:
        return request.build_absolute_uri(url)
    return url


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=4)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Username already exists.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs.get('username'), password=attrs.get('password'))
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()
    avatar = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()
    # posts_count, likes_received, comments_count будут добавлены,
    # когда появятся соответствующие модели (участники 2 и 3).

    def get_avatar(self, obj):
        return _avatar_url(obj, self.context.get('request'))

    def get_followers_count(self, obj):
        return obj.followers_set.count()

    def get_following_count(self, obj):
        return obj.following_set.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if not user or not user.is_authenticated or user.id == obj.id:
            return False
        return Follow.objects.filter(follower=user, following=obj).exists()

    def get_is_self(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        return bool(user and user.is_authenticated and user.id == obj.id)


class AvatarUploadSerializer(serializers.Serializer):
    avatar = serializers.ImageField()
