__author__ = 'Alec'

def stringify_sql(value):
    if value[0] is not "'" and value[-1] is not "'":
        return "'" + value + "'"
    return value