from django.contrib import admin
from .models import Hashtag, Post, Comment, Like, Profile, Follow, PostMedia, Poll, PollOption, PollVote

admin.site.register(Hashtag)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(PostMedia)
admin.site.register(Poll)
admin.site.register(PollOption)
admin.site.register(PollVote)
