_previous_id = -1


def get_new_id():
    global _previous_id
    _previous_id += 1
    return _previous_id


def set_lower_limit(limit):
    global _previous_id
    _previous_id = max(limit, _previous_id)
