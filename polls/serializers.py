from rest_framework import serializers
from .models import Poll, Vote
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class PollModelSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    description = serializers.CharField(required=False)
    expires_at = serializers.DateTimeField(
        required=False,
        format='%Y-%m-%dT%H:%M',
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S%z']
    )
    edited = serializers.BooleanField(read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = "__all__"

    def validate_expires_at(self, value):
        """
        Ensure expires_at is timezone-aware and in the future.
        """
        if value and timezone.is_naive(value):
            value = timezone.make_aware(value)

        if value and value <= timezone.now():
            logger.warning("Poll expiry validation failed: expiry in the past.")
            raise serializers.ValidationError("Expiry time must be in the future.")

        return value
    
    def get_is_expired(self, obj):
        return bool(obj.expires_at and obj.expires_at <= timezone.now())

class VoteModelSerializer(serializers.ModelSerializer):
    poll = serializers.PrimaryKeyRelatedField(read_only=True)
    voter = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Vote
        fields = "__all__"

    def validate_option(self, value):
        poll = self.context.get("poll")
        if poll and value.lower() not in [item.lower() for item in poll.options]:
            logger.warning(f"Invalid vote option '{value}' for poll {poll.poll_id}")
            raise serializers.ValidationError("Invalid option for this poll.")
        return value

