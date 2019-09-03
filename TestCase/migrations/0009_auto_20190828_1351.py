# Generated by Django 2.1.3 on 2019-08-28 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestCase', '0008_sheet_sheet_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sheet',
            name='sheet_description',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='sheet',
            name='sheet_name',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='testcase',
            name='case_id',
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='testcase',
            name='case_name',
            field=models.CharField(max_length=255),
        ),
    ]
