from datetime import date
import re
from django.core.management.base import BaseCommand
from django.utils import timezone
import pandas as pd
import datetime
import math
import re
from sqlalchemy import create_engine
from mybudget_app.models import Budget, monthly_table

import datetime
import time
from mybudget_app.models import Budget, monthly_table
import logging
from mybudget.model_tools import get_connection, dataframe_to_table, make_date_ready


xl_origin = datetime.datetime(1899,12,30)
def iso_to_datetime(iso_date):

    return datetime.datetime(int(iso_date[:4]),int(iso_date[4:6]),int(iso_date[6:8]),)


def df_selected(df, threshold, seT ):
    if seT == 'lower':
        return df.where(df['Debit']< threshold).dropna()
    if seT == 'upper':
        return df.where(df['Debit']>= threshold).dropna()
    if seT == 'equal':
        return df.where(df['Debit'] == threshold).dropna()

class PDC:

    def __init__(self, salaire, dataframe, home_price, netflix_price, coiffure):
        self.salaire = salaire
        self.df = dataframe
        self.home_price = float(home_price)
        self.netflix_price = float(netflix_price)
        self.coiffure = float(coiffure)

    def get_df(self, type):
        if type == 'achat':
            return self.df[self.df['Produit'].str.contains('ACHAT PAR CARTE DE PAIEMENT')]
        if type == 'retrait':
            return self.df[self.df['Produit'].str.contains('RETRAIT GAB')]
        if type == 'internet':
           return self.df[self.df['Produit'].str.contains('PAIEMENT FACT')] 

    def Compute_cout_fixe(self):
        # Récupération des couts d'alimentation
        df_alim= df_selected(self.get_df('achat'), 400, 'lower' )
        df_family = df_selected(self.get_df('retrait'), 1000, 'upper' )
        value = float(df_alim['Debit'].sum()) + float(df_family['Debit'].sum()) + self.coiffure
        if value > 0.4 * self.salaire:
            comment = 'Attention vous avez dépassé le seuil des cout fixes'
            #print(comment)
        else: 
            comment = "vous etes dans l'intervalle fixé sur les couts fixes "
            #print(comment)
        return value, comment   
             
    def Compute_DSC(self):
        df_sortie_from_achat = df_selected(self.get_df('achat'), 400, 'upper' )
        df_sortie_from_retrait = df_selected(self.get_df('retrait'), 1000, 'lower' )
        df_internet = self.get_df('internet')
        value = float(df_sortie_from_achat['Debit'].sum()) + float(df_sortie_from_retrait['Debit'].sum()) + self.netflix_price + float(df_internet['Debit'].sum())

        if value > 0.3 * self.salaire:
            comment = 'Attention vous avez dépassé le seuil des depenses sans culpabilisées'
            #print(comment)
        else: 
            comment = "vous etes dans l'intervalle fixé sur les depenses sans culpabilisées "
            #print(comment)
        return value, comment
        
    def invest_and_epargne(self):
        cout_fixe,_ = self.Compute_cout_fixe()
        dsc,_= self.Compute_DSC()
        return self.salaire - (cout_fixe + dsc)


def prevision_depense(df,cout_fixe, dsc, invest, salaire):
    montant_depense = float(df['Debit'].sum())
    print('montant_depense', montant_depense)
    cout_fixe = (0.35 -cout_fixe/ montant_depense)*salaire
    dsc = (0.25 - dsc/montant_depense) * salaire
    invest = (0.5 - invest/montant_depense)*salaire
    return cout_fixe, dsc, invest





class Command(BaseCommand):
    help = "Insert datas from CSV"

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
        parser.add_argument(
                    '--dry',
                    action='store_true',
                    dest='dry',
                    default=False,
                    help='Dry run, do not alter database..',
                )
        
        parser.add_argument(
                    '--insert',
                    action='store_true',
                    dest='insert',
                    default=False,
                    help='insert without delete previous table..',
                )

        parser.add_argument(
                    '--force',
                    action='store_true',
                    dest='force',
                    default=False,
                    help='forcer la maj de la table..',)

        parser.add_argument('csv_in', type=str)
        parser.add_argument('dateiso', type=str)
        #parser.add_argument('outfolder')


    def handle(self, *args, **options):
        csv_in = options['csv_in']
        #outfolder = options['outfolder']
        dateiso = options['dateiso']
        dry = options['dry']
        insert = options['insert']
        force = options['force']
        date = iso_to_datetime(dateiso)

        df = pd.read_excel(csv_in, sheet_name = 'historique compte')
        df['month'] = pd.DatetimeIndex(df['Date opération']).month
        df['year'] = pd.DatetimeIndex(df['Date opération']).year
        df['day'] = pd.DatetimeIndex(df['Date opération']).day
        print( df['day'])
        df= df.rename(columns = {'Date opération':'date','Réf':'ref', 'Libellé':'produit','Débit (MAD)':'debit', 'Crédit (MAD)':'credit', 'Solde (MAD)':'solde'})
    
        dd = df[df.duplicated(['date'], keep=False)].groupby(['date']).last()
        for d, _ in dd.iterrows():
            #d = str(d)
            d = d.date()
            print('dddddddd', d)
            if not dry and not insert:
                make_date_ready(Budget, d)

        if not dry:
            now = datetime.datetime.now()
            df['created'] = now
            df['modified'] = now
            dataframe_to_table(df, dry, 'mybudget_app_budget', disable_trigger = True)
        # #stockage data to db_table
        # engine = create_engine('sqlite:///DB_name')
        # df.to_sql(Budget._meta.db_table, if_exists='replace', con=engine, index=False)

        month_check = int(dateiso[4:6])
        year_check = int(dateiso[:4])
        day_check = int(dateiso[6:])

        if month_check <= 1:
            prev_month_check = 12
            prev_year_check = year_check -1
        else:
            prev_month_check = month_check-1
            prev_year_check = year_check    

        df = df.where((df['Date'] >= datetime.datetime(prev_year_check,prev_month_check,28)) & (df['Date'] <= datetime.datetime(year_check,month_check,day_check)) ).dropna()
        print(df)
        # #exit()


        #print(df1, int(dateiso[4:6]))
        print(df.columns)
        my_pdc = PDC(13500, df, 1000, 95, 30)
        dsc, comment_dsc = my_pdc.Compute_DSC()
        print(dsc)
        cout_fixe, comment_cost = my_pdc.Compute_cout_fixe()
        invest = my_pdc.invest_and_epargne()

        # création dataframe
        date= datetime.datetime(year_check, month_check, day_check)
        month = str(date.strftime("%B"))
        dico = {'date': date, 'month': month,  'fixed_cost': cout_fixe, 'dsc':dsc, 'invest': invest, 'commentaire': comment_cost + ' / ' + comment_dsc }
        df_monthly = pd.DataFrame(dico, index=[0])
        print(df_monthly)
        dd = df[df.duplicated(['date'], keep=False)].groupby(['date']).last()
        for d, _ in dd.iterrows():
            d = str(d)
            d=d.date()
            if not dry and not insert:
                make_date_ready(monthly_table, d)

        if not dry:
            now = datetime.datetime.now()
            df['created'] = now
            df['modified'] = now
            dataframe_to_table(df, dry, 'mybudget_app_monthly_table', disable_trigger = True)
        # #stockage df_monthly to db_table
        # engine = create_engine('sqlite:///DB_name')
        # df_monthly.to_sql(monthly_table._meta.db_table, if_exists='append', con=engine, index=False)

        #exit()

        print('invest', invest)
        #print('dsc', dsc)
        #print('cout_fixe', cout_fixe)

        cout_fixe_restant, dsc_restant, invest_restant = prevision_depense(df,cout_fixe, dsc, invest, 13500)
        print(invest_restant)
        exit()

