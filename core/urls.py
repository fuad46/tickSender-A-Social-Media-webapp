from django.urls import path
from . import views

# from .views import MessageViewSet
# from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    
    path('profile/', views.profile, name='profile'),
    path('delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('react/<int:post_id>', views.react_to_post, name='react'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('search/', views.search_users, name='search_users'),
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_request'),
    path('friend-requests/', views.view_friend_requests, name='friend_requests'),
    path('accept-request/<int:request_id>/', views.accept_friend_request, name='accept_request'),
    path('delete-request/<int:request_id>/', views.delete_friend_request, name='delete_request'),

    path('all-people/', views.all_people_view, name='all_people'),
path('create-post/', views.create_post, name='create_post'),
    path('my-friends/', views.my_friends_view, name='my_friends'),
path('update-bio/', views.update_bio, name='update_bio'),
path('chat/<int:friend_id>/', views.chat_view, name='chat'),

]

