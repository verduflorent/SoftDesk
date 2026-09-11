from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Comment, Contributor, Issue, Project

User = get_user_model()


class SoftDeskUserJourneyTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="Owner", password="testpass123", age=25)
        self.member = User.objects.create_user(username="Member", password="testpass123", age=25)
        self.outsider = User.objects.create_user(username="Outsider", password="testpass123", age=25)
        self.project = Project.objects.create(name="Project A", description="Test", type=Project.Type.BACK_END, author=self.owner)
        Contributor.objects.create(user=self.owner, project=self.project, author=self.owner)
        Contributor.objects.create(user=self.member, project=self.project, author=self.owner)
        self.issue = Issue.objects.create(title="Bug", description="Test", priority=Issue.Priority.HIGH, tag=Issue.Tag.BUG, project=self.project, author=self.member, assignee=self.owner)
        self.comment = Comment.objects.create(description="Comment", issue=self.issue, author=self.member)

    def login_as(self, user):
        self.client.force_authenticate(user=user)

    def test_project_creation_adds_creator_as_contributor(self):
        self.login_as(self.outsider)
        response = self.client.post(reverse("project-list"), {"name": "New Project", "description": "Test", "type": Project.Type.FRONT_END}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        project = Project.objects.get(pk=response.data["id"])
        contribution = Contributor.objects.get(user=self.outsider, project=project)
        self.assertEqual(project.author, self.outsider)
        self.assertEqual(contribution.author, self.outsider)

    def test_project_access_depends_on_membership(self):
        self.login_as(self.member)
        response = self.client.get(reverse("project-detail", args=[self.project.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.login_as(self.outsider)
        response = self.client.get(reverse("project-detail", args=[self.project.pk]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_only_project_author_can_modify_project(self):
        self.login_as(self.member)
        response = self.client.patch(reverse("project-detail", args=[self.project.pk]), {"name": "Blocked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.login_as(self.owner)
        response = self.client.patch(reverse("project-detail", args=[self.project.pk]), {"name": "Allowed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_only_issue_author_can_modify_issue(self):
        self.login_as(self.owner)
        response = self.client.patch(reverse("issue-detail", args=[self.issue.pk]), {"title": "Blocked"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.login_as(self.member)
        response = self.client.patch(reverse("issue-detail", args=[self.issue.pk]), {"title": "Allowed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_contributor_cannot_be_assigned_to_issue(self):
        self.login_as(self.member)
        response = self.client.patch(reverse("issue-detail", args=[self.issue.pk]), {"assignee": self.outsider.pk}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assignee", response.data)

    def test_issue_author_cannot_move_issue_to_inaccessible_project(self):
        private_project = Project.objects.create(name="Private", description="Test", type=Project.Type.BACK_END, author=self.outsider)
        Contributor.objects.create(user=self.outsider, project=private_project, author=self.outsider)

        self.login_as(self.member)
        response = self.client.patch(
            reverse("issue-detail", args=[self.issue.pk]),
            {"project": private_project.pk, "assignee": None},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_comment_author_can_delete_comment(self):
        url = reverse("comment-detail", args=[self.comment.uuid])
        self.login_as(self.owner)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.login_as(self.member)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_comment_author_cannot_move_comment_to_inaccessible_issue(self):
        private_project = Project.objects.create(name="Private", description="Test", type=Project.Type.BACK_END, author=self.outsider)
        Contributor.objects.create(user=self.outsider, project=private_project, author=self.outsider)
        private_issue = Issue.objects.create(title="Private bug", description="Test", priority=Issue.Priority.LOW, tag=Issue.Tag.BUG, project=private_project, author=self.outsider)

        self.login_as(self.member)
        response = self.client.patch(
            reverse("comment-detail", args=[self.comment.uuid]),
            {"issue": private_issue.pk},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_outsider_lists_are_empty(self):
        self.login_as(self.outsider)
        for route in ("project-list", "issue-list", "comment-list"):
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data["count"], 0)
