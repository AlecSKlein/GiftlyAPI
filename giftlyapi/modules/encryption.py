__author__ = 'Alec'

from Crypto.Cipher import AES
import bcrypt

def generate_cipher(aes_key, aes_mode, init_vector):
    return AES.new(aes_key, aes_mode, IV=init_vector)

def encrypt_message(message, cipher):
    return cipher.encrypt(message)

def decrypt_message(encrypted_message, cipher):
    return cipher.decrypt(encrypted_message)

def hash_password(password):
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    print hash
    return hash

def check_hashed_password(password, hashed):
    try:
        if bcrypt.hashpw(password.encode('utf-8'), hashed.encode('utf-8')) == hashed:
            return True
        else:
            return False
    except ValueError, e:
        print e.message
