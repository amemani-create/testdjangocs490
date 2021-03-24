from django.urls import path
from direct.views import Inbox, Directs, SendDirect, UserSearch, NewConversation

urlpatterns = [
    path('', Inbox, name='inbox'),
    path('messages/<username>', Directs, name='direct_messages'),
    path('send/', SendDirect, name='send_direct'),
    path('new/', UserSearch, name='user_search'),
    path('new/<username>', NewConversation, name='new_conversation'),
]
