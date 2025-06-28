from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Post,FriendRequest, MyFriend
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import Comment, Post
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def register(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        full_name = request.POST.get('full_name')
        sex = request.POST.get('gender')
        password = request.POST.get('password')

        if not phone or not full_name or not password:
            messages.error(request, "All fields are required.")
        elif UserProfile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already exists.")
        else:
            user = UserProfile(phone=phone, full_name=full_name)
            user.set_password(password)
            user.save()
            messages.success(request, "Registration successful!")
            return redirect('login')
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')

@login_required(login_url='login')
def home(request):
    return render(request, 'home.html')

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')

# post by user 
@login_required(login_url='login')
def home(request):
    if request.method == "POST":
        text = request.POST.get('text')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        audio = request.FILES.get('audio')

        
        if text or image or video or audio:
            Post.objects.create(
                user=request.user,
                text=text,
                image=image,
                video=video,
                audio=audio
            )
        else:
            messages.warning(request, "You must include text, an image, a video, or audio to post.")

        return redirect('home')

    posts = Post.objects.filter(user=request.user).order_by('-timestamp')
    friend_ids = MyFriend.objects.filter(user=request.user).values_list('friend_id', flat=True)
    posts = Post.objects.filter(user__in=list(friend_ids) + [request.user.id]).order_by('-timestamp')
    for post in posts:
        post.pretty_time = format_post_time(post.timestamp)
        post.like_count = post.reactions.filter(value='like').count()     # ✅ Here
        post.dislike_count = post.reactions.filter(value='dislike').count()
        post.user_reaction = post.reactions.filter(user=request.user).first()
 

    return render(request, 'home.html', {'posts': posts})



from datetime import timedelta
from django.utils import timezone

def format_post_time(post_time):
    now = timezone.now()  
    diff = now - post_time

    if diff < timedelta(minutes=1):
        return "Just now"
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return f"Posted {minutes} min ago"
    elif diff < timedelta(hours=24):
        hours = int(diff.total_seconds() / 3600)
        return f"Posted {hours} hr ago"
    else:
        return post_time.strftime("%d %B, %Y").lstrip("0").replace(" 0", " ")






from .models import Post
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def profile(request):
    user = request.user

    if request.method == 'POST':
        # Update bio
        if 'bio' in request.POST:
            user.bio = request.POST.get('bio')
            user.save()
            messages.success(request, "Bio updated.")

        # Update profile image
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')
            user.save()
            messages.success(request, "Profile picture updated.")

        # Handle post (reuse home logic)
        text = request.POST.get('text')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        audio = request.FILES.get('audio')
        if text or image or video or audio:
            Post.objects.create(
                user=user,
                text=text,
                image=image,
                video=video,
                audio=audio
            )
            messages.success(request, "Post shared.")

        return redirect('profile')

    posts = Post.objects.filter(user=user).order_by('-timestamp')
    for post in posts:
        post.pretty_time = format_post_time(post.timestamp)

    return render(request, 'profile.html', {'user': user, 'posts': posts})

@login_required(login_url='login')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect('profile')  # or 'profile' if deleting from profile page
    else:
        return HttpResponseForbidden("Invalid request")

from django.shortcuts import redirect, get_object_or_404
from .models import Post, Reaction
from django.contrib.auth.decorators import login_required

@login_required
def react_to_post(request, post_id):
    if request.method == 'POST':
        value = request.POST.get('value')  # either 'like' or 'dislike'
        post = get_object_or_404(Post, id=post_id)

        # Remove existing reaction from same user
        existing = Reaction.objects.filter(user=request.user, post=post)
        if existing.exists():
            existing.delete()

        # Save new reaction
        if value in ['like', 'dislike']:
            Reaction.objects.create(user=request.user, post=post, value=value)

    return redirect('home')



@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        post = get_object_or_404(Post, id=post_id)
        if text:
            Comment.objects.create(user=request.user, post=post, text=text)
    return redirect('home')


# @login_required
# def search_users(request):
#     query = request.GET.get('q')
#     results = []
#     if query:
#         results = UserProfile.objects.filter(
#             Q(full_name__icontains=query) | Q(phone__icontains=query)
#         ).exclude(id=request.user.id)

#     return render(request, 'searched.html', {'results': results, 'query': query})

# @login_required
# def search_users(request):
#     query = request.GET.get('q')
#     results = []
#     if query:
#         results = UserProfile.objects.filter(
#             Q(full_name__icontains=query) | Q(phone__icontains=query)
#         ).exclude(id=request.user.id)

   
#     sent_requests_ids = FriendRequest.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
#     friends_ids = MyFriend.objects.filter(user=request.user).values_list('friend_id', flat=True)

#     return render(request, 'searched.html', {
#         'results': results,
#         'query': query,
#         'sent_requests_ids': list(sent_requests_ids),
#         'friends_ids': list(friends_ids)
#     })



@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(UserProfile, id=user_id)
    if request.user != to_user:
        FriendRequest.objects.get_or_create(from_user=request.user, to_user=to_user)
    return redirect('all_people')

@login_required
def view_friend_requests(request):
    requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'friend-request.html', {'requests': requests})

@login_required
def accept_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    MyFriend.objects.create(user=request.user, friend=fr.from_user)
    MyFriend.objects.create(user=fr.from_user, friend=request.user)
    fr.delete()
    return redirect('friend_requests')

@login_required
def delete_friend_request(request, request_id):
    fr = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    fr.delete()
    return redirect('friend_requests')





@login_required
def friend_requests_view(request):
    incoming_requests = FriendRequest.objects.filter(receiver=request.user)
    return render(request, 'friend-request.html', {'requests': incoming_requests})

@login_required
def my_friends_view(request):
    friend_objs = MyFriend.objects.filter(user=request.user)
    friends = [f.friend for f in friend_objs]  # get actual UserProfile instances
    return render(request, 'my-friend.html', {'friends': friends})

from django.core.paginator import Paginator
from .models import FriendRequest, MyFriend, UserProfile

@login_required
def all_people_view(request):
    user = request.user
    all_users = UserProfile.objects.exclude(id=user.id)
    paginator = Paginator(all_users, 40)  # 40 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get friends & sent requests to avoid showing "Send Request" unnecessarily
    friends_ids = MyFriend.objects.filter(user=user).values_list('friend_id', flat=True)
    sent_requests_ids = FriendRequest.objects.filter(from_user=user).values_list('to_user_id', flat=True)

    return render(request, 'allpeople.html', {
        'page_obj': page_obj,
        'friends_ids': list(friends_ids),
        'sent_requests_ids': list(sent_requests_ids)
    })


@login_required(login_url='login')
def profile(request):
    user = request.user

    if request.method == 'POST':
        if 'bio' in request.POST:
            user.bio = request.POST.get('bio')
            user.save()
            messages.success(request, "Bio updated.")
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES.get('profile_image')
            user.save()
            messages.success(request, "Profile picture updated.")

        text = request.POST.get('text')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        audio = request.FILES.get('audio')
        if text or image or video or audio:
            Post.objects.create(
                user=user,
                text=text,
                image=image,
                video=video,
                audio=audio
            )
            messages.success(request, "Post shared.")
        return redirect('profile')

    posts = Post.objects.filter(user=user).order_by('-timestamp')
    for post in posts:
        post.pretty_time = format_post_time(post.timestamp)

    # ✅ Count actual number of friends
    friends_count = MyFriend.objects.filter(user=user).count()

    return render(request, 'profile.html', {
        'user': user,
        'posts': posts,
        'friends_count': friends_count
    })
@login_required
def create_post(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        audio = request.FILES.get('audio')

        Post.objects.create(
            user=request.user,
            text=text,
            image=image,
            video=video,
            audio=audio
        )
        return redirect('profile')  # redirect to profile afte

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def update_bio(request):
    if request.method == 'POST':
        new_bio = request.POST.get('bio')
        if new_bio:
            request.user.bio = new_bio
            request.user.save()
    return redirect('profile')
from .models import MyFriend, FriendRequest

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    results = UserProfile.objects.filter(full_name__icontains=query).exclude(id=request.user.id)

    # Get IDs of sent requests and friends
    sent_requests_ids = FriendRequest.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    friends_ids = MyFriend.objects.filter(user=request.user).values_list('friend_id', flat=True)

    return render(request, 'searched.html', {
        'query': query,
        'results': results,
        'friends_ids': list(friends_ids),
        'sent_requests_ids': list(sent_requests_ids),
    })


# from rest_framework import viewsets, permissions
# from .models import Message
# from .serializers import MessageSerializer
# from rest_framework.response import Response
# from rest_framework.decorators import action

# class MessageViewSet(viewsets.ModelViewSet):
#     queryset = Message.objects.all()
#     serializer_class = MessageSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         friend_id = self.request.query_params.get('friend_id')

#         if friend_id:
#             return Message.objects.filter(
#                 sender__id__in=[user.id, friend_id],
#                 receiver__id__in=[user.id, friend_id]
#             ).order_by('timestamp')
#         return Message.objects.none()

#     def perform_create(self, serializer):
#         serializer.save(sender=self.request.user)

#     @action(detail=False, methods=['post'], url_path='mark-read')
#     def mark_as_read(self, request):
#         friend_id = request.data.get('friend_id')
#         Message.objects.filter(sender_id=friend_id, receiver=request.user, is_read=False).update(is_read=True)
#         return Response({'status': 'Messages marked as read'})

# def chat_view(request, friend_id):
#     messages = Message.objects.filter(
#         Q(sender=request.user, recipient_id=friend_id) |
#         Q(sender_id=friend_id, recipient=request.user)
#     ).order_by('timestamp')
#     friend = get_object_or_404(UserProfile, id=friend_id)
#     return render(request, 'chat.html', {'messages': messages, 'friend': friend})
# def chat_view(request, friend_id):
#     friend = get_object_or_404(UserProfile, id=friend_id)  
#     context = {
#         'request': request, 
#         'friend': friend,
#     }
#     return render(request, 'chat.html', context)
from django.shortcuts import render, redirect
from .models import Message, UserProfile
from django.contrib.auth.decorators import login_required

@login_required
def chat_view(request, friend_id):
    friend = UserProfile.objects.get(id=friend_id)
    messages = Message.objects.filter(
        sender__in=[request.user, friend],
        receiver__in=[request.user, friend]
    ).order_by('timestamp')

    # Mark all unread messages as read
    Message.objects.filter(sender=friend, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=friend, content=content)
            return redirect('chat', friend_id=friend.id)

    return render(request, 'chat.html', {'messages': messages, 'friend': friend})
