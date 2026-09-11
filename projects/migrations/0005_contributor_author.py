import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def set_contributor_authors(apps, schema_editor):
    Contributor = apps.get_model("projects", "Contributor")

    for contributor in Contributor.objects.select_related("project").all():
        contributor.author_id = contributor.project.author_id
        contributor.save(update_fields=["author"])


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_comment"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="contributor",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contributions_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            set_contributor_authors,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="contributor",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contributions_created",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
