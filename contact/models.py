from django.db import models

# Create your models here.

class Contact(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.full_name} - {self.subject}"
