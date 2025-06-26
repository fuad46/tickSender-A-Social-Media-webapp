
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings

class MyUserManager(BaseUserManager):
    def create_user(self, phone, full_name, password=None):
        if not phone:
            raise ValueError("Phone number is required")
        user = self.model(phone=phone, full_name=full_name, )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, full_name,  password=None):
        user = self.create_user(phone, full_name,  password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class UserProfile(AbstractBaseUser):
    phone = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=100, default=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin




class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    audio = models.FileField(upload_to='audios/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name}'s post at {self.timestamp}"




class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField( null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
class Reaction(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    post = models.ForeignKey('Post', related_name='reactions', on_delete=models.CASCADE, null=True, blank=True)
    value = models.CharField(max_length=10, choices=[('like', 'Like'), ('dislike', 'Dislike')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)




class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

class MyFriend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='friend_of', on_delete=models.CASCADE)
    since = models.DateTimeField(auto_now_add=True)
