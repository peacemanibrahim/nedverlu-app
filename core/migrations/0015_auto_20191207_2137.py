# Generated by Django 2.2.7 on 2019-12-07 20:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20191207_1843'),
    ]

    operations = [
        migrations.RenameField(
            model_name='addslider',
            old_name='image1',
            new_name='image',
        ),
        migrations.RemoveField(
            model_name='addslider',
            name='image2',
        ),
        migrations.RemoveField(
            model_name='addslider',
            name='image3',
        ),
        migrations.RemoveField(
            model_name='addslider',
            name='image4',
        ),
        migrations.RemoveField(
            model_name='addslider',
            name='image5',
        ),
        migrations.RemoveField(
            model_name='addslider',
            name='image6',
        ),
    ]