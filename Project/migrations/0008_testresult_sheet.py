# Generated by Django 2.1.3 on 2019-04-12 02:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TestCase', '0008_sheet_sheet_description'),
        ('Project', '0007_auto_20190411_1432'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='sheet',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='TestCase.Sheet'),
        ),
    ]
