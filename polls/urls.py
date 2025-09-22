from django.urls import path, include
from .views import PollModelViewSet, VoteModelViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'polls', PollModelViewSet, basename="list-polls")

urlpatterns = [
    path('', include(router.urls)),
    path('polls/<uuid:poll_id>/votes/', VoteModelViewSet.as_view(), name='list-votes'),
]