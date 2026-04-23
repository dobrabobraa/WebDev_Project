from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Sum, Count
from rest_framework import serializers
from .models import Hashtag, Post, Profile, Follow, PostMedia


IMAGE_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
VIDEO_EXTS = {'mp4', 'webm', 'mov', 'm4v', 'ogg', 'ogv'}


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


def _absolute(url, request):
    if not url:
        return None
    if request is not None:
        return request.build_absolute_uri(url)
    return url


def _detect_kind(filename):
    ext = (filename.rsplit('.', 1)[-1] if '.' in filename else '').lower()
    if ext in IMAGE_EXTS:
        return PostMedia.IMAGE
    if ext in VIDEO_EXTS:
        return PostMedia.VIDEO
    return None


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


class PostMediaReadSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = PostMedia
        fields = ['id', 'kind', 'url', 'order']

    def get_url(self, obj):
        try:
            raw = obj.file.url
        except ValueError:
            return None
        return _absolute(raw, self.context.get('request'))


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    title = serializers.CharField(max_length=200, required=True, allow_blank=False)
    hashtags = serializers.SerializerMethodField()
    hashtags_input = serializers.ListField(
        child=serializers.CharField(max_length=100), write_only=True, required=False, default=list,
    )
    hashtags_input_text = serializers.CharField(write_only=True, required=False, allow_blank=True)
    media = PostMediaReadSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'text', 'created_at', 'updated_at',
            'hashtags', 'hashtags_input', 'hashtags_input_text',
            'author_username', 'author_avatar',
            'media',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'hashtags',
            'author_username', 'author_avatar', 'media',
        ]

    def get_author_avatar(self, obj):
        return _avatar_url(obj.author, self.context.get('request'))

    def get_hashtags(self, obj):
        return list(obj.hashtags.values_list('name', flat=True))

    def _sync_hashtags(self, post, tag_names):
        tags = []
        for raw in tag_names:
            name = raw.strip().lstrip('#').lower()
            if name:
                tag, _ = Hashtag.objects.get_or_create(name=name)
                tags.append(tag)
        post.hashtags.set(tags)

    def _attach_media(self, post):
        request = self.context.get('request')
        if request is None:
            return
        files = request.FILES.getlist('media_files')
        start_order = post.media.count()
        for i, f in enumerate(files):
            kind = _detect_kind(f.name)
            if not kind:
                continue
            PostMedia.objects.create(post=post, file=f, kind=kind, order=start_order + i)

    def _collect_tags(self, validated_data):
        names = list(validated_data.pop('hashtags_input', None) or [])
        raw_text = validated_data.pop('hashtags_input_text', None)
        if raw_text:
            for piece in raw_text.replace(',', ' ').split():
                names.append(piece)
        return names

    @transaction.atomic
    def create(self, validated_data):
        tag_names = self._collect_tags(validated_data)
        post = Post.objects.create(**validated_data)
        self._sync_hashtags(post, tag_names)
        self._attach_media(post)
        return post

    @transaction.atomic
    def update(self, instance, validated_data):
        tags_provided = 'hashtags_input' in validated_data or 'hashtags_input_text' in validated_data
        tag_names = self._collect_tags(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_provided:
            self._sync_hashtags(instance, tag_names)
        return instance


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField()
    avatar = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_self = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        return _avatar_url(obj, self.context.get('request'))

    def get_posts_count(self, obj):
        return obj.posts.count()

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
