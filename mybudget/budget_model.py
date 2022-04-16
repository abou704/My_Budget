from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


import logging

logger = logging.getLogger(__name__)


TOLERANCE_FLOAT_EQUAL = 1e-10

class BudgetModelManager(models.Manager):

    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except ObjectDoesNotExist:
            return None
    
    def get_or_none_with_related(self, sel_related, **kwargs):
        try:
            return self.select_related(*sel_related).get(**kwargs)
        except ObjectDoesNotExist:
            return None



class BudgetModel(models.Model):
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(default=timezone.now)

    def _for_same(self):
        return []

    def same(self, ctr):
        left = self._for_same()
        right = ctr._for_same()
        are_same =  (left == right) and len(right) > 0
        return  are_same

    class Meta:
        abstract = True