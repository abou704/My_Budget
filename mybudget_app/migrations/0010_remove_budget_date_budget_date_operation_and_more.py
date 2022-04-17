# Generated by Django 4.0.4 on 2022-04-17 11:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mybudget_app', '0009_alter_budget_day_alter_budget_month_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='budget',
            name='date',
        ),
        migrations.AddField(
            model_name='budget',
            name='date_operation',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='monthly_table',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]