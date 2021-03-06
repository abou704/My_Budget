# Generated by Django 4.0.4 on 2022-04-16 03:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mybudget_app', '0005_monthly_table_month'),
    ]

    operations = [
        migrations.RenameField(
            model_name='budget',
            old_name='Credit',
            new_name='credit',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='Date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='Debit',
            new_name='debit',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='Produit',
            new_name='produit',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='Ref',
            new_name='ref',
        ),
        migrations.RenameField(
            model_name='budget',
            old_name='Solde',
            new_name='solde',
        ),
        migrations.RenameField(
            model_name='monthly_table',
            old_name='Commentaire',
            new_name='commentaire',
        ),
        migrations.RenameField(
            model_name='monthly_table',
            old_name='Date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='monthly_table',
            old_name='Dsc',
            new_name='dsc',
        ),
        migrations.RenameField(
            model_name='monthly_table',
            old_name='Fixed_cost',
            new_name='fixed_cost',
        ),
        migrations.RenameField(
            model_name='monthly_table',
            old_name='Month',
            new_name='month',
        ),
    ]
