from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader

from comments.forms import CommentForm
from comments.models import Comment
from posts.forms import NewPostForm, TFPostForm
from posts.models import Stream, Post, Tag, Likes, TF_Post

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from accounts.models import Profile
from django.db.models import Q


@login_required
def index(request):
    user = request.user
    posts = Stream.objects.filter(user=user)

    group_ids = []  # list for post ids from stream
    # need to also add most liked posts

    for post in posts:
        group_ids.append(post.post_id)  # post_id identifies that unique id#

    post_items = Post.objects.all().order_by('-posted')

    template = loader.get_template('index.html')

    context = {
        'post_items': post_items,

    }

    return HttpResponse(template.render(context, request))


@login_required
def PostDetail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    is_favorite = False
    comments = Comment.objects.filter(post=post).order_by('date')
    # checks to see if you've bookmarked the post and use flag for color change of button
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=user)

        if profile.favorites.filter(id=post_id).exists():  # using this boolean flag to identify if post is bookmarked
            is_favorite = True
    # adds comment section to post detail view

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = user
            comment.save()
            return HttpResponseRedirect(reverse('post_detail', args=[post_id]))
    else:
        form = CommentForm()

    template = loader.get_template('post_detail.html')
    context = {
        'post': post,
        'is_favorite': is_favorite,
        'profile': profile,
        'form': form,
        'comments': comments,
    }
    return HttpResponse(template.render(context, request))


@login_required
def NewPost(request):
    user = request.user
    tags_objs = []
    files_objs = []

    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tags_form = form.cleaned_data.get('tags')
            subject = form.cleaned_data.get('subject')

            tags_list = list(tags_form.split(', '))

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            if not picture:
                p, created = Post.objects.get_or_create(subject=subject, caption=caption, user=user)
                p.tags.set(tags_objs)
                p.save()
            else:
                p, created = Post.objects.get_or_create(picture=picture, subject=subject, caption=caption, user=user)
                p.tags.set(tags_objs)
                p.save()
            return redirect('index')
    else:
        form = NewPostForm()

    context = {
        'form': form,
    }

    return render(request, 'new_post.html', context)


@login_required
def tags(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-posted')

    template = loader.get_template('tag.html')

    context = {
        'posts': posts,
        'tag': tag,
    }

    return HttpResponse(template.render(context, request))


@login_required
def like(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    current_likes = post.likes
    liked = Likes.objects.filter(user=user, post=post).count()

    if not liked:
        like = Likes.objects.create(user=user, post=post)
        # like.save()
        current_likes = current_likes + 1

    else:
        Likes.objects.filter(user=user, post=post).delete()
        current_likes = current_likes - 1

    post.likes = current_likes
    post.save()

    return HttpResponseRedirect(reverse('post_detail', args=[post_id]))


@login_required
def favorite(request, post_id):
    user = request.user
    post = Post.objects.get(id=post_id)
    profile = Profile.objects.get(user=user)

    if profile.favorites.filter(id=post_id).exists():
        profile.favorites.remove(post)

    else:
        profile.favorites.add(post)

    return HttpResponseRedirect(reverse('post_detail', args=[post_id]))


@login_required
def ContentSearch(request):  # search for content
    query = request.GET.get("q")
    context = {}

    if query:  # queryset of subject, caption
        content = Post.objects.filter(
            Q(subject__icontains=query) | Q(caption__icontains=query) | Q(tags__title__icontains=query) | Q(
                user__profile__first_name__icontains=query) | Q(user__profile__first_name__icontains=query) | Q(
                user__profile__first_name__icontains=query)
        )

        # Pagination
        paginator = Paginator(content, 20)
        page_number = request.GET.get('page')
        content_paginator = paginator.get_page(page_number)

        context = {
            'content': content_paginator,
        }

    template = loader.get_template('search_content.html')

    return HttpResponse(template.render(context, request))


@login_required
def TutoringForum(request):
    user = request.user
    post_items = TF_Post.objects.all().order_by('-posted')

    template = loader.get_template('tutoring_platform.html')

    context = {
        'post_items': post_items,

    }

    return HttpResponse(template.render(context, request))


@login_required
def TFNewPost(request):
    user = request.user
    tags_objs = []
    files_objs = []

    if request.method == 'POST':
        form = TFPostForm(request.POST, request.FILES)
        if form.is_valid():
            picture = form.cleaned_data.get('picture')
            caption = form.cleaned_data.get('caption')
            tags_form = form.cleaned_data.get('tags')
            subject = form.cleaned_data.get('subject')
            state = form.cleaned_data.get('state')
            city = form.cleaned_data.get('city')
            virtual = form.cleaned_data.get('virtual')
            school_level = form.cleaned_data.get('school_level')
            topics = form.cleaned_data.get('topics')
            tags_list = list(tags_form.split(', '))

            for tag in tags_list:
                t, created = Tag.objects.get_or_create(title=tag)
                tags_objs.append(t)
            if not picture:
                p, created = Post.objects.get_or_create(subject=subject, caption=caption, user=user, state=state,
                                                        city=city, virtual=virtual, school_level=school_level,
                                                        topics=topics)
                p.tags.set(tags_objs)
                p.save()
            else:
                p, created = Post.objects.get_or_create(picture=picture, subject=subject, caption=caption, user=user,
                                                        state=state, city=city, virtual=virtual,
                                                        school_level=school_level, topics=topics)
                p.tags.set(tags_objs)
                p.save()
            return redirect('index')
    else:
        form = TFPostForm()

    context = {
        'form': form,
    }

    return render(request, 'new_tutoring_post.html', context)

@login_required
def TutorSearch(request):  # search for content
    query = request.GET.get("q")
    context = {}

    if query:  # queryset of subject, caption
        content = TF_Post.objects.filter(
            Q(subject__icontains=query) |
            Q(caption__icontains=query) |
            Q(tags__title__icontains=query) |
            Q(user__profile__first_name__icontains=query) |
            Q(user__profile__first_name__icontains=query) |
            Q(user__profile__first_name__icontains=query) |
            Q(user__profile__account_type__icontains=query) |
            Q(virtual__icontains=query) |
            Q(school_level__icontains=query) |
            Q(topics__icontains=query) |
            Q(city__icontains=query) |
            Q(state__icontains=query)

        )

        # Pagination
        paginator = Paginator(content, 20)
        page_number = request.GET.get('page')
        content_paginator = paginator.get_page(page_number)

        context = {
            'content': content_paginator,
        }

    template = loader.get_template('search_tutoring.html')

    return HttpResponse(template.render(context, request))