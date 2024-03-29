# Generated by Django 2.2.17 on 2021-05-23 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('githubs', '0007_auto_20210310_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='githubuser',
            name='tier',
            field=models.SmallIntegerField(choices=[(35, 'Challenger'), (30, 'Master'), (25, 'Platinum'), (20, 'Diamond'), (15, 'Gold'), (10, 'Silver'), (5, 'Bronze'), (0, 'UnRank')], default=0),
        ),
    ]
