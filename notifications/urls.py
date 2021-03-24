from django.urls import path
from notifications.views import ShowNotifications, DeleteNotification

urlpatterns = [
   	path('', ShowNotifications, name='show_notifications'),
   	path('<noti_id>/delete', DeleteNotification, name='delete_notification'),

]