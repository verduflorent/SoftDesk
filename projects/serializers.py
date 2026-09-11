from rest_framework import serializers

from .models import Contributor, Issue, Project


class ProjectSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "type",
            "author",
            "created_time",
        ]
        read_only_fields = [
            "author",
            "created_time",
        ]


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = [
            "id",
            "user",
            "project",
            "created_time",
        ]
        read_only_fields = [
            "created_time",
        ]


class IssueSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "description",
            "priority",
            "tag",
            "status",
            "project",
            "author",
            "assignee",
            "created_time",
        ]
        read_only_fields = [
            "author",
            "created_time",
        ]

    def validate(self, data):
        project = data.get("project")
        assignee = data.get("assignee")

        if assignee and project:
            is_contributor = Contributor.objects.filter(
                user=assignee,
                project=project,
            ).exists()

            if not is_contributor:
                raise serializers.ValidationError(
                    {
                        "assignee": (
                            "L'utilisateur assigné doit être "
                            "contributeur du projet."
                        )
                    }
                )

        return data
