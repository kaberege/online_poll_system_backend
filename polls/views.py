from rest_framework.generics import ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly
from .models import Poll, Vote
from .serializers import PollModelSerializer, VoteModelSerializer
from .util import get_results
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class PollModelViewSet(ModelViewSet):
    queryset = Poll.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = PollModelSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(edited=True)
    
    @swagger_auto_schema(
        operation_summary="List all polls",
        operation_description="Retrieve a list of all polls. Anyone can view polls, "
                              "but only authenticated users can create. Polls are ordered by creation date.",
        responses={200: PollModelSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new poll",
        operation_description="Create a new poll with title, description, options, and optional expiry date. "
                              "The authenticated user becomes the owner.",
        request_body=PollModelSerializer,
        responses={201: PollModelSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a poll",
        operation_description="Update an existing poll. Only the owner can update their polls. "
                              "Expired polls cannot be edited.",
        request_body=PollModelSerializer,
        responses={200: PollModelSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a poll",
        operation_description="Delete a poll by ID. Only the owner (or an admin, if allowed) can delete their poll.",
        responses={
            204: openapi.Response(description="Poll deleted successfully"),
            403: "Not allowed to delete this poll",
            404: "Poll not found",
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class VoteModelViewSet(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VoteModelSerializer

    def get_queryset(self):
        poll_id = self.kwargs["poll_id"]
        return Vote.objects.filter(poll=poll_id)

    @swagger_auto_schema(
        operation_summary="List votes for a poll",
        operation_description="Retrieve all votes for the specified poll along with real-time results. "
                              "Anyone can view votes and results.",
        responses={
            200: openapi.Response(
                description="Votes with real-time results",
                examples={
                    "application/json": {
                        "votes": [
                            {"vote_id": "uuid", "poll": "uuid", "voter": "user_id", "option": "Yes"}
                        ],
                        "real_time_results": {
                            "poll_id": "uuid",
                            "title": "Poll title",
                            "options": ["Yes", "No"],
                            "results": [
                                {"option": "Yes", "count": 1},
                                {"option": "No", "count": 0}
                            ],
                            "total_votes": 1,
                            "is_expired": False
                        }
                    }
                }
            ),
            404: "Poll not found"
        }
    )
    def list(self, request):
        votes_per_poll = self.get_queryset()
        serializer_votes = self.get_serializer(votes_per_poll, many=True)

        try:
            poll = Poll.objects.get(poll_id=poll_id)
        except Poll.DoesNotExist:
            return Response({"message": "Poll not found"}, status.HTTP_404_NOT_FOUND)

        real_time_results = get_results(poll)

        return Response(
            {
                "votes": serializer_votes.data,
                "real_time_results": real_time_results
            }, 
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_summary="Cast a vote on a poll",
        operation_description="Cast a vote for one of the poll's options. "
                              "Only authenticated users can vote. "
                              "Users can vote once per poll, and cannot vote on expired polls.",
        request_body=VoteModelSerializer,
        responses={
            201: openapi.Response(
                description="Vote created with updated results",
                examples={
                    "application/json": {
                        "vote": {"vote_id": "uuid", "poll": "uuid", "voter": "user_id", "option": "Yes"},
                        "real_time_results": {
                            "poll_id": "uuid",
                            "title": "Poll title",
                            "options": ["Yes", "No"],
                            "results": [
                                {"option": "Yes", "count": 1},
                                {"option": "No", "count": 0}
                            ],
                            "total_votes": 1,
                            "is_expired": False
                        }
                    }
                }
            ),
            400: "Invalid vote (duplicate, expired poll, or invalid option)",
            404: "Poll not found"
        }
    )
    def create(self, request, poll_id):
        try:
            poll = Poll.objects.get(poll_id=poll_id)
        except Poll.DoesNotExist:
            return Response({"message": "Poll with that ID does not exist."}, status.HTTP_404_NOT_FOUND)
        
        if poll.is_expired:
            return Response({"message": "This poll has expired, you cannot vote.", status.HTTP_400_BAD_REQUEST})

        if Vote.objects.filter(poll=poll, voter=self.request.user).exists():
            return Response({"message": "You have already voted for this poll."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(poll=poll, voter=self.request.user)

        real_time_results = get_results(poll)
 
        return Response(
            {
                "vote": serializer.data, 
                "real_time_results": real_time_results
            },
            status=status.HTTP_201_CREATED
        )
        