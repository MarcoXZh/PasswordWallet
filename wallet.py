# -*- coding: utf-8 -*-
'''
The password wallet
@author:  MarcoXZh3
@version: 0.0.1
'''
import os
import random
import re
import sqlite3
import time
from datetime import datetime
from encryption import Cipher


class Wallet(object):
    '''
    The wallet class
    '''
    SEPARATOR = '~'
    CODES = {
        'SUCCEED':      0,
        'NOT_FOUND':    1,
        'FAILED':       2,
    } # CODES = { ... }


    def __init__(self, key, db_name='data', table_name='data'):
        '''
        Initialize the wallet
        @param {str}    key         key to unlock the wallet
        @param {str}    db_name     name of the database
        @param {str}    table_name  name of the table
        '''
        folder = 'dist'
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.key = key
        self.cipher = Cipher(key)
        self.db = folder + '/' + db_name
        self.table = table_name
    # def __init__(self, key, db_name='data', table_name='data')


    def search(self, pattern=None, show=False):
        '''
        Find all password matching the filter regex pattern.
        If pwd provided, then return decrypted "pwd" field
        @param {dict}   pattern     the patterns for filtering
        @param {str}    pwd         the owner password
        @return {list}              the list of target passwords
        '''
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        # Find the "pwd" column
        cols = cur.execute('PRAGMA table_info(%s);' % self.table).fetchall()

        # Query the records
        if not pattern:
            rows = cur.execute('SELECT * FROM %s;' % self.table).fetchall()
        else:
            # Define regex function for SQLite
            conn.create_function('REGEXP', 2,
                                 lambda expr, item:\
                                    re.compile(expr).search(item) is not None)
            condisions = []
            regexes = []
            for k, v in pattern.items():
                condisions.append('%s REGEXP ?' % k)
                regexes.append(v)
            # for k, v in pattern.items()
            rows = cur.execute('SELECT * FROM %s WHERE %s;' %
                               (self.table, ' AND '.join(condisions)),
                               regexes \
            ).fetchall() # rows = cur.execute( ... ).fetchall()
        # else - if not pattern

        # Prepare the records, with "pwd" decrypted
        results = []
        for row in rows:
            record = {}
            for i, col in enumerate(cols):
                record[col[1]] = row[i]
            # for i, col in enumerate(cols)
            if show:
                record['pwd'] = self.cipher.decrypt(record['pwd'])
            # if show
            results.append(record)
        # for row in rows
        conn.close()

        return results
    # def search(self, pattern=None, show=False)


    def add(self, pwd, name=None, site=None, desc=None):
        '''
        Add a new password
        @param {str}    pwd     password of the record, to be encrypted
        @param {str}    name    name of the record
        @param {str}    site    site of the record
        @param {str}    desc    description of the record
        @return {tuple}         (status code in CODES, supplement message)
        '''
        # Verify inputs - name and password
        if pwd is None or pwd.strip() == '':
            return (self.CODES['FAILED'], 'Empty password to add')
        # if pwd is None or pwd.strip() == ''
        old_name = name
        if name is None or name.strip() == '':
            name = 'Guest'
        # if name is None or name.strip() == ''
        old_site = site
        if site is None or site.strip() == '':
            site = 'Default'
        # if site is None or site.strip() == ''
        if desc is None:
            desc = ''
        # if desc is None

        # Create the database if not exist
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS %s (
                id          INTEGER PRIMARY KEY,
                created     INTEGER,
                modified    INTEGER,
                name        TEXT NOT NULL,
                pwd         BLOB,
                site        TEXT NOT NULL,
                desc        TEXT,
                UNIQUE(name, site)
            );
        ''' % self.table) # cur.execute(''' ... ''')
        conn.commit()

        # Prepare the data - when name-site provided, they should be new
        rows = cur.execute('SELECT name, site FROM %s;' % self.table).fetchall()
        if (old_name is not None and not old_name.strip() == '') and \
           (old_site is not None and not old_site.strip() == '') and \
           (old_name, old_site, ) in rows:
            return (self.CODES['FAILED'], 'Record already exists')
        # if ...
        # Otherwise - rename "name" if necessary
        cnt = 2
        while (name, site, ) in rows:
            regex = r'\%s\d+$' % self.SEPARATOR
            old_name = self.SEPARATOR.join(re.split(regex, name)[:-1]) \
                       if re.search(regex, name) else name
            name = '%s%s%d' % (old_name, self.SEPARATOR, cnt)
            cnt += 1
        # while (name, site, ) in rows
        created = int(time.mktime(datetime.now().timetuple()))
        enc = self.cipher.encrypt(pwd)

        # Save the data
        cur.execute('''
            INSERT INTO %s (created, modified, name, pwd, site, desc)
                    VALUES (?, ?, ?, ?, ?, ?);
            ''' % self.table, \
            (created, created, name, sqlite3.Binary(enc), site, desc, ) \
        ) # cur.execute(''' ... ''')
        conn.commit()
        conn.close()
        return (self.CODES['SUCCEED'], 'Add password succeeded')
    # def add(self, pwd, name=None, site=None, desc=None)


    def delete(self, id=None, name=None, site=None, pwd=None, desc=None):
        '''
        Delete a password
        @param {int}    id      id of the record
        @param {str}    name    name of the record
        @param {str}    site    site of the record
        @param {str}    pwd     password of the record, to be encrypted
        @param {str}    desc    description of the record
        @return {tuple}         (status code in CODES, supplement message)
        '''
        # Verify parameters - either id or name-site is required
        if not id or id <= 0:
            if name is None or name.strip() == '':
                return (self.CODES['FAILED'], 'Empty name to delete')
            # if name is None or name.strip() == ''
            if site is None or site.strip() == '':
                return (self.CODES['FAILED'], 'Empty site to delete')
            # if site is None or site.strip() == ''
        # if not id or id <= 0

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        # Find the target record
        if not id or id <= 0:
            ids = cur.execute('SELECT id from %s WHERE name=? AND site=?;' % \
                              self.table,
                              (name, site, )).fetchall()
            if len(ids) == 0:
                return (self.CODES['NOT_FOUND'], 'No record found to delete')
            # if len(ids) == 0
            id = ids[0][0]
        else:
            ids = cur.execute('SELECT id from %s;' % self.table).fetchall()
            if (id, ) not in ids:
                return (self.CODES['NOT_FOUND'], 'No record found to delete')
            # if (id, ) not in ids
        # if not id or id <= 0

        # Delete it
        cur.execute('DELETE FROM %s WHERE id=?;' % self.table, (id, ))
        conn.commit()
        conn.close()
        return (self.CODES['SUCCEED'], 'Delete password succeeded')
    # def delete(self, id=None, name=None, site=None, pwd=None, desc=None)


    def update(self, id=None, name=None, site=None, pwd=None, desc=None):
        '''
        Update a password
        @param {int}    id      id of the record
        @param {str}    name    name of the record
        @param {str}    site    site of the record
        @param {str}    pwd     password of the record, to be encrypted
        @param {str}    desc    description of the record
        @return {tuple}         (status code in CODES, supplement message)
        '''
        # Verify parameters
        if not id:  # name-site to search; password/description to be updated
            if name is None or name.strip() == '':
                return (self.CODES['FAILED'], 'Empty name to update')
            # if name is None or name.strip() == ''
            if site is None or site.strip() == '':
                return (self.CODES['FAILED'], 'Empty site to update')
            # if site is None or site.strip() == ''
            if (pwd is None or pwd.strip() == '') and \
               (desc is None or desc.strip() == ''):
                return (self.CODES['FAILED'], 'Nothing to update')
            # if ...
        else:       # id to search; others to be updated
            if (name is None or name.strip() == '') and \
               (site is None or site.strip() == '') and \
               (pwd is None or pwd.strip() == '') and \
               (desc is None or desc.strip() == ''):
                return (self.CODES['FAILED'], 'Nothing to update')
            # if ...
        # if not id

        conn = sqlite3.connect(self.db)
        cur = conn.cursor()

        # Prepare data while searching the target record
        targets = []
        values = []
        if pwd:
            targets.append('pwd=?')
            values.append(self.cipher.encrypt(pwd))
        # if password
        if desc:
            targets.append('desc=?')
            values.append(desc)
        # if desc

        # Find the target record
        if not id:
            ids = cur.execute('SELECT id from %s WHERE name=? AND site=?;' % \
                              self.table,
                              (name, site, )).fetchall()
            if len(ids) == 0:
                return (self.CODES['NOT_FOUND'], 'No record found to update')
            # if len(ids) == 0
            id = ids[0][0]
        else:
            ids = cur.execute('SELECT id from %s;' % self.table).fetchall()
            if (id,)  not in ids:
                return (self.CODES['NOT_FOUND'], 'No record found to update')
            # if (id,)  not in ids

            # name and/or site, password, description to be updated
            if name:
                targets.append('name=?')
                values.append(name)
            # if name
            if site:
                targets.append('site=?')
                values.append(site)
            # if site
        # if not id

        # Finalize data and update
        targets.append('modified=?')
        values.append(int(time.mktime(datetime.now().timetuple())))
        cur.execute('UPDATE %s SET %s WHERE id=%d;' % \
                    (self.table, ', '.join(targets), id),
                    values)
        conn.commit()
        conn.close()
        return (self.CODES['SUCCEED'], 'Update password succeeded')
    # def update(self, id=None, name=None, site=None, pwd=None, desc=None)


    def __str__(self):
        '''
        To string
        @returns {str}      the string format of the class
        '''
        return 'Wallet<key="%s", target="%s">' % \
               (self.key, self.db + '.' + self.table)
    # def __str__(self)
# class Wallet(object)


def main():
    '''
    The main entry - test the wallet functions
    '''
    records = [
        ('password1', ),
        ('password2', 'name2', ),
        ('密码3', '姓名3', '站点3', ),
        ('password2', 'name2', ),         # NOT duplicated because not site
        ('密码3', '姓名3', '站点3', ),      # duplicated
    ] # records = [ ... ]

    wallet_key = 'My Wallet钱包 Password密码'
    wallet = Wallet(wallet_key, 'tmp_db.db', 'tmp_table')
    print('%s\n' % wallet)

    # Add - 4 added
    print('Add:')
    for i, r in enumerate(records):
        print('%d/%d - %s' % (i+1, len(records), wallet.add(*r)))
    # for i, r in enumerate(records)

    # List all, not showing the password - 4 records
    print('\nList all:')
    records = wallet.search(show=False)
    for i, r in enumerate(records):
        print('%d/%d - %s' % \
              (i+1, len(records),   # i == 4 means password
              [v[:10] if i == 4 else v for i, v in enumerate(r)]))
    # for i, r in enumerate(records)

    # Delete - 2 deleted
    print('\nDelete:')
    print(wallet.delete())          # delete nothing
    print(wallet.delete(3))         # delete something
    print(wallet.delete(3))         # delete non-existing
    print(wallet.delete(None, 'name2', 'Default'))  # delete by name-site
    print(wallet.delete(None, 'no-name', 'no-site'))  # delete non-existing

    # Update - 2 deleted
    print('\nUpdate:')
    print(wallet.update())          # update nothing
    print(wallet.update(1))         # update nothing
    print(wallet.update(1, 'new-name2'))    # update something
    print(wallet.update(2, 'some-name'))    # update non-existing
    print(wallet.update(None, 'new-name2', 'Default'))
                                    # update nothing
    print(wallet.update(None, 'new-name2', 'Default', 'new-password'))
                                    # update by name-site
    print(wallet.update(None, 'new-name2', 'no-site', 'new-password'))
                                    # update non-existing

    # List all, showing the password
    print('\nList all:')
    records = wallet.search(show=True)
    for i, r in enumerate(records):
        print('%d/%d - %s' % (i+1, len(records), r))
    # for i, r in enumerate(records)

    # List some
    print('\nList some:')
    records = wallet.search({ 'name':r'\-' }, show=True)
    for i, r in enumerate(records):
        print('%d/%d - %s' % (i+1, len(records), r))
    # for i, r in enumerate(records)
    records = wallet.search({ 'name':r'\~', 'site':r'^\D' }, show=True)
    for i, r in enumerate(records):
        print('%d/%d - %s' % (i+1, len(records), r))
    # for i, r in enumerate(records)
# def main()


if __name__ == '__main__':
    main()
# if __name__ == '__main__'
