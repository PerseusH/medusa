# -*- coding:utf-8 -*-


import threading
import functools
import logging
import time
import mysql.connector

# get cwd of app
import os, sys; app_name='app'; cwd, offset=os.getcwd(), len(app_name); sys.path.append(cwd[:cwd.find(app_name)+offset])
print sys.path


_conn = _db_ctx = None


def create_engine(user, password, database, host='127.0.0.1', port='3306', **kw):
    """
    Create db connection enggine.
    """
    global _conn
    if _conn:
        raise DBError('Connection has already been initialized!')

    params = dict(
            user=user, password=password, database=database, host=host, port=port,
            use_unicode=True, charset='utf8', autocommit=False, buffered=True, collation='utf8_general_ci'
            #数据库默认事务是自动提交的，执行增删改查等操作时，会自动提交事务，如果关闭autocommit，那么执行完增删改查后需要再执行 commit 来提交事务，否则sql就不会执行
            )
    params.update(kw)

    _conn = lambda: mysql.connector.connect(**params)


class _DBCtx(threading.local):
    """
    DB context with thread-local.
    """
    def __init__(self):
        self.connection = None
        self.transactions = 0

    def cursor(self):
        if self.connection is None:
            global conn
            _c_start = time.time()
            self.connection = _conn()
            _c_stop = time.time()
            logging.info('Connecting time: %f' % (_c_stop - _c_start))

        return self.connection.cursor()

    def cleanup(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

        self.transactions = 0


class _ConnectionCtx():
    """
    ContextManager for db connection.
    """
    def __enter__(self):
        logging.info('Enter _ConnectionCtx.')
        global _db_ctx
        if _db_ctx is None:
            _db_ctx = _DBCtx()

        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        '''
        exc_type: <type 'exceptions.XXXError'>
        exc_value: <Exception Message>
        exc_trace: <traceback object at 0x1004a8128>
			Traceback (most recent call last):
			  File "./with_example02.py", line 19, in <module>
			    sample.do_something()
			  File "./with_example02.py", line 15, in do_something
			    bar = 1/0
			ZeroDivisionError: integer division or modulo by zero
        '''
        logging.info('Exit _ConnectionCtx.')
        global _db_ctx
        if _db_ctx is not None:
            _db_ctx.cleanup()


def with_connection(func):
    """
    Decorator for _ConnectionCtx
    """
    @functools.wraps(func)
    def wrapper(*args, **kw):
        global _conn
        if _conn is None:
            raise DBError('No connection to db!')

        with _ConnectionCtx():
            return func(*args, **kw)

    return wrapper



@with_connection
def _select(_sql, *_args):
    '''
    Select data from db.
    '''
    cursor = None
    _sql = _sql.replace('?', '%s')

    try:
        cursor = _db_ctx.cursor()
        cursor.execute(_sql) if _args is () else cursor.execute(_sql, _args)

        fields = [field[0] for field in cursor.description]

        if cursor.rowcount > 0:
            return {'data': [dict(zip(fields, data)) for data in cursor.fetchall()], 'count': cursor.rowcount}
        else:
            logging.warning('Got nothing from db!')
            return None

    except mysql.connector.Error, e:
        logging.error(e.msg)

    finally:
        if cursor is not None:
            cursor.close()


def select(*args):
    '''
    Select data list.
    '''
    if args[0].lower().startswith('select '):
        _sql = args[0]
    else:
        _sql = 'select %s from %s %s' % (args[1], args[0], '' if args[-1] is args[1] else 'where %s' % ' and '.join(args[2:-1]))

    return _select(_sql, *() if args[-1] is args[1] else args[-1]) 


def select_item(*args):
    '''
    Select single data.
    '''
    result = select(*args)
    return result and result['data'][0]


def select_value(*args):
    '''
    Select single value.
    '''
    result = select_item(*args)
    return result and result.values()[0]


@with_connection
def _modify(_sql, *_args):
    '''
    Modify db data.
    '''
    global _db_ctx
    cursor = None
    _sql = _sql.replace('?', '%s')
    logging.info('%s, %s', _sql, _args)

    try:
        cursor = _db_ctx.cursor()
        cursor.execute(_sql, _args)

        _db_ctx.connection.commit()

        if cursor.rowcount <= 0:
            logging.warning('Sql executed failed.')

        return cursor.rowcount

    except mysql.connector.Error, e:
        _db_ctx.connection.rollback()
        logging.error(e.msg)

    finally:
        if cursor is not None:
            cursor.close()


def update(*sql, **args):
    '''
    Update data.
    '''
    if sql[0].lower().startswith('update '):
        _sql = sql[0]

        fields = _sql.split(' where')[0].split('set ')[1].replace(' ', '').split(',')
        fields = [s.split('=')[0] for s in fields]
    else:
        fields = args.keys()

        _sql = 'update %s set %s %s' % (sql[0], ', '.join(map(lambda f: '%s=?' % f, fields)), 'where %s' % ' and '.join(sql[1:]) if sql[-1] is not sql[0] else '')

    _args = (args[f] for f in fields)

    return _modify(_sql, *_args)


def insert(sql, **args):
    '''
    Insert data.
    '''
    if sql.lower().startswith('insert '):
        fields = sql.split(')')[0].split('(')[1].replace(' ', '').split(',')
        _sql = sql
    else:
        fields = args.keys()
        _sql = 'insert into %s(%s) values(%s)' % (sql, ', '.join(fields), ', '.join(['?' for f in fields]))

    _args = (args[f] for f in fields)

    return _modify(_sql, *_args)


def delete(*args):
    '''
    Delete data.
    '''
    if args[0].lower().startswith('delete '):
        _sql = args[0]
    else:
        _sql = 'delete from %s %s' % (args[0], '' if args[-1] is args[0] else 'where %s' % ' and '.join(args[1:-1]))

    return _modify(_sql, *() if args[-1] is args[0] else args[-1])


class DBError(Exception):
    pass


class _TransactionCtx():
    '''
    Create context-manager for transaction.
    '''
    def __enter__(self):
        global _db_ctx
        if _db_ctx is None:
            _db_ctx = _DbCtx()

        _db_ctx.transactions += 1

        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        global _db_ctx
        _db_ctx.transactions -= 1

        try:
            if _db_ctx.transactions == 0:
                if exc_type is None:
                    _db_ctx.connection.commit()
                else:
                    _db_ctx.connection.rollback()
        except:
            _db_ctx.connection.rollback()

        finally:
            if _db_ctx.transactions == 0:
                _db_ctx.cleanup()


def with_transaction(func):                
    '''
    Decorator for transaction.
    '''
    @functools.wraps(func)
    def wrapper(*args, **kw):
        with _TransactionCtx():
            return func(*args, **kw)

    return wrapper


class Dict(dict):
    '''
    Generate a dict which could access keys directly.
    '''
    def __init__(self, **kw):
        super(Dict, self).__init__(**kw)

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r'"Dict" object does not have attribute "%s"' % key)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    create_engine('root', 'root', 'perseus')
    #update('user', 'username="Duhui"', password='Pegasus', username='Twocold')
    #update('update user set username=?, password=? where username="Twocold"', password='eurika', username='Archimedes')
    #insert('user', username='Perseus', password='Pegasus')
    #insert('insert into user(username, gender, password) values(?, ?, ?)', gender=1, password='Apple', username='Newton')
    #delete('user', 'username=?', ('Newton',))
    #delete('delete from user where username=?', ('Perseus',))
    time.sleep(1)
    data = select('user', '*')
    from libs.utils import json
    #logging.info('Count: %s', data['count'])
    logging.info(json.dumps(data, indent=4))
