# Generated by Django 2.1.3 on 2019-01-22 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestCase', '0003_auto_20190121_1539'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcase',
            name='test_plan_pic_path',
            field=models.FileField(blank=True, null=True, upload_to='upload'),
        ),
    ]
