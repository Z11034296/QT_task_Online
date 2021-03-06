# Generated by Django 2.1.3 on 2019-01-16 03:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Function',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('function_name', models.CharField(max_length=64, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheet_name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case_id', models.CharField(max_length=32, unique=True)),
                ('case_name', models.CharField(max_length=64)),
                ('procedure', models.TextField(blank=True, null=True)),
                ('passcritearia', models.TextField(blank=True, null=True)),
                ('test_plan_pic_path', models.CharField(blank=True, max_length=64, null=True)),
                ('attend_time', models.CharField(max_length=32)),
                ('function', models.ForeignKey(null=True, on_delete=None, to='TestCase.Function')),
                ('sheet', models.ForeignKey(null=True, on_delete=None, to='TestCase.Sheet')),
            ],
        ),
    ]
