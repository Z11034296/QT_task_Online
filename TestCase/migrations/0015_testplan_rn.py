# Generated by Django 2.1.3 on 2021-03-09 05:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TestCase', '0014_auto_20201224_1323'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestPlan_RN',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rn_version', models.CharField(max_length=128, unique=True, verbose_name='rn_version')),
                ('rn_date', models.DateField(blank=True, null=True)),
                ('rn_description', models.TextField(blank=True, null=True, verbose_name='rn_description')),
                ('rn_keeper', models.CharField(max_length=128, null=True, verbose_name='rn_keeper')),
                ('rn_mote', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
