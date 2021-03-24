import uuid

from django.db import models
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save, post_delete
from django.utils.text import slugify
from django.urls import reverse

from notifications.models import Notification


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Tag(models.Model):
    title = models.CharField(max_length=150, verbose_name='Tag')
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def get_absolute_url(self):
        return reverse('tags', args=[self.slug])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=200, blank=True, null=True)
    caption = models.TextField(max_length=1500, verbose_name='Caption')
    posted = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, related_name='tags')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    updated_on = models.DateTimeField(auto_now=True)
    picture = models.ImageField(blank=True, null=True, upload_to=user_directory_path, verbose_name='Picture')

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Topics(models.Model):
    topic_name = models.CharField(max_length=200)

    def __str__(self):
        return self.topic_name

    def get_absolute_url(self): #change this later
        return reverse('index')


class TF_Post(Post):
    virtual = models.CharField(max_length=200, blank=True, null=True, )
    state = models.CharField(max_length=3, blank=True, null=True, )
    city = models.CharField(max_length=200, blank=True, null=True, )
    school_level = models.CharField(max_length=200, blank=True, null=True, )
    topics = models.CharField(max_length=200, blank=True, null=True, )


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='follower')
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='following')

    def user_follow(sender, instance, *args, **kwargs):  # adds follow notification to notification page
        follow = instance
        sender = follow.follower
        following = follow.following
        notify = Notification(sender=sender, user=following, notification_type=3)
        notify.save()

    def user_unfollow(sender, instance, *args, **kwargs):  # adds unfollow notification to notification page
        follow = instance
        sender = follow.follower
        following = follow.following

        notify = Notification.objects.filter(sender=sender, user=following, notification_type=3)
        notify.delete()


post_save.connect(Follow.user_follow, sender=Follow)  # adds follower to your list of followers
post_delete.connect(Follow.user_unfollow, sender=Follow)  # removes follower to your list of follower


class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='stream_following')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    def add_post(sender, instance, *args, **kwargs):  # adds the post of the user you follow to your stream
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()


post_save.connect(Stream.add_post, sender=Post)  # saves the post of the user you follow


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_like')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_like')

    def user_liked_post(sender, instance, *args, **kwargs):  # adds like to your notification page
        like = instance
        post = like.post
        sender = like.user
        notify = Notification(post=post, sender=sender, user=post.user, notification_type=1)
        notify.save()

    def user_unlike_post(sender, instance, *args, **kwargs):  # adds unlike to your notification page
        like = instance
        post = like.post
        sender = like.user

        notify = Notification.objects.filter(post=post, sender=sender, notification_type=1)
        notify.delete()


post_save.connect(Likes.user_liked_post, sender=Likes)  # adds like to your liked objects
post_delete.connect(Likes.user_unlike_post, sender=Likes)  # removes like of object from your liked objects
