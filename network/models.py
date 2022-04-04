from datetime import datetime

import project4.settings as settings

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.views.generic.list import ListView

from django.utils import timezone

class User(AbstractUser):
    pass

class Profile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    profile_pic = models.ImageField(upload_to='profilepix/',default='profilepix/default_dog.jpg')
    full_name = models.CharField(max_length=50)
    bio = models.CharField(max_length=500)

class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_timestamp = models.DateTimeField(default=timezone.now)
    post_title = models.CharField(max_length=100)
    post_text = models.CharField(max_length=1000)

class Like(models.Model):
    class Meta:
        unique_together = (('user_id', 'post_id'),)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

class Follow(models.Model):
    class Meta:
        unique_together = (('follower_id', 'followee_id'),)
    follower_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followee_id")
    followee_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower_id")
