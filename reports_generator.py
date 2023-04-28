import requests
import re
import mysql.connector as mc
from mysql.connector import errorcode
from datetime import date, datetime, timedelta


def url_maker(reportApi, isCsv, auth_token):
    auth = {'Authorization': 'Token ' + auth_token}
    url = "http://prescond.hyperaptive.io/"
    if isCsv:
        endpoint = f"api/v5/{reportApi}/csv"
    else:
        endpoint = f"api/v5/{reportApi}"
    full_url = url + endpoint
    return full_url, auth


def create_table(raw_data, table_name):
    header = raw_data[0]
    column_name = ""
    for i in header:
        i = i.replace(" ", "_").replace("-", "_").replace(":", "").replace("(", "").replace(")", "").replace("&",
                                                                                                             "").replace(
            "#", "")
        if len(i) > 64:  # sql only supports up to 128 bytes or unicode utf-8 64 chars
            i = i[:64]
        column_name += f" `{i}` text, "
    column_name = column_name[:-2]
    query = f"CREATE TABLE `{table_name}` ({column_name}) ENGINE=InnoDB"
    return query, header


def insert_values(table_name, header):
    insert_statement = f"INSERT INTO {table_name} ("
    for i in header:
        i = i.replace(" ", "_").replace("-", "_").replace(":", "").replace("(", "").replace(")", "").replace("&",
                                                                                                             "").replace(
            "#", "")
        if len(i) > 64:  # sql only supports up to 128 bytes or unicode utf-8 64 chars
            i = i[:64]
        insert_statement += f"{i}, "
    insert_statement = insert_statement[:-2]

    insert_statement += ') VALUES ('
    for i in range(0, len(header)):
        insert_statement += "%s, "
    insert_statement = insert_statement[:-2]
    insert_statement += ')'
    return insert_statement


def drop_table(cursor, drop_table_query):
    try:
        cursor.execute(drop_table_query)
    except mc.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists drop.")
        else:
            print(err.msg)


def create_and_insert(cursor, create_table_query, table_name, raw_data, insert_statement):
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(create_table_query)
        for i in range(1, len(raw_data)):
            insert_data = []
            for j in raw_data[i]:
                insert_data.append(j)
            cursor.execute(insert_statement, insert_data)
    except mc.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


def reporting(table_name, reportApi, params, isCsv, auth_token):
    all_errors = []
    full_url, auth = url_maker(reportApi, isCsv, auth_token)
    if params is None:
        res = requests.get(full_url, headers=auth, stream=True)
    else:
        res = requests.get(full_url, params=params, headers=auth, stream=True)
    if res.status_code == 404:
        all_errors.append(f"ERROR: The page for report {table_name} does NOT exists!")
    else:
        # res contains a chunk of data per line. We need to iterate over each line and access the data.
        raw_data = []
        totalLines = -1
        for line in res.iter_lines():
            totalLines += 1
            decoded_line = line.decode('utf-8')
            data = re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', decoded_line)
            if len(data) > 1:  # sometimes an empty line is received
                raw_data.append(data)
        if totalLines <= 0:
            all_errors.append(f"{table_name} has NO DATA")
        else:
            create_table_query, header = create_table(raw_data, table_name)

            insert_statement = insert_values(table_name, header)

            drop_table_query = f"DROP TABLE IF EXISTS `{table_name}`;"

            conn = mc.connect(user='root', password='root',
                              host='localhost',
                              database='test_schema')

            cursor = conn.cursor()
            drop_table(cursor, drop_table_query)

            create_and_insert(cursor, create_table_query, table_name, raw_data, insert_statement)

            conn.commit()
            cursor.close()
            conn.close()
    for err in all_errors:
        print(err)


def create_date_param():
    date_format = "XXXX,XX,XX"
    raw_start_date = input("\nProvide start date in format YYYY,MM,DD:")
    while len(date_format) != len(raw_start_date):
        raw_start_date = input("ERROR: Please provide valid date:")

    raw_end_date = input("\nProvide end date in format YYYY,MM,DD:")
    while len(date_format) != len(raw_end_date):
        raw_end_date = input("ERROR: Please provide valid date:")

    start_date = raw_start_date.split(",")
    end_date = raw_end_date.split(",")

    params['start_date'] = date(int(start_date[0]), int(start_date[1]), int(start_date[2])).isoformat()
    params['end_date'] = date(int(end_date[0]), int(end_date[1]), int(end_date[2])).isoformat()

    return params


if __name__ == '__main__':
    auth_token = input("Please provide your authentication token:")
    # reports that do NOT take dates as parameters
    reports_no_params_csv = ["submissions", "pages", "fields"]
    reports_no_params_noCsv = "reporting/projected_transcription_automation"

    # reports that TAKE dates as parameter
    reports_params_noCsv = ["reporting/transcription_automation",
                            "reporting/identification_automation", "reporting/table_identification_automation",
                            "reporting/classification_automation", "reporting/output_accuracy",
                            "reporting/transcription_accuracy", "reporting/identification_accuracy",
                            "reporting/table_identification_accuracy", "reporting/classification_accuracy",
                            "reporting/manual_working_time", "reporting/machine_working_time",
                            "reporting/transcription_supervision_volume",
                            "reporting/identification_supervision_volume",
                            "reporting/transcription_supervision_performance",
                            "reporting/identification_supervision_performance",
                            "reporting/classification_supervision_performance",
                            "reporting/hourly_reporting_submission",
                            "reporting/historical_processing", "reporting/keyer_performance",
                            "reporting/supervision_transcriptions", "reporting/machine_transcriptions",
                            "reporting/signature_machine_transcriptions", "reporting/checkbox_machine_transcriptions",
                            "reporting/application_usage"]

    tableName = reports_no_params_noCsv.split("/")[1]
    reporting(tableName, reports_no_params_noCsv, params=None, isCsv=False, auth_token=auth_token)

    for reportApi in reports_no_params_csv:
        reporting(reportApi, reportApi, params=None, isCsv=True, auth_token=auth_token)

    showReports = input("Multiple reports require dates for successful fetch. \n"
                        "Would you like to see names of these reports?[Y/N]:")
    showReports = showReports.lower()

    if showReports == "y" or showReports == "yes":
        for reports in reports_params_noCsv:
            report_name = reports.split("/")[1]
            print(report_name)

    params = {}

    val = input("\nWould you like to provide uniform dates for all reports?[Y/N]:")
    val = val.lower()

    if val == "y" or val == "yes":
        params = create_date_param()
        for reportApi in reports_params_noCsv:
            tableName = reportApi.split("/")[1]
            reporting(tableName, reportApi, params=params, isCsv=False, auth_token=auth_token)
    else:
        for reportApi in reports_params_noCsv:
            reportName = reportApi.split("/")[1]

            params = create_date_param()
            reporting(reportName, reportApi, params=params, isCsv=False, auth_token=auth_token)
