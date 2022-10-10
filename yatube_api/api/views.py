from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.serializers import CommentSerializer, GroupSerializer, PostSerializer
from posts.models import Comment, Group, Post
from .permissions import IsOwnerOrReadOnly


class PostAPIView(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly,)

    def get_object(self):
        return Post.objects.get(pk=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super(PostAPIView, self).destroy(request, *args, **kwargs)


class GroupAPICreateReadList(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticated,)


class GroupAPIReadDetail(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticated,)


class CommentAPICreateReadList(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user,
                        post=post)

    def get_queryset(self):
        pk = self.kwargs['post_id']
        post = get_object_or_404(Post, id=pk)
        return post.comments
