import uuid

from django.conf import settings
from django.db import models


class Project(models.Model):
    class Type(models.TextChoices):
        BACK_END = "BACK_END", "Back-end"
        FRONT_END = "FRONT_END", "Front-end"
        IOS = "IOS", "iOS"
        ANDROID = "ANDROID", "Android"

    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(
        max_length=10,
        choices=Type.choices,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects_created",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Contributor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contributions",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="contributors",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"],
                name="unique_project_contributor",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.project.name}"


class Issue(models.Model):
    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Tag(models.TextChoices):
        BUG = "BUG", "Bug"
        FEATURE = "FEATURE", "Feature"
        TASK = "TASK", "Task"

    class Status(models.TextChoices):
        TO_DO = "TO_DO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        FINISHED = "FINISHED", "Finished"

    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
    )
    tag = models.CharField(
        max_length=10,
        choices=Tag.choices,
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.TO_DO,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="issues",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issues_created",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="issues_assigned",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    description = models.TextField()
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments_created",
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uuid)
