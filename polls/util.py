from django.db.models import Count
from .models import Vote

def get_results(poll):
    # Count votes grouped by option
    vote_counts = (
        Vote.objects.filter(poll=poll).values("option")
        .annotate(count=Count("option"))
        .order_by("option")
    )

    # Convert queryset into a dict for quick lookup
    counts_map = {vc["option"]: vc["count"] for vc in vote_counts}

    # Make sure every option is included, even if it has 0 votes
    results = []
    for option in poll.options:
        results.append({
            "option": option,
            "count": counts_map.get(option, 0)
        })
    
    # Total votes
    total_votes = sum(counts_map.values())

    return {
        "poll_id": str(poll.poll_id),
        "title": poll.title,
        "options": poll.options,
        "results": results,
        "total_votes": total_votes,
        "is_expired": poll.is_expired
    }

