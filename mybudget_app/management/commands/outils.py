from datetime import date
import re
from django.core.management.base import BaseCommand
from django.utils import timezone
import pandas as pd
import datetime

def month(xldate):

    "returns month of xldate"

    d=xl_origin+datetime.timedelta(xldate)

    return d.month

def datetime_to_xl(datetime_date):

    """Warning : date becomes integer (hours are forgotten)"""

    return iso_to_xl(datetime_to_iso(datetime_date))