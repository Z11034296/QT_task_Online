# Generated by Django 2.1.3 on 2019-05-14 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0011_auto_20190506_1639'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controltablelist',
            name='stage_begin',
            field=models.DateField(blank=True, null=True, verbose_name='开始日期'),
        ),
        migrations.AlterField(
            model_name='controltablelist',
            name='stage_end',
            field=models.DateField(blank=True, null=True, verbose_name='结束日期'),
        ),
    ]