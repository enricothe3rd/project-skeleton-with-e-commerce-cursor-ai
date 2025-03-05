from django.db import connection
from django.utils import timezone
from skeleton.utils.queries.statements import select as statements
import datetime


# ACCEPTS QUERY SET VALUES GENERALLY THE OUTPUT FROM STRAIGHTFORWARD DJANGO ORM QUERIES
def extract_queryset(value):
    arr = []
    for val in value:
        arr.append(val)
    return arr


def get_field_value_from_raw_values(arr, field):
    final = []
    for value in arr:
        final.append(value[field])
    return final


def execute_raw_query(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        return fetchall_dictionary(cursor)


def execute_raw_query_list(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()


def execute_raw_query_insert(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        # return fetchall_dictionary(cursor)


def execute_raw_query_operations(query):
    with connection.cursor() as cursor:
        cursor.execute(query)


def execute_response_build(data, method):
    if len(data) <= 0:
        return []
    else:
        return method()


def fetchall_dictionary(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def build_conditions(value):
    condition_string = ""
    extracted = []
    if value != "":
        arr = value.split(";")

        for val in arr:
            extracted.append(val.split(","))

        for condition_values in extracted:
            connector = ""
            if condition_values[3] != "None":
                connector = condition_values[3]

            condition_string += "A.{} {} {} {} ".format(
                condition_values[0],
                condition_values[1],
                condition_values[2],
                connector
            )

    return condition_string


def calculate_offset(page, batch_size):
    offset_value = 0
    if int(page) > 1:
        offset_value = int(page) * int(batch_size)
    return offset_value


def construct_ids_tuple(initial_list):
    iterator = 1
    ids_list = []
    ids_collection = ""
    for ids in initial_list:
        if len(initial_list) == iterator:
            ids_collection += str(ids['id'])
        else:
            ids_collection += (str(ids['id']) + ", ")
        ids_list.append(ids['id'])
        iterator += 1
    return "({})".format(ids_collection), ids_list


class GenerateConditionLevelBased:
    def __init__(self, level, eid):
        self.level = level
        self.eid = eid

    def execute(self):
        condition = ""
        if self.level == "EMPLOYEE":
            if self.eid is not None:
                condition = "A.employee_id_id = %s AND " % self.eid
            else:
                condition = "A.employee_id_id = 0 AND "
        elif self.level == "MANAGER":
            managed_departments_query = statements.fetch_managed_departments.format(self.eid)
            managed_teams_query = statements.fetch_managed_teams.format(self.eid)
            managed_positions_query = statements.fetch_managed_positions.format(self.eid)

            managed_departments = get_field_value_from_raw_values(
                execute_raw_query(managed_departments_query), "id"
            )
            managed_teams = get_field_value_from_raw_values(
                execute_raw_query(managed_teams_query), "id"
            )
            managed_positions = get_field_value_from_raw_values(
                execute_raw_query(managed_positions_query), "id"
            )
            if len(managed_departments) > 0:
                condition += self._build_conditions_managed_areas(managed_departments, "G.id") + " AND "
            if len(managed_teams) > 0:
                condition += self._build_conditions_managed_areas(managed_teams, "H.id") + " AND "
            if len(managed_positions) > 0:
                condition += self._build_conditions_managed_areas(managed_positions, "I.id") + " AND "
        return condition

    @staticmethod
    def _build_conditions_managed_areas(ids, db_field):
        filters = "{} IN (".format(db_field)
        for val in ids:
            if val == ids[-1]:
                filters = filters + str(val)
            else:
                filters = filters + str(val) + ","
        filters += ")"
        return filters


def generate_condition_level_based(level, eid):
    condition = ""
    if level == "EMPLOYEE":
        if eid is not None:
            condition = "employee_id_id,=,%s,AND;" % eid
        else:
            condition = "employee_id_id,=,0,AND;"
    return condition


class Redirect:
    def __init__(self, operation, class_name):
        self.operation = operation
        self.class_name = class_name

    def identify_operation(self):
        operations = {
            "CREATE": self.class_name.create,
            "READ": self.class_name.fetch,
            "READ_DETAIL": self.class_name.fetch_details,
            "UPDATE": self.class_name.update,
            "DELETE": self.class_name.delete,
            "LINE_UPDATE": self.class_name.change_line,
            "LINE_DELETE": self.class_name.delete_line,
            "DEACTIVATE": self.class_name.deactivate,
            "REACTIVATE": self.class_name.reactivate,
            "UPDATE_STATUS": self.class_name.update_status
        }
        
        operation = operations.get(self.operation)
        if operation:
            return operation()
        return {"error": "Invalid Operation"}


class ProcessHeaderInfo:
    def __init__(self, raw_values):
        self.values = raw_values

    def execute(self):
        processed_arr = {}
        value = self.values[0]
        keys = list(value.keys())

        for key in keys:
            if value[key]["form_control"] == "date":
                processed_arr[value[key]["technical_name"]] = {
                    "value": value[key]["value"],
                    "real_value": self._date_to_list(value[key]["real_value"]),
                }
            elif value[key]["form_control"] == "select":
                processed_arr[value[key]["technical_name"]] = value[key]["real_value"]
            else:
                processed_arr[value[key]["technical_name"]] = value[key]["value"]
        return processed_arr

    @staticmethod
    def _date_to_list(str_date):
        if str_date is not None:
            date = datetime.datetime.strptime(str_date, "%B %d, %Y")

            return [date.year, date.month, date.day]
        else:
            return None


class ParseValues:
    def __init__(self, values):
        self.values = values

    def parse_date(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(datetime.date(date[0], date[1], date[2]))

        return parsed

    def parse_time(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(datetime.time(date[0], date[1], date[2]))

        return parsed

    def parse_datetime(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(
                    timezone.make_aware(datetime.datetime.strptime(date, "%B %d, %Y %H:%S"))
                )

        return parsed

    def parse_date_from_string_not_naive(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(
                    datetime.datetime.strptime(date, "%B %d, %Y")
                )

        return parsed

    def parse_date_from_string(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(
                    timezone.make_aware(datetime.datetime.strptime(date, "%B %d, %Y"))
                )

        return parsed

    def parse_time_from_string(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(datetime.datetime.strptime(date, "%H:%M"))

        return parsed

    def parse_ymd_hms_from_string(self):
        parsed = []
        date = self.values
        if date is None or date == "":
            parsed.append(None)
        else:
            parsed.append(
                timezone.make_aware(datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
            )

        return parsed

    def parse_datetime_from_string(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(
                    timezone.make_aware(datetime.datetime.strptime(date, "%B %d, %Y %H:%M:%S"))
                )

        return parsed

    def parse_datetime_from_string_no_sec(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(
                    timezone.make_aware(datetime.datetime.strptime(date, "%B %d, %Y %H:%M"))
                )

        return parsed

    def parse_get_month_string(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%B")

        return parsed

    def parse_get_month_numeric_string(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%m")

        return parsed

    def parse_get_month_date_string(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%m%d")

        return parsed

    def parse_get_year_string(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%Y")

        return parsed

    def parse_date_to_string(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%B %d, %Y")

        return parsed

    def parse_date_to_string_ymd(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%Y-%m-%d")

        return parsed

    def parse_date_to_string_mdy(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%m%d%Y")

        return parsed

    def parse_date_to_string_md(self):
        date = self.values
        parsed = None

        if date is not None and date != "":
            parsed = date.strftime("%m%d")

        return parsed

    def parse_time_to_string(self):
        time = self.values
        parsed = None

        if time is not None and time != "":
            parsed = time.strftime("%H:%M")

        return parsed

    def parse_datetime_to_string(self):
        parsed = []
        for date in self.values:
            if date is None or date == "":
                parsed.append(None)
            else:
                parsed.append(date.strftime("%B %d, %Y %H:%M:%S"))

        return parsed

    def datetime_to_ymd_string(self):
        # self.values = self.parse_datetime_to_string()
        parsed_obj = self.values
        parsed = None
        if parsed_obj is not None:
            parsed = parsed_obj[0].strftime("%Y-%m-%d")
        return parsed

    def subtract_datetime_to_minutes(self):
        if self.values[0] is None or self.values[1] is None:
            return 0
        else:
            difference = self.values[0] - self.values[1]
            return difference.total_seconds() / 60

    def subtract_datetime_to_hours(self):
        if self.values[0] is None or self.values[1] is None:
            return 0
        else:
            difference = self.values[0] - self.values[1]
            return round((difference.total_seconds() / 60) / 60, 2)

    def get_month(self):
        time = self.values
        parsed = None
        if time is not None and time != "":
            parsed = time.strftime("%m")
        return parsed

    def get_year(self):
        time = self.values
        parsed = None
        if time is not None and time != "":
            parsed = time.strftime("%Y")
        return parsed


# ACCEPTS OBJECT WITH SELECT_RELATED OR PREFETCH_RELATED METHODS
class ExtractAndBuildFromRawSQL:
    def __init__(self, mapping):
        self.mapping = mapping

    def execute_object(self, query):
        results = self.extract_from_raw_sql(query.objects)
        return self.map_values(results)

    def execute_string(self, query):
        # try:
        results = self.extract_from_raw_sql(query)
        return self.map_values(results)
        # except KeyError as k_err:
        #     return {'error': str(k_err)}
        # except Exception as ex:
        #     return {'error': str(ex)}

    def execute_for_async_select(self, query):
        try:
            results = self.extract_from_raw_sql(query)
            return self.map_values_for_async_select(results)
        except KeyError as k_err:
            return {'error': str(k_err)}
        except Exception as ex:
            return {'error': str(ex)}

    @staticmethod
    def extract_from_raw_sql(query):
        with connection.cursor() as cursor:
            cursor.execute(str(query))

            results = cursor.fetchall()
        return results

    def map_values(self, values):
        wrapper = []
        mapping_raw = self.mapping
        for val in values:
            mapping_output = {}
            for key, map_value in mapping_raw.items():
                mapping_output[key] = {
                    "value": val[map_value[0]],
                    "real_value": val[map_value[0]],
                    "widget": map_value[1],
                    "valid_values": map_value[2],
                    "form_control": map_value[3],
                    "relational_table": map_value[5],
                    "technical_name": map_value[6],
                    "is_required": map_value[7],
                }

                if map_value[4] is not None:
                    mapping_output[key]["real_value"] = val[map_value[4]]
                # else:
                #     mapping_output[key]["foreign_key"] = None

                if map_value[3] == "date" and val[map_value[0]] is not None:
                    mapping_output[key]["value"] = val[map_value[0]].strftime("%B %d, %Y")
                    mapping_output[key]["real_value"] = val[map_value[0]].strftime("%B %d, %Y")

                if map_value[3] == "time" and val[map_value[0]] is not None:
                    mapping_output[key]["value"] = val[map_value[0]].strftime("%H:%M")
                    mapping_output[key]["real_value"] = val[map_value[0]].strftime("%H:%M")

            wrapper.append(mapping_output)

        return wrapper

    def map_values_for_async_select(self, values):
        wrapper = []
        mapping_raw = self.mapping
        for val in values:
            mapping_output = {}
            for key, map_value in mapping_raw.items():
                mapping_output[key] = val[map_value]

            wrapper.append(mapping_output)

        return wrapper


class Queries:
    def __init__(self, db_object):
        self.db_object = db_object

    def execute_create(self, params):
        try:
            create_object = self.db_object(**params)
            create_object.save()

            return {"status": True,
                    "message": "Success",
                    "values": extract_queryset(self.db_object.objects.filter(id=create_object.id).values()),
                    "id": create_object.id}, create_object
        except ValueError as val_err:
            return {"status": False, "message": str(val_err)}, None
        except KeyError as key_err:
            return {"status": False, "message": str(key_err)}, None
        except TypeError as type_err:
            return {"status": False, "message": str(type_err)}, None
        except Exception as ex:
            return {"status": False, "message": str(ex)}, None

    def execute_change(self, params, row_id):
        try:
            update_object = self.db_object.objects.filter(id=row_id)
            update_object.update(**params)

            return {"status": True,
                    "message": "Success",
                    "values": extract_queryset(self.db_object.objects.filter(id=row_id).values()),
                    "id": row_id}, update_object
        except ValueError as val_err:
            return {"status": False, "message": str(val_err)}, None
        except KeyError as key_err:
            return {"status": False, "message": str(key_err)}, None
        except TypeError as type_err:
            return {"status": False, "message": str(type_err)}, None
        except Exception as ex:
            return {"status": False, "message": str(ex)}, None

    def execute_deactivate(self, row_id):
        try:
            update_object = self.db_object.objects.filter(id=row_id)
            update_object.update(is_active=False)

            return {"status": True,
                    "message": "Success",
                    "values": extract_queryset(self.db_object.objects.filter(id=row_id).values()),
                    "id": row_id}, update_object
        except ValueError as val_err:
            return {"status": False, "message": str(val_err)}, None
        except KeyError as key_err:
            return {"status": False, "message": str(key_err)}, None
        except TypeError as type_err:
            return {"status": False, "message": str(type_err)}, None
        except Exception as ex:
            return {"status": False, "message": str(ex)}, None

    def execute_reactivate(self, row_id):
        try:
            update_object = self.db_object.objects.filter(id=row_id)
            update_object.update(is_active=True)

            return {"status": True,
                    "message": "Success",
                    "values": extract_queryset(self.db_object.objects.filter(id=row_id).values()),
                    "id": row_id}, update_object
        except ValueError as val_err:
            return {"status": False, "message": str(val_err)}, None
        except KeyError as key_err:
            return {"status": False, "message": str(key_err)}, None
        except TypeError as type_err:
            return {"status": False, "message": str(type_err)}, None
        except Exception as ex:
            return {"status": False, "message": str(ex)}, None

    def execute_restricted_delete(self, row_id):
        # ADD is_active = False checking
        try:
            update_object = self.db_object.objects.filter(id=row_id)
            update_object.delete()

            return {"status": True,
                    "message": "Success",
                    "values": extract_queryset(self.db_object.objects.filter(id=row_id).values()),
                    "id": row_id}, update_object
        except ValueError as val_err:
            return {"status": False, "message": str(val_err)}, None
        except KeyError as key_err:
            return {"status": False, "message": str(key_err)}, None
        except TypeError as type_err:
            return {"status": False, "message": str(type_err)}, None
        except Exception as ex:
            return {"status": False, "message": str(ex)}, None

    def execute_unrestricted_delete(self, row_id):
        try:
            update_object = self.db_object.objects.filter(id=row_id)
            update_object.delete()

            return {"status": True,
                    "message": "Success",
                    "values": extract_queryset(self.db_object.objects.filter(id=row_id).values()),
                    "id": row_id}, update_object
        except ValueError as val_err:
            return {"status": False, "message": str(val_err)}, None
        except KeyError as key_err:
            return {"status": False, "message": str(key_err)}, None
        except TypeError as type_err:
            return {"status": False, "message": str(type_err)}, None
        except Exception as ex:
            return {"status": False, "message": str(ex)}, None


class FetchValues:
    def __init__(self, obj):
        self.obj = obj

    def fetch_one_row(self, filters):
        table_obj = self.obj

        fetch_obj = table_obj.objects.filter(**filters)
        obj_value = fetch_obj.values()

        return extract_queryset(obj_value)


class ConstructSelectQuery:
    def __init__(self, model, filters, level):
        self.model = model
        self.filters = filters
        self.level = level

    def search(self):
        conditions = self._dissect_filters(self.filters)
        return self._build_query(conditions)

    def _build_query(self, conditions_raw):
        level = self.level
        model = self.model

        base = self._get_base_data(model)
        conditions = self._build_conditions(conditions_raw, base[0])

        return "{0} {1} {2}".format(str(base[1]), conditions, " ORDER BY " + base[0] + ".id DESC")

    @staticmethod
    def _dissect_filters(value):
        extracted = []
        arr = value.split(";")
        for val in arr:
            extracted.append(val.split(","))

        return extracted

    @staticmethod
    def _build_conditions(raw, table):
        try:
            conditions = "WHERE "

            for const in raw:
                if const[3] != "None":
                    append_val = ('"{4}"."{0}" {1} \'{2}\' {3} '.
                                  format(const[0], const[1], const[2], const[3], table))
                else:
                    append_val = ('"{3}"."{0}" {1} \'{2}\''.
                                  format(const[0], const[1], const[2], table))

                conditions = conditions + append_val

            return conditions
        except KeyError as k_err:
            return {'error': str(k_err)}
        except Exception as ex:
            return {'error': str(ex)}

    @staticmethod
    def _get_base_data(model):
        base_object = model.objects.filter().select_related()
        table = model.objects.model._meta.db_table
        query = base_object.query

        return table, query


class EvaluateQueryResults:
    def __init__(self, results):
        self.results = results

    def execute_query_results(self):
        eval_result = True

        for res_dat in self.results:
            if res_dat[0]['status'] is not True:
                eval_result = False

        return eval_result

    def execute_batch_query_results(self):
        eval_result = True
        results = self.results
        keys = self.results.keys()

        for key in keys:
            if results[key] is not True:
                eval_result = False

        return eval_result


