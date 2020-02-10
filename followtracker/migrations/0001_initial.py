# Generated by Django 2.2.7 on 2020-02-10 04:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstaUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('email', models.CharField(default='', max_length=200)),
                ('num_followers', models.IntegerField(default=0)),
                ('num_followees', models.IntegerField(default=0)),
                ('create_ts', models.DateTimeField(auto_now_add=True)),
                ('last_update_ts', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Follower',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='_followers', to='followtracker.InstaUser')),
            ],
        ),
        migrations.CreateModel(
            name='Followee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='_followees', to='followtracker.InstaUser')),
            ],
        ),
    ]
