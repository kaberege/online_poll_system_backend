from rest_framework.generics import ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Poll, Vote
from .serializers import PollModelSerializer, VoteModelSerializer

class PollModelViewSet(ModelViewSet):
    queryset = Poll.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PollModelSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(edited=True)
    
    def perform_partial_update(self, serializer):
        serializer.save(edited=True)

class VoteModelViewSet(ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = VoteModelSerializer

    def get_queryset(self):
        poll_id = self.kwargs['poll_id']
        return Vote.objects.filter(poll=poll_id)

    def list(self, request):
        votes_per_poll = self.get_queryset()
        serializer_votes = self.get_serializer(votes_per_poll, many=True)
        return Response(serializer_votes.data, status=status.HTTP_200_OK)

    def create(self, request, poll_id):
        try:
            poll = Poll.objects.get(poll_id=poll_id)
        except Poll.DoesNotExist:
            return Response({'message':'Poll with that ID does not exist'}, status.HTTP_404_NOT_FOUND)

        if Vote.objects.filter(poll=poll, voter=self.request.user).exists():
            return Response({"message": "You have already voted for this poll"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(poll=poll, voter=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        