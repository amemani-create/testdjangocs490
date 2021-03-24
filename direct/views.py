from django.shortcuts import render, redirect
from django.template import loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User

from accounts.models import Profile
from direct.models import Message

from django.db.models import Q
from django.core.paginator import Paginator


@login_required
def Inbox(request):
    messages = Message.get_messages(user=request.user)
    active_direct = None
    directs = None
    # organizing how the messages show up in the inbox whihc is the menu section of the direct.html
    if messages:
        message = messages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, recipient=message['user'])
        directs.update(is_read=True)
        for message in messages:  # shows how many unread messages there are from a user
            if message['user'].username == active_direct:
                message['unread'] = 0

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }

    template = loader.get_template('direct.html')

    return HttpResponse(template.render(context, request))


@login_required
def Directs(request, username):  # view to show the conversation section of direct.html
    user = request.user
    messages = Message.get_messages(user=user)
    active_direct = username
    directs = Message.objects.filter(user=user, recipient__username=username)
    directs.update(is_read=True)
    for message in messages:  # counter for unread messages
        if message['user'].username == username:
            message['unread'] = 0

    context = {
        'directs': directs,
        'messages': messages,
        'active_direct': active_direct,
    }

    template = loader.get_template('direct.html')

    return HttpResponse(template.render(context, request))


@login_required
def SendDirect(request):  # brings messages from another user into the inbox and conversation sections
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == 'POST':
        to_user = User.objects.get(username=to_user_username)
        Message.send_message(from_user, to_user, body)
        return redirect('inbox')
    else:
        HttpResponseBadRequest()


@login_required
def UserSearch(request):  # search for users to send a DM to
    query = request.GET.get("q")
    context = {}

    if query:  # queryset of username(foreignkey), first name, and lastname
        users = Profile.objects.filter(
            Q(user__username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query))

        # Pagination
        paginator = Paginator(users, 20)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users': users_paginator,
        }

    template = loader.get_template('search_user.html')

    return HttpResponse(template.render(context, request))


@login_required
def NewConversation(request, username):  # from search results of users send one user a message
    from_user = request.user
    body = ''
    try:
        to_user = User.objects.get(username=username)
    except Exception as e:
        return redirect('user_search')
    if from_user != to_user:
        Message.send_message(from_user, to_user, body)
    return redirect('inbox')


def checkDirects(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(user=request.user, is_read=False).count()

    return {'directs_count': directs_count}
