# Generated by Django 3.2.19 on 2023-05-14 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mbsa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='temporaryfile',
            name='file',
            field=models.FileField(upload_to=''),
        ),
    ]