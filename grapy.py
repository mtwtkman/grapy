# -*- coding: utf-8 -*-
import os
from string import Template as T
from itertools import repeat
import subprocess


base_types = (int, float, str, bytes, bytearray)
base_itypes = (list, tuple, set)
iterables_cnt = dict(zip((i.__name__ for i in base_itypes),
                         repeat(1, len(base_itypes))))

t = T('''
${prefix}graph {name} {{
  {body}
}}
''')
main_t, sub_t = [t.safe_substitute({'prefix': x}) for x in ['di', 'sub']]


class TransferalError(Exception):
    pass


def draw(data, name=None, path=None, out=False, ext='gif'):
    if not isinstance(data, base_itypes + (dict,)):
        raise TypeError('Allowed types are `list`, `tuple`, `dict`, `set`')

    if name is None:
        name = 'from_grapy'
    body = make_body(data)
    result = main_t.format(name=name, body=body)
    if path is None:
        path = os.getcwd()
    _file = os.path.join(path, name)
    with open(_file + '.dot', 'w') as f:
        f.write(result)

    if out and subprocess.call(['which', 'dot']) == 0:
        cmd = ['dot', '-T' + ext, _file + '.dot', '-o', _file + '.' + ext]
        result = subprocess.call(cmd)
        if result > 0:
            raise TransferalError('Some probroblems occured while transfering.')
        print('Finished to Draw at {}.'.format(_file + 'ext'))


def make_body(data):
    if isinstance(data, dict):
        return '\n'.join(iter_parse_dict(data))
    elif isinstance(data, base_itypes):
        return '\n'.join(iter_parse_iterable(data))


def arrow(key, value):
    return str(key) + '->' + str(value) + ';'


def iter_parse_dict(data):
    for key, value in data.items():
        if isinstance(value, base_types):
            yield arrow(key, value)
        elif isinstance(value, base_itypes):
            yield '\n'.join(iter_parse_iterable(key, value))
        elif isinstance(value, dict):
            ivalue = ({k: v} for k, v in value.items())
            yield '\n'.join(iter_parse_iterable(key, ivalue))


def iter_parse_iterable(key, data):
    for d in data:
        if isinstance(d, base_types):
            yield arrow(key, d)
        if isinstance(d, base_itypes):
            type_name = type(d).__name__
            node_name = type_name.upper() + str(iterables_cnt[type_name])
            iterables_cnt[type_name] += 1
            yield arrow(key, node_name) + '\n' + \
                '\n'.join(iter_parse_iterable(node_name, d))
        if isinstance(d, dict):
            yield arrow(key, [k for k in d.keys()][0]) + '\n' + \
                '\n'.join(iter_parse_dict(d))
