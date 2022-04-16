import datetime
from sqlalchemy import create_engine
from django.conf import settings
#from pyofs.date_tools import datetime_to_iso, datetime_to_fr
from django.db import ProgrammingError
import os
import time
import logging
import io

_log = logging.getLogger(__name__)


def get_connection(superuser=False):
    password = settings.DATABASES['default']['PASSWORD']
    database_name = settings.DATABASES['default']['NAME']
    role_db = settings.DATABASES['default']['USER']
    host = settings.DATABASES['default']['HOST']
    if superuser :
        role_db = 'postgres'
        password = 'postgres'
    database_url = 'postgresql://%s:%s@%s:5432/%s'%(role_db,password,host,database_name,)
    engine = create_engine(database_url)
    conn = engine.raw_connection()
    cursor = conn.cursor()
    return engine, conn, cursor

def backup_indexs_table(table, sql_file_name):
    if not os.path.exists(settings.BACKUP_DIR_TEMPORARY) :
        _log.info('creating folder : %s ' %(settings.BACKUP_DIR_TEMPORARY))
        os.makedirs(settings.BACKUP_DIR_TEMPORARY)
    
    database_name = settings.DATABASES['default']['NAME']
    sql_file_name = os.path.join(settings.BACKUP_DIR_TEMPORARY, sql_file_name)
    engine, conn, cursor = get_connection()  
    try:
        sql_file = open(sql_file_name, 'w')
        _log.info('dumping tables %s from db %s to file %s' % (table, database_name, sql_file_name))
        table="'%s'"%table
        cursor.execute('select indexname,indexdef from pg_indexes where tablename=%s;'%table)
        res = cursor.fetchall()
        for r in res :
            cursor.execute('''select 1 from pg_constraint where conname='%s';'''%r[0])
            contraint = cursor.fetchone()
            if contraint is None:
                index = '"%s"'%r[0]
                sql_file.write("%s;\n"%r[1])
                _log.info('drop index %s  from table %s and db %s' % (index, table, database_name))
                cursor.execute('DROP INDEX %s;'%index)
        conn.commit()
    except  Exception as e:
        _log.error('erreur dumping tables %s from db %s, erreur msg : %s... IGNORING THIS ERRR' % (table, database_name, str(e)))

    finally:
        cursor.close()
    _log.info('end dumping tables %s from db %s' % (table, database_name))

def restore_indexs_table(table, sql_file_name):
    database_name = settings.DATABASES['default']['NAME']
    sql_file = os.path.join(settings.BACKUP_DIR_TEMPORARY, sql_file_name)
    table = "'%s'"%table
    _, conn_su, cursor_su = get_connection(superuser=True)
    _log.info('restore indexs table %s to db %s from file %s' % (table, database_name, sql_file))
    with open(sql_file, "r", encoding='latin-1') as infile:
        for line in infile:
            query = "%s" %(line,)
            _log.info('executing query %s', query)
            cursor_su.execute(query)
        conn_su.commit()
        cursor_su.close()

def switch_trigger(tablename, disable, conn= None):
    conn_su = conn
    if conn_su is None:
        _, conn_su, cursor_su = get_connection(superuser=True)
    cursor_su = conn.cursor()
    if disable:
        cursor_su.execute("ALTER TABLE %s DISABLE TRIGGER ALL;" %(tablename))
    else:
        cursor_su.execute("ALTER TABLE %s ENABLE TRIGGER ALL;" %(tablename))

    conn_su.commit()
    conn_su.close()

def dataframe_to_table(df, dry, tablename, disable_trigger):
    if df.empty :
        return
    _log.info('debut chargement %s....'%(tablename))
    _, conn, cursor = get_connection()
    f = io.StringIO()
    _log.info('chargement dataframe dans le tampon csv....')
    start = time.time()
    df.to_csv(f, index=False, header=False, sep=';', encoding='latin-1')
    _log.info ('loading dataframe dans le tampon duration %s'%(time.time()-start))
    f.seek(0)
    _log.info('copy tampon csv vers db table %s....'%(tablename))
    if not dry:
        columns = []
        # for col in list(df.columns) :
        #     columns.append('"%s"'%col)
        columns = list(df.columns)
        if disable_trigger :
            _, conn_su, cursor_su = get_connection(superuser=True)
            cursor_su.execute("ALTER TABLE %s DISABLE TRIGGER ALL;" %(tablename))
            conn_su.commit()
            try:
                cursor.copy_from(f, tablename, columns=tuple(columns), sep=';',null='')
                conn.commit()
            except  Exception as e:
                _log.info('cursor last query %s', cursor.query)
                raise(e)
            
            cursor_su.execute("ALTER TABLE %s ENABLE TRIGGER ALL;" %(tablename))
            conn_su.commit()
            conn_su.close()
        else :
            cursor.copy_from(f, tablename, columns=tuple(columns), sep=';',null='')
            conn.commit()
        _log.info('Fin copy tampon csv vres db....')
    conn.close()
    _log.info ('temps de chargement des donnees %s'%(time.time()-start))

def truncate_data_model(model):
    _, conn_su, cursor_su = get_connection(superuser=True)
    fk_list = get_list_fk_from_model(model)
    database_name = settings.DATABASES['default']['NAME']
    _log.info('database_name %s'%database_name)
    _log.info('desactivation triggers')
    if fk_list:
        cursor_su.execute("ALTER TABLE %s DISABLE TRIGGER ALL;"%(model._meta.db_table))
        for fk in fk_list:
            _log.info('desactivation trigger table name %s'%fk.related_model._meta.db_table)
            cursor_su.execute("ALTER TABLE %s DISABLE TRIGGER ALL;"%(fk.related_model._meta.db_table))
    
    delete_query = "DELETE FROM %s;" %(model._meta.db_table)
    _log.info('executing delete query %s ...', delete_query)
    cursor_su.execute(delete_query)
    
    _log.info('activation triggers')
    cursor_su.execute("ALTER TABLE %s ENABLE TRIGGER ALL;"%(model._meta.db_table))
    if fk_list:
        for fk in fk_list:
            cursor_su.execute("ALTER TABLE %s ENABLE TRIGGER ALL;"%(fk.related_model._meta.db_table))

    conn_su.commit()
    cursor_su.close()

DATES = {}
def make_date_ready(model, d):
    global DATES
    if (model.__name__, d) not in DATES:
        _log.info(' %s : purge de la date d arrete %s' %(model.__name__, d))
        model.objects.filter(date = d).delete()

        DATES[(model.__name__, d)] = True
