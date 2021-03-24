from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic

from accounts.forms import ChangePasswordForm, EditProfileForm
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from accounts.models import Profile
from django.db import transaction
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy

from django.core.paginator import Paginator

from django.urls import resolve

from posts.models import Follow, Stream, Post


def UserProfile(request, username):

    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name
#creating 2 tabs on profile view page to show personal posts and favorite posts
    if url_name == 'profile':
        posts = Post.objects.filter(user=user).order_by('-posted')

    elif url_name == 'bookmarks': #instead of else to create more tabs use elif with url names created in main url file of project
        posts = profile.favorites.all()

    elif url_name == 'popular':
        posts = Post.objects.all().order_by('-likes')[:100]

    # Profile info box
    posts_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()

    # follow status
    follow_status = Follow.objects.filter(following=user, follower=request.user).exists()

    # Pagination
    paginator = Paginator(posts, 15)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    template = loader.get_template('profile.html')

    context = {
        'posts': posts_paginator,
        'profile': profile,
        'following_count': following_count,
        'followers_count': followers_count,
        'posts_count': posts_count,
        'follow_status': follow_status,
        'url_name': url_name,
    }

    return HttpResponse(template.render(context, request))


def UserProfileFavorites(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)

    posts = profile.favorites.all()

    # Profile info box
    posts_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    followers_count = Follow.objects.filter(following=user).count()

    # Pagination
    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    posts_paginator = paginator.get_page(page_number)

    template = loader.get_template('profile_favorite.html')

    context = {
        'posts': posts_paginator,
        'profile': profile,
        'following_count': following_count,
        'followers_count': followers_count,
        'posts_count': posts_count,
    }

    return HttpResponse(template.render(context, request))


class UserRegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')


@login_required
def PasswordChange(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            return redirect('change_password_done')
    else:
        form = ChangePasswordForm(instance=user)

    context = {
        'form': form,
    }

    return render(request, 'change_password.html', context)


def PasswordChangeDone(request):
    return render(request, 'change_password_done.html')


@login_required
def EditProfile(request):
    user = request.user.id
    profile = Profile.objects.get(user__id=user)
    BASE_WIDTH = 400

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile.picture = form.cleaned_data.get('picture')
            profile.first_name = form.cleaned_data.get('first_name')
            profile.last_name = form.cleaned_data.get('last_name')
            profile.location = form.cleaned_data.get('location')
            profile.url = form.cleaned_data.get('url')
            profile.profile_info = form.cleaned_data.get('profile_info')
            profile.account_type = form.cleaned_data.get('account_type')

            profile.save()
            return redirect('index')
    else:
        form = EditProfileForm()

    context = {
        'form': form,
    }

    return render(request, 'edit_profile.html', context)


@login_required
def follow(request, username, option): #this is to follow a user
    following = get_object_or_404(User, username=username)

    try:
        f, created = Follow.objects.get_or_create(follower=request.user, following=following)

        if int(option) == 0:
            f.delete()
            Stream.objects.filter(following=following, user=request.user).all().delete()
        else:
            posts = Post.objects.all().filter(user=following)

            with transaction.atomic(): #changes and updates the database
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.posted, following=following) #based on fields created in Stream class object
                    stream.save()

        return HttpResponseRedirect(reverse('profile', args=[username]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('profile', args=[username]))