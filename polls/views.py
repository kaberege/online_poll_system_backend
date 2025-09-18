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
import logging

logger = logging.getLogger(__name__)

class PollModelViewSet(ModelViewSet):
    queryset = Poll.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = PollModelSerializer

    def perform_create(self, serializer):
        poll = serializer.save(owner=self.request.user)
        logger.info(f"Poll '{poll.title}' created by {self.request.user.email}")
    
    def perform_update(self, serializer):
        poll = serializer.save(edited=True)
        logger.info(f"Poll '{poll.title}' updated by {self.request.user.email}")

    @swagger_auto_schema(
        operation_summary="List all polls",
        operation_description="Retrieve a list of all polls. Anyone can view polls, "
                              "but only authenticated users can create. Polls are ordered by creation date."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new poll",
        operation_description="Create a new poll with title, description, options, and optional expiry date. "
                              "The authenticated user becomes the owner."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve a poll",
        operation_description="Retrieve the details of a specific poll by its ID. "
                              "Anyone can view poll details, including title, description, options, "
                              "and expiry date. The response also includes owner information."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a poll",
        operation_description="Update specific fields of an existing poll (e.g., title or description). "
                              "Only the owner can edit their polls. Expired polls cannot be modified."
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a poll",
        operation_description="Update an existing poll. Only the owner can update their polls. "
                              "Expired polls cannot be edited."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a poll",
        operation_description="Delete a poll by ID. Only the owner (or an admin) can delete their poll."
    )
    def destroy(self, request, *args, **kwargs):
        poll = self.get_object()
        logger.critical(f"Poll '{poll.title}' deleted by {request.user.email}")
        return super().destroy(request, *args, **kwargs)

class VoteModelViewSet(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VoteModelSerializer

    def get_queryset(self):
        poll_id = self.kwargs["poll_id"]
        return Vote.objects.filter(poll=poll_id)
    
    def list(self, request, poll_id):
        votes_per_poll = self.get_queryset()
        serializer_votes = self.get_serializer(votes_per_poll, many=True)

        try:
            poll = Poll.objects.get(poll_id=poll_id)
        except Poll.DoesNotExist:
            logger.error(f"Poll with ID {poll_id} not found when listing votes.")
            return Response({"message": "Poll not found"}, status=status.HTTP_404_NOT_FOUND)

        real_time_results = get_results(poll)

        return Response(
            {
                "votes": serializer_votes.data,
                "real_time_results": real_time_results
            }, 
            status=status.HTTP_200_OK
        )
    
    def create(self, request, poll_id):
        try:
            poll = Poll.objects.get(poll_id=poll_id)
        except Poll.DoesNotExist:
            logger.error(f"Vote attempt on non-existent poll {poll_id}")
            return Response({"message": "Poll with that ID does not exist."}, status=status.HTTP_404_NOT_FOUND)
        
        if poll.is_expired:
            logger.warning(f"User {request.user.email} tried voting on expired poll {poll_id}")
            return Response({"message": "This poll has expired, you cannot vote."}, status=status.HTTP_400_BAD_REQUEST)

        if Vote.objects.filter(poll=poll, voter=self.request.user).exists():
            logger.warning(f"User {request.user.email} tried voting twice on poll {poll_id}")
            return Response({"message": "You have already voted for this poll."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={"poll": poll})
        serializer.is_valid(raise_exception=True)
        vote = serializer.save(poll=poll, voter=self.request.user)

        real_time_results = get_results(poll)

        logger.info(f"User {request.user.email} voted '{vote.option}' on poll {poll_id}")
 
        return Response(
            {
                "vote": serializer.data, 
                "real_time_results": real_time_results
            },
            status=status.HTTP_201_CREATED
        ) 
    
    @swagger_auto_schema(
        operation_summary="List votes for a poll",
        operation_description="Retrieve all votes for the specified poll along with real-time results. "
                              "Anyone can view votes and results.",
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Cast a vote on a poll",
        operation_description="Cast a vote for one of the poll's options. "
                              "Only authenticated users can vote. "
                              "Users can vote once per poll, and cannot vote on expired polls."
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

