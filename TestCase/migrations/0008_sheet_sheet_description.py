# Generated by Django 2.1.3 on 2019-03-12 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestCase', '0007_auto_20190301_1008'),
    ]

    operations = [
        migrations.AddField(
            model_name='sheet',
            name='sheet_description',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
