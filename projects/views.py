from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Comment, Contributor, Issue, Project
from .permissions import IsAuthorOrReadOnly, IsProjectAuthorOrReadOnly
from .serializers import (
    CommentSerializer,
    ContributorSerializer,
    IssueSerializer,
    ProjectSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(
            contributors__user=self.request.user,
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.save(author=self.request.user)

        Contributor.objects.create(
            user=self.request.user,
            project=project,
        )


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthorOrReadOnly]

    def get_queryset(self):
        return Contributor.objects.filter(
            project__contributors__user=self.request.user,
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]

        if project.author != self.request.user:
            raise PermissionDenied(
                "Seul l'auteur du projet peut ajouter un contributeur."
            )

        serializer.save()


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Issue.objects.filter(
            project__contributors__user=self.request.user,
        ).distinct()

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]

        if not Contributor.objects.filter(
            user=self.request.user,
            project=project,
        ).exists():
            raise PermissionDenied(
                "Vous devez être contributeur du projet pour créer une issue."
            )

        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(
            issue__project__contributors__user=self.request.user,
        ).distinct()

    def perform_create(self, serializer):
        issue = serializer.validated_data["issue"]

        if not Contributor.objects.filter(
            user=self.request.user,
            project=issue.project,
        ).exists():
            raise PermissionDenied(
                "Vous devez être contributeur du projet pour commenter cette issue."
            )

        serializer.save(author=self.request.user)
