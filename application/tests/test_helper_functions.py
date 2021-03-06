import os
import logging
import psycopg2
import psycopg2.extras as psycop_extras
from nose.tools import nottest
from application.services import config_service
from application.services import logging_service
from application.services import debug_service
from application.services import conversion_service
from application.services import database_service
from application.models.classes import dycast_parameters


debug_service.enable_debugger()

current_dir = os.path.basename(os.path.dirname(os.path.realpath(__file__)))


@nottest
def init_test_environment():
    config_path = os.path.join(current_dir, '..', 'dycast.config')

    config_service.init_config(config_path)
    logging_service.init_logging()

@nottest
def get_dycast_parameters():
    dycast = dycast_parameters.DycastParameters()

    dycast.srid_of_cases = '3857'
    dycast.files_to_import = get_test_cases_import_files_latlong()

    dycast.spatial_domain = 600
    dycast.temporal_domain = 28
    dycast.close_in_space = 100
    dycast.close_in_time = 4
    dycast.case_threshold = 10

    dycast.startdate = conversion_service.get_date_object_from_string('2016-03-30')
    dycast.enddate = conversion_service.get_date_object_from_string('2016-03-31')
    dycast.extent_min_x = 1830400
    dycast.extent_min_y = 2120600
    dycast.extent_max_x = 1830700
    dycast.extent_max_y = 2120300
    dycast.srid_of_extent = 3857

    return dycast  

@nottest
def get_test_data_directory():
    return os.path.join(current_dir, 'test_data')

@nottest
def get_test_data_import_directory():
    return os.path.join(get_test_data_directory(), 'import')

@nottest
def get_test_data_export_directory():
    return os.path.join(get_test_data_directory(), 'export')

@nottest
def get_test_cases_import_files_latlong():
    file_1 = os.path.join(get_test_data_import_directory(), 'input_cases_latlong1.tsv')
    file_2 = os.path.join(get_test_data_import_directory(), 'input_cases_latlong2.tsv')
    return [file_1, file_2]

@nottest
def get_test_cases_import_file_geometry():
    return os.path.join(get_test_data_import_directory(), 'input_cases_geometry.tsv')

@nottest
def get_count_from_table(table_name):
    cur, conn = database_service.init_db()
    querystring = "SELECT count(*) from " + table_name
    try:
        cur.execute(querystring)
    except Exception:
        conn.rollback()
        logging.exception("Can't select count from table, exiting...")
        raise
    new_row = cur.fetchone()
    return new_row[0]

@nottest
def insert_test_risk():
    cur, conn = database_service.init_db()
    querystring = "INSERT INTO risk VALUES %s"
    data_tuple = [('2016-03-30', 1830400, 2120400, 10, 1, 6, 7, 0.3946), ('2016-03-31', 1830400, 2120400, 10, 1, 6, 7, 0.3946)]
    try:
        psycop_extras.execute_values(cur, querystring, data_tuple)
    except psycopg2.IntegrityError:
        conn.rollback()
        logging.warning("Couldn't insert duplicate key in tuple: %s...", data_tuple)            
    except Exception:
        conn.rollback()
        logging.exception("Couldn't insert tuple")
        raise
    conn.commit()