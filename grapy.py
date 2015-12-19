# -*- coding: utf-8 -*-
import os
import sys
from itertools import repeat
import subprocess


PYVER = sys.version_info.major
base_types = (int, float, str, bytes, bytearray)
base_itypes = (list, tuple, set)
iterables_cnt = dict(zip((i.__name__ for i in base_itypes),
                         repeat(1, len(base_itypes))))
template = '''
digraph {name} {{
  {body}
}}
'''


class TransferalError(Exception):
    pass


class DotCommandNotFound(Exception):
    pass


def transfer(data, name=None, path=None):
    if not isinstance(data, base_itypes + (dict,)):
        raise TypeError('Allowed types are `list`, `tuple`, `dict`, `set`')

    if name is None:
        name = 'from_grapy'
    body = make_body(data)
    result = template.format(name=name, body=body)
    if path is None:
        path = os.getcwd()
    _file = os.path.join(path, name)
    with open(_file + '.dot', 'w') as f:
        f.write(result)
    return _file


def draw(data, name=None, path=None, ext='gif'):
    if subprocess.call(['which', 'dot']) == 0:
        _file = transfer(data, name, path)
        cmd = ['dot', '-T' + ext, _file + '.dot', '-o', _file + '.' + ext]
        result = subprocess.call(cmd)
        if result > 0:
            raise TransferalError('Some probroblems occured while transfering.')
        print('Finished to Draw at {}.'.format(_file + 'ext'))
    else:
        raise DotCommandNotFound


def make_body(data):
    if isinstance(data, dict):
        return '\n'.join(iter_parse_dict(data))
    elif isinstance(data, base_itypes):
        return '\n'.join(iter_parse_iterable(data))


def arrow(key, value):
    if PYVER == 2:
        key, value = list(replace_byte_str(key, value))
    return str(key) + '->' + str(value) + ';'


def replace_byte_str(*args):
    for arg in args:
        if isinstance(arg, bytearray):
            yield 'bytearray(b\'{}\')'.format(arg)
        else:
            yield arg


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
