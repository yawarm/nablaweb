# Generated by Django 3.0.7 on 2021-01-29 14:38

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VotingEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                (
                    "creation_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="Opprettet"),
                ),
                (
                    "checked_in_users",
                    models.ManyToManyField(
                        related_name="checked_in_users", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Voting",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField()),
                (
                    "is_active",
                    models.BooleanField(
                        default=False, verbose_name="Åpen for avtemning?"
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        editable=False,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Voting_created_by",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Opprettet av",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votings",
                        to="vote.VotingEvent",
                    ),
                ),
                (
                    "users_voted",
                    models.ManyToManyField(
                        related_name="users_voted", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Alternative",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.CharField(max_length=250)),
                (
                    "votes",
                    models.IntegerField(default=0, verbose_name="Antall stemmer"),
                ),
                (
                    "voting",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alternatives",
                        to="vote.Voting",
                    ),
                ),
            ],
        ),
    ]
