# Generated by Django 3.2.7 on 2021-09-17 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_alter_profile_account_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentout',
            name='narration',
            field=models.CharField(max_length=200),
        ),
    ]
