# -*- coding: utf-8 -*-
import unittest
import tempfile
import os
import shutil

import grapy as g


if g.PYVER == 2:
    setattr(unittest.TestCase, 'assertCountEqual',
        unittest.TestCase.assertItemsEqual)
else:
    from imp import reload


class ParseDictTest(unittest.TestCase):
    def _callFUT(self, data):
        # To reflesh toplevel variable named `iterables_cnt`.
        reload(g)
        return g.iter_parse_dict(data)

    def assertParseDict(self, datas, expects):
        for d, e in zip(datas, expects):
            self.assertCountEqual(next(self._callFUT(d)).split('\n'), e)

    def assertParseMultipleParentDict(self, datas, expects):
        for d, e in zip(datas, expects):
            self.assertCountEqual(list(self._callFUT(d)), e)

    def test_ok_child_is_base_types(self):
        datas = [
            {'a': 1},
            {10: 'b'},
            {'c': 'd'},
            {100: 1000},
            {10000.1: 100000.2},
            {b'e': bytearray(b'f')}
        ]
        expects = [
            ('a->1;',),
            ('10->b;',),
            ('c->d;',),
            ('100->1000;',),
            ('10000.1->100000.2;',),
            ((lambda x: x + '->bytearray(b\'f\');')('b\'e\'' if g.PYVER == 3 else 'e'),)
        ]
        self.assertParseDict(datas, expects)

    def test_ok_child_is_base_iterables(self):
        datas = [
            {'a': [1, 2]},
            {'b': (3, 4)},
            {'c': {5, 6}}
        ]
        expects = [
            ('a->1;', 'a->2;'),
            ('b->3;', 'b->4;'),
            ('c->5;', 'c->6;')
        ]
        self.assertParseDict(datas, expects)

    def test_ok_child_is_dict(self):
        datas = [
            {'a': {'b': 1}},
            {'c': {'d': [2, 3, {'e': 'f'}]}},
            {'g': {'h': 4, 'i': 5}},
        ]
        expects = [
            ('a->b;', 'b->1;'),
            ('c->d;', 'd->2;', 'd->3;', 'd->e;', 'e->f;'),
            ('g->h;', 'h->4;', 'g->i;', 'i->5;'),
        ]
        self.assertParseDict(datas, expects)

    def test_ok_child_is_list(self):
        datas = [
            {'a': [1, {'b': 2}, 'c']},
            {'d': [{'e': 3}, {'f': 4}]},
            {'g': [[5, 6], [7], 8]}
        ]
        expects = [
            ('a->1;', 'a->b;', 'b->2;', 'a->c;'),
            ('d->e;', 'e->3;', 'd->f;', 'f->4;'),
            ('g->LIST1;', 'LIST1->5;', 'LIST1->6;',
             'g->LIST2;', 'LIST2->7;', 'g->8;')
        ]
        self.assertParseDict(datas, expects)

    def test_ok_child_is_nesting_base_iterables(self):
        datas = [
            {'a': [{'iam', 'set'}, ['iam', 'list'], ('iam', 'tuple')]},
            {'b': [{'set', 1}, {'set', 2}, {'set', 3}]},
            {'c': [['list', 1], ['list', 2], ['list', 3]]},
            {'d': [('tuple', 1), ('tuple', 2), ('tuple', 3)]},
        ]
        expects = [
            ('a->SET1;', 'SET1->iam;', 'SET1->set;',
             'a->LIST1;', 'LIST1->iam;', 'LIST1->list;',
             'a->TUPLE1;', 'TUPLE1->iam;', 'TUPLE1->tuple;'),
            ('b->SET1;', 'SET1->set;', 'SET1->1;',
             'b->SET2;', 'SET2->set;', 'SET2->2;',
             'b->SET3;', 'SET3->set;', 'SET3->3;'),
            ('c->LIST1;', 'LIST1->list;', 'LIST1->1;',
             'c->LIST2;', 'LIST2->list;', 'LIST2->2;',
             'c->LIST3;', 'LIST3->list;', 'LIST3->3;'),
            ('d->TUPLE1;', 'TUPLE1->tuple;', 'TUPLE1->1;',
             'd->TUPLE2;', 'TUPLE2->tuple;', 'TUPLE2->2;',
             'd->TUPLE3;', 'TUPLE3->tuple;', 'TUPLE3->3;'),
        ]
        self.assertParseDict(datas, expects)

    def test_ok_multiple_parents(self):
        datas = [
            {'a': 1, 'b': 2},
        ]
        expects = [
            ('a->1;', 'b->2;'),
        ]
        self.assertParseMultipleParentDict(datas, expects)


class DrawTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(dir='.')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _callFUT(self, data, name=None):
        # To reflesh toplevel variable named `iterables_cnt`.
        reload(g)
        return g.draw(data, name=name, path=self.tmpdir)

    def test_raise_exception_with_invalid_type(self):
        data = [
            'basestring',
            1,
            1.1,
            b'bytestring',
            bytearray(b'bytearray')
        ]
        for d in data:
            with self.assertRaises(TypeError):
                self._callFUT(d)

    def test_ok_draw(self):
        data = {'a': 1}
        name = 'test1'
        self._callFUT(data, name='test1')
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, name + '.dot')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
