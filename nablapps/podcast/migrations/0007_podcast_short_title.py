# Generated by Django 2.1.7 on 2019-04-22 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcast', '0006_auto_20190319_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='short_title',
            field=models.CharField(blank=True, help_text='kort tittel som vises i boksen på forsiden med de fire siste sendingene.', max_length=50, verbose_name='kort tittel'),
        ),
    ]
