# -*- coding: utf-8 -*-
'''
The shell to access the wallet
@author:  MarcoXZh3
@version: 0.0.1
'''
import datetime
import getpass
import json
import re
import os
import sys
import time
from wallet import Wallet

KEY_PATH = 'dist'
KEY_FILE = 'key.log'
RETRY = 3


def action_add(wallet, *args):
    '''
    Add new password
    @param {Wallet} wallet  the wallet
    @param {list}   args    to be ignored
    '''
    try:
        # Get name
        name = input('Enter name: [Guest]').strip()
        if name == '':
            name = 'Guest'
        # if name == ''

        # Get password and confirmation
        pwd = getpass.getpass('Enter password:').strip()
        cnt = 1
        while pwd == '':
            if cnt == RETRY:
                return
            # if cnt == RETRY
            pwd = getpass.getpass('Empty, try again:').strip()
            cnt += 1
        # while pwd == ''
        pwd2 = getpass.getpass('Confirm password:').strip()
        cnt = 1
        while not pwd == pwd2:
            if cnt == RETRY:
                print('Maximum trials, quit')
                return
            # if cnt == RETRY
            pwd2 = getpass.getpass('Mismatch, try again:').strip()
            cnt += 1
        # while not pwd == pwd2

        # Get site
        site = input('Enter site: [Default]').strip()
        if site == '':
            site = 'Default'
        # if site == ''

        # Get description
        desc = input('Enter description: []').strip()
    except KeyboardInterrupt:
        print()
        return
    # try - except KeyboardInterrupt

    # Add to wallet
    result = wallet.add(pwd, name, site, desc)
    if (result[0] == 0):
        print('Password added to wallet')
    else:
        print('Error: %s' % result[1])
    # else - if (result[0] == 0)
# def action_add(wallet, *args)


def action_del(wallet, *args):
    '''
    Delete password
    @param {Wallet} wallet  the wallet
    @param {list}   args    to be ignored
    '''
    try:
        # Get name
        name = input('Enter name: [Guest]').strip()
        if name == '':
            name = 'Guest'
        # if name == ''

        # Get site
        site = input('Enter site: [Default]').strip()
        if site == '':
            site = 'Default'
        # if site == ''
    except KeyboardInterrupt:
        print()
        return
    # try - except KeyboardInterrupt

    # Delete from wallet
    result = wallet.delete(None, name, site)
    if (result[0] == 0):
        print('Password deleted from wallet')
    else:
        print('Error: %s' % result[1])
    # else - if (result[0] == 0)
# def action_del(wallet, *args)


def action_update(wallet, *args):
    '''
    Update password
    @param {Wallet} wallet  the wallet
    @param {list}   args    to be ignored
    '''
    try:
        # Get name
        name = input('Enter name: [Guest]').strip()
        if name == '':
            name = 'Guest'
        # if name == ''

        # Get site
        site = input('Enter site: [Default]').strip()
        if site == '':
            site = 'Default'
        # if site == ''

        # Get password and confirmation
        pwd = getpass.getpass('Enter password (empty = not change) []:').strip()
        if not pwd == '':
            pwd2 = getpass.getpass('Confirm password:').strip()
            cnt = 1
            while not pwd == pwd2:
                if cnt == RETRY:
                    print('Maximum trials, quit')
                    return
                # if cnt == RETRY
                pwd2 = getpass.getpass('Mismatch, try again:').strip()
                cnt += 1
            # while not pwd == pwd2
        # if not pwd == ''

        # Get description
        desc = input('Enter description (empty = not change) []:').strip()
    except KeyboardInterrupt:
        print()
        return
    # try - except KeyboardInterrupt

    # Update in wallet
    result = wallet.update(None, name, site, pwd, desc)
    if (result[0] == 0):
        print('Password updated in wallet')
    else:
        print('Error: %s' % result[1])
    # else - if (result[0] == 0)
# def action_update(wallet, *args)


def action_find(wallet, *args):
    '''
    Find target passwords
    @param {Wallet} wallet  the wallet
    @param {list}   args    arguments
    '''
    pattern = {}
    show = False
    for i, arg in enumerate(args[0]):
        if not i == len(args[0]) - 1:
            if re.search(r'^(name|site|desc)\=.+$', arg):
                k, v = arg.split('=')
                pattern[k] = v
            else:
                print('Unrecognized arg: "%s"' % arg)
                return
        elif arg.strip().lower() == 'true':
            show = True
        # if ... elif
    # for i, arg in enumerate(args[0])
    if len(pattern.keys()) == 0:
        pattern = None
    # if len(pattern.keys()) == 0

    # Find in wallet
    results = wallet.search(pattern, show)
    if results is None or results[0] == 0:
        print('No records found')
    else:
        for i, result in enumerate(results):
            result['created'] = datetime.datetime\
                                        .fromtimestamp(result['created'])\
                                        .isoformat()
            result['modified'] = datetime.datetime\
                                         .fromtimestamp(result['modified'])\
                                         .isoformat()
            if not show:
                result['pwd'] = str(result['pwd'][:10]) + ' ...'
            # if not show
            print('%d/%d - %s' % (i+1, len(results), \
                                  json.dumps(result, indent=4, ensure_ascii=False)))
        # for i, result in enumerate(results)
    # else - if results is None or results[0] == 0
# def action_find(wallet, *args)


def main():
    '''
    The main entry
    '''
    help_msg = '\n'.join([
        'Password Wallet shell:',
        '  Usage: python3 shell.py add',
        '     or: python3 shell.py del',
        '     or: python3 shell.py update',
        '     or: python3 shell.py find [name=R1 [site=R2 [desc=R3]] [True|False]]',
        '  R1, R2, R3: regular expression',
    ]) # help_msg = '\n'.join([ ... ])

    # Check keys
    key = None
    if not os.path.exists(KEY_PATH):
        os.makedirs(KEY_PATH)
    # if not os.path.exists(KEY_PATH)
    key_file = os.path.join(KEY_PATH, KEY_FILE)
    if os.path.exists(key_file):    # Get key from file
        f = open(key_file, 'r')
        key = f.read().strip()
        f.close()
    else:                           # Get key from console
        key = getpass.getpass('Enter the wallet key:').strip()
        cnt = 1
        while key == '':
            if cnt == RETRY:
                return
            # if cnt == RETRY
            key = getpass.getpass('Empty, try again:').strip()
            cnt += 1
        # while key == ''
        f = open(key_file, 'w')
        f.write(key + '\n')
        f.close()
    # else - if os.path.exists(key_file)

    # Initialize wallet
    wallet = Wallet(key)

    func = None
    try:
        func = getattr(sys.modules[__name__], 'action_%s' % sys.argv[1].strip())
    except:
        print(help_msg)
        func = None
    # try - except
    if func:
        func(wallet, sys.argv[2:])
    # if func
# def main()


if __name__ == '__main__':
    main()
# if __name__ == u'__main__'
