from django.contrib import admin
from .models import Poll, Vote

class PollAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "created_at",
        "expires_at",
        "is_expired",
        "total_votes",
    )
    list_filter = ("created_at", "expires_at", "owner")
    search_fields = ("title", "description")
    ordering = ("-created_at",)
    readonly_fields = ("total_votes", "is_expired")

    def total_votes(self, obj):
        return obj.votes.count()
    total_votes.short_description = "Votes"

class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "poll",
        "voter",
        "option",
        "created_at",
    )
    list_filter = ("created_at", "option", "poll")
    search_fields = ("poll__title", "option")
    ordering = ("-created_at",)

admin.site.register(Poll, PollAdmin)
admin.site.register(Vote, VoteAdmin)