# Generated by Django 2.1.3 on 2021-01-27 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0019_auto_20201224_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='impact_model',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='impact_model'),
        ),
    ]