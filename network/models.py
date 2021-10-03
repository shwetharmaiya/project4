from datetime import datetime

import project4.settings as settings

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils import timezone

class User(AbstractUser):
    pass

class Post(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_timestamp = models.DateTimeField(default=timezone.now)
    post_title = models.CharField(max_length=100)
    post_text = models.CharField(max_length=1000)
