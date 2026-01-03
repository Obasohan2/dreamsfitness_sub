from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class BlogPost(models.Model):
    title = models.CharField(
        max_length=250,
        unique=True
    )

    slug = models.SlugField(
        max_length=130,
        unique=True,
        blank=True,  
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )

    body = models.TextField()

    image = models.ImageField(
        upload_to="blog/",
        null=True,
        blank=True
    )

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    likes = models.ManyToManyField(
        User,
        related_name="liked_posts",
        blank=True
    )

    unlikes = models.ManyToManyField(
        User,
        related_name="unliked_posts",
        blank=True
    )

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_unlikes(self):
        return self.unlikes.count()

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Comment(models.Model):
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    body = models.TextField()

    created_on = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment by {self.user.username}"
