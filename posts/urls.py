from django.urls import path
from posts.views import index, NewPost, PostDetail, tags, like, favorite, ContentSearch, TutoringForum, TFNewPost

urlpatterns = [
    path('', index, name='index'),
    path('new_post/', NewPost, name='new_post'),
    path('<uuid:post_id>', PostDetail, name='post_detail'),
    path('tag/<slug:tag_slug>', tags, name='tags'),
    path('<uuid:post_id>/like', like, name='post_like'),
    path('<uuid:post_id>/favorite', favorite, name='post_favorite'),
    path('new/', ContentSearch, name='search_content'),
    path('tutoring/', TutoringForum, name='tutoring_forum'),
    path('tutoring/new_post/', TFNewPost, name='new_tf_post'),

]
