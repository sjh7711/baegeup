# photos/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    first_name = None
    last_name = None
    email = None
    
    username = models.CharField(max_length=4, unique=True)
    phone = models.CharField(max_length=11, unique=True)

class Photo(models.Model):
    user = get_user_model()
    image = models.ImageField(upload_to='photos/uploads/')
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(user, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(user, related_name='liked_photos', blank=True)
    
    def __str__(self):
        return f"{self.description[:20]} - {self.uploaded_by.username}"

class Comment(models.Model):
    user = get_user_model()
    photo = models.ForeignKey(Photo, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(user, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.photo.description[:20]}"

