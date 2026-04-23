from django.contrib import admin
from .models import Hashtag, Post, Profile, Follow, PostMedia

admin.site.register(Hashtag)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Follow)
admin.site.register(PostMedia)
