from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = [
        ('staff', 'Staff'),
        ('approver1', 'Approver Level 1'),
        ('approver2', 'Approver Level 2'),
        ('finance', 'Finance'),
        ('admin', 'Admin'),
    ]

    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff',
        help_text="User role in the procurement system"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.name} ({self.get_role_display()})"