# Generated by Django 2.2.12 on 2020-06-16 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rpm', '0010_revision_null_redo'),
    ]

    operations = [
        migrations.AddField(
            model_name='rpmremote',
            name='sles_auth_token',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
