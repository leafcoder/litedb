#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import yaml
import sqlite3
from cStringIO import StringIO

__version__ = '1.0'
is_name = re.compile(r'^[a-zA-Z0-9]+$').match

class LiteDB(object):

    def __init__(self, path):
        self.path = path
        self.conn = self._connect()

    def _connect(self):
        conn = sqlite3.connect(self.path, check_same_thread=True)
        conn.text_factory = str
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.execute('PRAGMA cache_size = 8000;')
        conn.commit()
        return conn

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    @property
    def tables(self):
        conn = self.conn
        cur = conn.execute('''\
        SELECT name FROM sqlite_master
        WHERE type='table' AND name like 'litedb_%'
        ORDER BY name;''')
        ret = cur.fetchall()
        names = []
        for row in ret:
            name = row[0]
            if not name.startswith('litedb_'):
                continue
            names.append(name[len('litedb_'):])
        return tuple(names)

    def table(self, name, auto_increment=True):
        self.create(name, auto_increment=auto_increment)
        return LiteDBTable(
            self, name, auto_increment=auto_increment
        )

    def delete(self, name):
        if is_name(name) is None:
            raise ValueError('invalid table name')
        conn = self.conn
        conn.execute('''\
        DROP TABLE IF EXISTS litedb_%s;''' % name)

    def create(self, name, auto_increment=True):
        if is_name(name) is None:
            raise ValueError('invalid table name')
        conn = self.conn
        if auto_increment:
            conn.execute('''\
            CREATE TABLE IF NOT EXISTS litedb_%s (
                id INTEGER,
                data BYTEA,
                PRIMARY KEY (id)
            )
            ''' % name)
        else:
            conn.execute('''\
            CREATE TABLE IF NOT EXISTS litedb_%s (
                id VARCHAR,
                data BYTEA,
                PRIMARY KEY (id)
            )
            ''' % name)

class LiteDBTable(object):

    def __init__(self, litedb, name, auto_increment=True):
        self.auto_increment = auto_increment
        self.name = name
        self.litedb = litedb

    def rows(self):
        litedb = self.litedb
        conn = litedb.conn
        cur = conn.execute('''\
        SELECT id, data FROM litedb_%s;
        ''' % self.name)
        result = []
        for id, data_str in cur.fetchall():
            data = data_str
            if data_str is not None:
                data = yaml.load(StringIO(data_str))
            result.append(LiteDBRow(self, id, data))
        return result

    def row(self, *args, **kwargs):
        litedb = self.litedb
        conn = litedb.conn
        if 0 == len(args):
            if 'data' in kwargs:
                id = kwargs.get('id')
                data = kwargs['data']
                return self._new_row(id, data)
            else:
                id = kwargs.pop('id')
                return self._get_row(id)
        elif 1 == len(args):
            id = args[0]
            if 'data' not in kwargs:
                return self._get_row(id)
            data = kwargs['data']
            return self._new_row(id, data)
        elif 2 == len(args):
            id, data = args
            return self._new_row(id, data)
        else:
            id, data = args[0], args[1]
            return self._new_row(id, data)

    def delete(self, id):
        litedb = self.litedb
        conn = litedb.conn
        cur = conn.execute('''\
        DELETE FROM litedb_%s WHERE id=?;
        ''' % self.name, (id, ))

    def _get_row(self, id):
        litedb = self.litedb
        conn = litedb.conn
        cur = conn.execute('''\
        SELECT id, data FROM litedb_%s WHERE id=?;
        ''' % self.name, (id, ))
        ret = cur.fetchone()
        if ret is None:
            return
        id, data_str = ret
        data = data_str
        if data_str is not None:
            data = yaml.load(StringIO(data_str))
        return LiteDBRow(self, id, data)

    def _new_row(self, id, data):
        litedb = self.litedb
        conn = litedb.conn
        data_str = data
        if data is not None:
            data_str = yaml.dump(data)
        if id is not None:
            if self.auto_increment:
                try:
                    id = int(id)
                except:
                    raise ValueError('id requires integer')
            cur = conn.execute('''\
            UPDATE litedb_%s SET data=? WHERE id=?;
            ''' % self.name, (data_str, id))
            if cur.rowcount == 0:
                cur = conn.execute('''\
                INSERT INTO litedb_%s (id, data) VALUES (?, ?);
                ''' % self.name,  (id, data_str))
                id = cur.lastrowid
        else:
            cur = conn.execute('''\
            INSERT INTO litedb_%s (data) VALUES (?);
            ''' % self.name,  (data_str, ))
            id = cur.lastrowid
        return LiteDBRow(self, id, data)

    # TODO
    def search(self, AND=None, OR=None, NOT=None, order=None):
        pass

class LiteDBRow(object):

    def __init__(self, table, id, data):
        self.table = table
        self.data = data
        self.id = id
