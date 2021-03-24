from django.contrib import admin

from posts.models import Post, Tag, Follow, Stream, TF_Post

# Register your models here.
admin.site.register(Tag)
admin.site.register(TF_Post)
admin.site.register(Post)
admin.site.register(Follow)
admin.site.register(Stream)
