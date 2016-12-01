#!/usr/bin/python
# -*- coding: utf-8 -*-

__version__ = '1.0'

import re
import yaml
import sqlite3
from cStringIO import StringIO

max_limit = 100
is_name = re.compile(r'^[a-zA-Z0-9]+$').match

class LiteDB(object):

    def __init__(self, path):
        self.path = path
        self.conn = conn = sqlite3.connect(self.path, check_same_thread=True)
        conn.text_factory = str
        conn.isolation_level=None
        conn.execute('BEGIN;')
        conn.execute('PRAGMA foreign_keys = ON;')
        conn.execute('PRAGMA cache_size = 8000;')
        conn.commit()

    def begin(self):
        return LiteDBTransaction(self)

class LiteDBTransaction(object):

    def __init__(self, litedb):
        self.litedb = litedb
        self.conn = litedb.conn
        self.conn.execute('BEGIN;')

    def commit(self):
        self.conn.commit()
        self.conn.execute('BEGIN;')

    def rollback(self):
        self.conn.rollback()
        self.conn.execute('BEGIN;')

    def tables(self, offset=0, limit=10):
        conn = self.conn
        offset = int(offset)
        limit = min(int(limit), max_limit)
        cur = conn.execute('''\
        SELECT name FROM sqlite_master
        WHERE type='table' AND name like 'litedb_%'
        ORDER BY name LIMIT ? OFFSET ?;
        ''', (limit, offset))
        names = []
        for row in cur.fetchall():
            name = row[0]
            if not name.startswith('litedb_'):
                continue
            names.append(name[len('litedb_'):])
        return tuple(names)

    def table(self, name):
        if not is_name(name):
            raise ValueError('invalid table name %s' % name)
        conn = self.conn
        conn.execute('''\
        CREATE TABLE IF NOT EXISTS litedb_%s (
            id INTEGER,
            data BYTEA,
            PRIMARY KEY (id)
        );''' % name)
        return LiteDBTable(self, name)

    def exists(self, name):
        if not is_name(name):
            raise ValueError('invalid table name %s' % name)
        conn = self.conn
        cur = conn.execute('''\
        SELECT name FROM sqlite_master WHERE type='table' AND name=?;
        ''', ('litedb_%s' % name, ))
        ret = cur.fetchone()
        if ret is None:
            return False
        return True

    def delete(self, name):
        if not is_name(name):
            raise ValueError('invalid table name %s' % name)
        conn = self.conn
        conn.execute('''\
        DROP TABLE IF EXISTS litedb_%s;''' % name)

class LiteDBTable(object):

    def __init__(self, txn, name):
        self.txn = txn
        self.name = name

    def rows(self, offset=0, limit=10):
        txn = self.txn
        conn = txn.conn
        offset = int(offset)
        limit = min(int(limit), max_limit)
        cur = conn.execute('''\
        SELECT id, data FROM litedb_%s LIMIT ? OFFSET ?;
        ''' % self.name, (limit, offset))
        result = []
        for id, data_str in cur.fetchall():
            data = data_str
            if data_str is not None:
                data = yaml.load(StringIO(data_str))
            result.append(LiteDBRow(self, id, data))
        return result

    def row(self, id):
        txn = self.txn
        conn = txn.conn
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

    def insert(self, data):
        txn = self.txn
        conn = txn.conn
        data_str = data
        if data is not None:
            data_str = yaml.dump(data)
        cur = conn.execute('''\
        INSERT INTO litedb_%s (data) VALUES (?);
        ''' % self.name,  (data_str, ))
        id = cur.lastrowid
        return LiteDBRow(self, id, data)

    def update(self, id, data):
        txn = self.txn
        conn = txn.conn
        if isinstance(id, LiteDBRow):
            id = id.id
        data_str = data
        if data is not None:
            data_str = yaml.dump(data)
        cur = conn.execute('''\
        UPDATE litedb_%s SET data=? WHERE id=?;
        ''' % self.name, (data_str, id))

    def delete(self, id):
        txn = self.txn
        conn = txn.conn
        if isinstance(id, LiteDBRow):
            id = id.id
        cur = conn.execute('''\
        DELETE FROM litedb_%s WHERE id=?;
        ''' % self.name, (id, ))

    # TODO
    def search(self, AND=None, OR=None, NOT=None, order=None):
        pass

class LiteDBRow(object):

    def __init__(self, table, id, data):
        self.table = table
        self.data = data
        self.id = id
