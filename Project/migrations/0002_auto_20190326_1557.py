# Generated by Django 2.1.3 on 2019-03-26 07:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('UserProfile', '0004_userinfo_site'),
        ('TestCase', '0008_sheet_sheet_description'),
        ('Project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlTableContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku_num', models.CharField(blank=True, default=None, max_length=16, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ControlTableList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_stage', models.CharField(max_length=255, verbose_name='Project_stage')),
                ('stage_begin', models.DateField(verbose_name='开始日期')),
                ('stage_end', models.DateField(verbose_name='结束日期')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Project.Project')),
            ],
        ),
        migrations.AddField(
            model_name='controltablecontent',
            name='ControlTable_List_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Project.ControlTableList'),
        ),
        migrations.AddField(
            model_name='controltablecontent',
            name='sheet_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='TestCase.Sheet'),
        ),
        migrations.AddField(
            model_name='controltablecontent',
            name='tester',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='UserProfile.UserInfo'),
        ),
    ]