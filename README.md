# litedb
基于 sqlite3 实现的简单对象数据库

## 1. 创建对象

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')

## 2. 获取所有表名

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    >>> print litedb.tables
    ('table_1', 'table_2')

## 3. 新建表、获取表

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    >>> table_name = 'table_1'
    >>> table = litedb.table(table_name)
    >>> print table.name
    >>> litedb.commit()

## 4. 删除表

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    >>> table_name = 'table_1'
    >>> litedb.delete(table_name)
    >>> litedb.commit()

## 5. 新建行

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    >>> table_name = 'table_1'
    >>> table = litedb.table(table_name, auto_increment=True)
    >>> row = table.row(id=1, data={'name': 'litedb'}) # 指定 ID
    >>> row = table.row(data={'name': 'litedb'}) # 不指定 ID，只允许自增表
    >>> table = litedb.table(table_name, auto_increment=False)
    >>> row = table.row(id='str_id', data={'name': 'litedb'})
    >>> litedb.commit()

## 6. 获取行

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    >>> table_name = 'table_1'
    >>> table = litedb.table(table_name, auto_increment=True)
    >>> row = table.row(1)
    >>> row = table.row(id=1)

## 7. 删除行

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    >>> table_name = 'table_1'
    >>> table = litedb.table(table_name, auto_increment=True)
    >>> table.delete(1)
    >>> litedb.commit()

## 8. 搜索数据 TODO

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    >>> table_name = 'table_1'
    >>> table = litedb.table(table_name, auto_increment=True)
    >>> table.search(
        AND={
            'name': 'leo',
            'age': {'lt': 20, 'gt': 10},
            'grade': [1, 2, 3, 4, 5],
            'addr': None
        },
        OR={},
        NOT={},
        order=[
            {'name': 'desc'},
            {'name': 'desc'},
            {'name': 'desc'},
            {'name': 'desc'}
        ]
    )
