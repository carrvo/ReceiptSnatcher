"""
"""

from itertools import groupby

def sorted_groupby(iterable, key=None):
    return groupby(sorted(iterable, key=key), key=key)

def key_counter(iterable, key=None):
    return tuple((gkey, len(tuple(group))) for gkey, group in sorted_groupby(iterable, key=key))


def group_count(iterable, fields, count_field='count'):
    key = lambda x: tuple(x[f] for f in fields)
    counted_fields = (*fields, count_field)
    counted = ((*gkey, len(tuple(group))) for gkey, group in sorted_groupby(iterable, key=key))
    return tuple({k:v for k,v in zip(counted_fields, c)} for c in counted)

