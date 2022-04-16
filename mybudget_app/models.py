from django.db import models
from mybudget.budget_model import BudgetModelManager, BudgetModel
from django.utils import timezone


class Budget(BudgetModel):
    date = models.DateTimeField(default=timezone.now)
    produit = models.CharField(max_length=255)
    ref = models.CharField(max_length=255)
    debit= models.FloatField()
    credit =  models.FloatField()
    solde = models.FloatField()
    month = models.CharField(max_length=255, default= 'none')
    year = models.CharField(max_length=255, default= 'none')
    day = models.CharField(max_length=255, default= 'none')

    objects = BudgetModelManager()

class monthly_table(BudgetModel):
    date = models.DateTimeField(default=timezone.now)
    month = models.CharField(max_length=255, default= 'none')
    fixed_cost = models.FloatField()
    dsc = models.FloatField()
    invest = models.FloatField()
    commentaire = models.CharField(max_length=255)

    objects = BudgetModelManager()
    
# Create your models here.
