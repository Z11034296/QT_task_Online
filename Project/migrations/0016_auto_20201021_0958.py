# Generated by Django 2.1.3 on 2020-10-21 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0015_auto_20201019_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='controltablelist',
            name='finished_time',
            field=models.CharField(default='0', max_length=128, null=True, verbose_name='attend_time'),
        ),
        migrations.AlterField(
            model_name='controltablelist',
            name='attend_time',
            field=models.CharField(default='1', max_length=128, null=True, verbose_name='attend_time'),
        ),
    ]
