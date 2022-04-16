import numpy as np
import pandas as pd
import datetime
import time
from referentiel.models import PMO
import logging
from djofs.model_tools import get_connection, dataframe_to_table, make_date_ready
from pyofs.date_tools import iso_to_datetime

_log = logging.getLogger(__name__) # pylint:disable=C0103

def loading_pmo(file, dry, insert, outfolder) :
    
    # engine, conn, cursor = get_connection()
    start = time.time()
    csvstart = time.time()
    _log.info (' read fichier csv %s', file)
    df = pd.read_csv(file, dtype={'RADICAL': str, 'FORMJUR': str, 'RC' :str, 'IMPOTSS' :str, 'PATENTE' :str, 'FONCTION' :str, 'NATIONALITE' :str, 'ACT_PRINC' :str, 'STE_BOURSE' :str, 'PREN_NOM_CONT' :str, 'FONCT_ENTREP' :str, 'NOM_ACT_PRIN' :str, 'TYPE_ACT' :str, 'LIEU_IMM_RC' :str, 'ETAT_ENTR' :str, 'EQUI_FIN' :str, 'RESP_RAT' :str, 'TEL_CONTACT' :str}, sep=';')
    
    if df.empty:
        _log.warning ('dataframe empty exiting ...')
        return 
    
    df_columns_order = ['RADICAL', 'FORMJUR', 'RC', 'IMPOTSS', 'PATENTE', 'CAPITAL', 'CHIFFRE_AFF',
                        'FONCTION', 'DATE_CREA', 'NATIONALITE', 'ACT_PRINC', 'STE_BOURSE', 'EFFECTIF',
                        'PREN_NOM_CONT', 'FONCT_ENTREP', 'NOM_ACT_PRIN', 'TYPE_ACT', 'LIEU_IMM_RC',
                        'ETAT_ENTR', 'CHIF_AFF_EXP', 'TOTAL_BILAN', 'EQUI_FIN', 'RESP_RAT', 'TEL_CONTACT', 'date']
    
    df = df[df_columns_order]

    df.columns = ['radical', 'formejur', 'rc', 'impotss', 'patente', 'capital', 'chiffre_aff',
                    'fonction', 'date_crea', 'nationalite', 'act_princ', 'ste_bourse', 'effectif',
                    'pren_nom_cont', 'fonct_entrep', 'nom_act_princ', 'type_act', 'lieu_imm_rc', 
                    'etat_entr', 'chif_aff_exp','total_bilan','equi_fin','resp_rat','tel_contact', 'date']

    df['date_crea_str'] = df.date_crea
    df.date_crea = pd.to_datetime(df.date_crea, format='%d.%m.%Y', errors = 'coerce')

    df.radical = df.radical.str.strip()
    _log.info ('taille de dataframe %s', df.shape)

    dd = df[df.duplicated(['date'], keep=False)].groupby(['date']).last()
    for d, _ in dd.iterrows():
        d = str(d)
        if not dry and not insert:
            make_date_ready(PMO, iso_to_datetime(d))

    if not dry:
        now = datetime.datetime.now()
        df['created'] = now
        df['modified'] = now
        dataframe_to_table(df, dry, 'referentiel_pmo', disable_trigger = True)