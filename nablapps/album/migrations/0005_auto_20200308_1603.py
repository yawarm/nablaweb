# Generated by Django 2.1.13 on 2020-03-08 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('album', '0004_remove_album_view_counter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='album',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='album',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
