from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.templatetags.static import static

from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    A user profile model for maintaining default
    delivery information and order history
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    is_subscriber = models.BooleanField(default=False)

    image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    workouts_completed = models.PositiveIntegerField(default=0)
    weight_lost = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)

    default_phone_number = models.CharField(max_length=20, blank=True)
    default_street_address1 = models.CharField(max_length=80, null=True, blank=True)
    default_street_address2 = models.CharField(max_length=80, null=True, blank=True)
    default_town_or_city = models.CharField(max_length=40, null=True, blank=True)
    default_postcode = models.CharField(max_length=20, null=True, blank=True)
    default_country = CountryField(blank_label="Country", null=True, blank=True)

    def __str__(self):
        return self.user.username

    @property
    def image_url(self):
        """
        Always return a usable image URL
        """
        if self.image:
            return self.image.url
        return static("img/noimage.png")


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile automatically
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
