# Generated by Django 2.1.3 on 2019-03-26 08:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0002_auto_20190326_1557'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='controltablelist',
            unique_together={('project', 'project_stage')},
        ),
    ]