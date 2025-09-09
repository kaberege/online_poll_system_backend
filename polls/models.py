from django.db import models
import uuid
from django.contrib.postgres.fields import ArrayField
from django.db.models import UniqueConstraint, Index
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()  # Custom user

class Poll(models.Model):
    poll_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    options = ArrayField(
        base_field=models.CharField(max_length=255),
        size=10,
        blank=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            Index(fields=['owner', 'created_at']),
            Index(fields=['expires_at']),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return bool(self.expires_at and self.expires_at <= timezone.now())

class Vote(models.Model):
    vote_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    option = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['voter', 'poll'], name='uq_one_vote_per_user_per_poll'),
        ]

        indexes = [
            Index(fields=['poll','created_at']),
        ]

    def clean(self):
        if self.option not in self.poll.options:
            raise ValidationError("Invalid option for this poll.")