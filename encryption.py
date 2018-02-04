# -*- coding: utf-8 -*-
'''
Encryption library
@author:    MarcoXZh3
@version:   0.0.1
'''
import json
import random
from Crypto import Random
from Crypto.Cipher import AES


class Cipher(object):
    '''
    The chipher class
    '''

    DATA_LENGTH = 1024  # 1024 bytes = 8192 bits
    KEY_LENGTH  = 32     # 32 bytes = 256 bits
    DUMMY       = ''.join([chr(i) for i in range(33, 127)]).encode()
    QUOTE       = '~~~'.encode()


    def __init__(self, key, mode=AES.MODE_EAX):
        '''
        Initialize the cipher
        @param {str}    key     the key of the cipher
        '''
        self.key = key[:]
        self.mode = mode
        self.iv = bytes([0] * AES.block_size)
    # def __init__(self, key, mode=AES.MODE_EAX)


    def encrypt(self, msg):
        '''
        Encryption
        @param {str}    msg     the message to be encrypted
        @returns {bytes}        the encrypted bytes
        '''
        msg = list(msg.encode())

        # Generate dummy bytes -- all those in "DUMMY" but not in "data"
        dummy = [d for d in self.DUMMY if d not in msg]

        # Salt "msg" with "dummy", then append "QUOTE" and "dummy"
        while len(msg) + len(self.QUOTE) + len(dummy) < self.DATA_LENGTH:
            msg.insert(random.randint(0, len(msg)), random.choice(dummy))
        # while len(msg) + len(self.QUOTE) + len(dummy) < self.DATA_LENGTH
        msg += list(self.QUOTE) + dummy
        msg = bytes(msg)

        # Prepare the key
        key = self.key.encode()
        while len(key) < self.KEY_LENGTH:
            key += key
        # while len(key) < self.KEY_LENGTH

        # Encrypt the salted bytes
        return AES.new(key[:self.KEY_LENGTH], self.mode, self.iv).encrypt(msg)
    # def encrypt(self, data)


    def decrypt(self, data):
        '''
        Decrypt bytes width password
        '''
        # Prepare the key
        key = self.key.encode()
        while len(key) < self.KEY_LENGTH:
            key += key
        # while len(key) < self.KEY_LENGTH

        # Decrypt the data
        data = AES.new(key[:self.KEY_LENGTH], self.mode, self.iv).decrypt(data)

        # Unsalt, split by the last "QUOTE", and the right most part is "dummy"
        fields = data.split(self.QUOTE)
        data, dummy = self.QUOTE.join(fields[:-1]), fields[-1]
        data = bytes([d for d in data if d not in dummy])

        # Return the data in bytes
        return data.decode()
    # def decrypt(self, data)


    def save(self, path, msg):
        '''
        Save message to file
        @param {str}    path    the path of the file
        @param {str}    msg     the message to be saved
        '''
        data = self.encrypt(msg)
        f = open(path, 'wb')
        f.write(data)
        f.close()
    # def save(self, path, msg)


    def load(self, path):
        '''
        Load message from file
        @param {str}    msg     the message to be loaded
        @param {str}    path    the path of the file
        '''
        f = open(path, 'rb')
        data = f.read()
        f.close()
        return self.decrypt(data)
    # def load(self, path)


    def __str__(self):
        '''
        To string
        @returns {str}      the string format of the cipher
        '''
        MODES = {
            1:  'MODE_ECB',
            2:  'MODE_CBC',
            3:  'MODE_CFB',
            5:  'MODE_OFB',
            6:  'MODE_CTR',
            7:  'MODE_OPENPGP',
            8:  'MODE_CCM',
            9:  'MODE_EAX',
            10: 'MODE_SIV',
            11: 'MODE_GCM',
            12: 'MODE_OCB'
        } # MODES = { ... }
        return 'Cipher<mode=%s, key=%s>' % (MODES[self.mode], self.key)
    # def __str__(self)
# class Cipher(object)


def main():
    '''
    The main entry
    '''
    msg = '~This这 - is是 ^ a一 @ piece条 # of $ text文本 %% acting作为 ' + \
          '& as * the ( 原始raw ) 信息message! +'
    password = '此处为密码!~'

    # encryption/decryption
    cipher = Cipher(password)
    print(cipher)
    enc = cipher.encrypt(msg)
    dec = cipher.decrypt(enc)
    print(msg)
    print(dec)
    print(msg == dec)

    # export/import
    obj = {
        'text':     msg,
        'keyword':  'Hello World!'
    } # obj = { ... }
    msg = json.dumps(obj, indent=4)
    cipher.save('encryption.test.so', msg)
    dec = cipher.load('encryption.test.so')
    obj1 = json.loads(dec)
    print(json.dumps(obj, indent=4, ensure_ascii=False))
    print(json.dumps(obj1, indent=4, ensure_ascii=False))
    print(obj == obj1)
# def main()


if __name__ == '__main__':
    main()
# if __name__ == '__main__'
