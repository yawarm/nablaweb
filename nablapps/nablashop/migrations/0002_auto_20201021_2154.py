# Generated by Django 3.0.7 on 2020-10-21 21:54

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nablashop', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=ckeditor.fields.RichTextField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='description_short',
            field=ckeditor.fields.RichTextField(),
        ),
    ]