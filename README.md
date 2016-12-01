# litedb
基于 sqlite3 实现的简单对象数据库

## 1. 创建对象

    >>> from litedb import LiteDB
    >>> litedb = LiteDB('sqlite.db')
    
## 2. 开始事务
    >>> txn = litedb.begin()
    >>> ......

## 3. 获取所有表名

    >>> txn = litedb.begin()
    >>> print txn.tables
    ('table_1', 'table_2')

## 4. 新建表、获取表

    >>> txn = litedb.begin()
    >>> table = txn.table('table_1')
    >>> print table.name
    >>> txn.commit()

## 5. 删除表

    >>> txn = litedb.begin()
    >>> litedb.delete('table_1')
    >>> litedb.commit()

## 6. 新建行

    >>> txn = litedb.begin()
    >>> table_name = 'table_1'
    >>> table = txn.table(table_name)
    >>> row = table.insert(None)
    >>> row = table.insert(1)
    >>> row = table.insert(2.5)
    >>> row = table.insert('text')
    >>> ...
    >>> row = table.insert({'name': 'litedb'})
    >>> txn.commit()

## 6. 获取行

    >>> txn = litedb.begin()
    >>> table = txn.table('table_1')
    >>> row = table.row(1)

## 7. 更新行数据

    >>> txn = litedb.begin()
    >>> table_name = 'table_1'
    >>> table = txn.table(table_name)
    >>> table.update(1, None)
    >>> table.update(2, 1)
    >>> table.update(3, 2.5)
    >>> table.update(4, 'text')
    >>> ...
    >>> table.update(9, {'name': 'litedb'})
    >>> txn.commit()

## 8. 删除行

    >>> txn = litedb.begin()
    >>> table = txn.table('table_1')
    >>> table.delete(1)
    >>> txn.commit()

## 9. 提交事务

    >>> txn = litedb.begin()
    >>> ... # write something
    >>> txn.commit()

## 10. 回滚事务

    >>> txn = litedb.begin()
    >>> ... # write something
    >>> txn.rollback()

## 11. 搜索数据 TODO

    >>> txn = litedb.begin()
    >>> table_name = 'table_1'
    >>> table = txn.table(table_name)
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
