# pylint: disable=E0402,E0401,E0611,C0412,C0116,C0114,C0115

def validate_index_pattern(index_pattern: str):

    error: str = None

    if '*' not in index_pattern:
        error = "Index Pattern must contain asterisk"

    # pylint: disable=line-too-long
    if index_pattern.count('*') == 1 and not (index_pattern.startswith('*') or index_pattern.endswith('*')):
        error = "Wildcards must be at the start and end."

    # pylint: disable=line-too-long
    if index_pattern.count('*') == 2 and not (index_pattern.startswith('*') and index_pattern.endswith('*')):
        error = "If two wildcards are supplied, they must be at the start and end."

    if index_pattern.count('*') > 2:
        error = "Index Pattern must contain no more than two asterisk"

    return index_pattern.replace('*', '%'), error
