# Generated by Django 2.1.3 on 2019-03-18 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0003_site'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='UserProfile.Site'),
        ),
    ]
