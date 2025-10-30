from django.db import models
from tinymce.models import HTMLField
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Categorys(models.Model):
    title = models.CharField(max_length=250, null=False, blank=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

class BlogEntry(models.Model):
    title = models.CharField(max_length=250, null=False, blank=False)
    content = HTMLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Categorys, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    rating = models.FloatField(null=True, blank=True, default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    image = models.ImageField(null=True, blank=True, upload_to="media/blog_images")

    def __str__(self):
        return f"{self.title}"

class Comments(models.Model):
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    blog_entry = models.ForeignKey(
        BlogEntry, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField(null=False, blank=False, validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        ordering = ["-created_at"]

class SavedPosts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_posts")
    post = models.ForeignKey(BlogEntry, on_delete=models.CASCADE, related_name="savers")
    created_at = models.DateTimeField(auto_now_add=True)