# Generated by Django 2.1.9 on 2019-10-03 19:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_company_ignorecrop'),
        ('events', '0002_auto_20190205_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='company',
            field=models.ForeignKey(blank=True, help_text='Kun relevant for bedriftspresentasjoner.', null=True, on_delete=django.db.models.deletion.CASCADE, to='jobs.Company', verbose_name='Bedrift'),
        ),
        migrations.AddField(
            model_name='event',
            name='is_bedpres',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='penalty',
            field=models.IntegerField(blank=True, choices=[(0, 'Ingen prikker'), (1, 'Bedpres'), (2, 'Arrangement med betaling'), (3, 'Arrangement uten betaling')], default=0, null=True),
        ),
        migrations.AddField(
            model_name='eventregistration',
            name='penalty',
            field=models.IntegerField(blank=True, default=0, verbose_name='Prikk'),
        ),
    ]
