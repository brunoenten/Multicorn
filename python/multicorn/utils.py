from logging import ERROR, INFO, DEBUG, WARNING, CRITICAL
try:
    from ._utils import _log_to_postgres
    from ._utils import check_interrupts
except ImportError as e:
    from warnings import warn
    warn("Not executed in a postgresql server,"
         " disabling log_to_postgres", ImportWarning)

    def _log_to_postgres(message, level=0, hint=None, detail=None):
        pass


REPORT_CODES = {
    DEBUG: 0,
    INFO: 1,
    WARNING: 2,
    ERROR: 3,
    CRITICAL: 4
}

def log_to_postgres(message, level=INFO, hint=None, detail=None):
    code = REPORT_CODES.get(level, None)
    if code is None:
        raise KeyError("Not a valid log level")
    _log_to_postgres(message, code, hint=hint, detail=detail)

def updates_from_dict(changes_dict):
    changes_list = []
    for col, value in changes_dict.items():
        if not isinstance(value, (int, float)):
            value = f"'{value}'"

        changes_list.append(f"\"{col}\" = {value}")
    return ",".join(changes_list)

def quoted_insert_values(_values):
    values_list = []
    for value in _values:
        if not isinstance(value, (int, float)):
            value = f"'{value}'"
        values_list.append(value)
    return ",".join(values_list)



