# Generated by Django 2.2.1 on 2019-07-15 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_author_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='stone',
            name='order',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
