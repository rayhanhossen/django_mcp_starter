import time
from datetime import datetime, timedelta
from django.core.cache import cache, CacheKeyWarning
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import warnings
from mf_analytics.settings import APP_NAME

warnings.filterwarnings('ignore', category=CacheKeyWarning)

def cached_execute_query(connection, query, params = {}, cache_domain = APP_NAME):

    # Specify an encryption key
    encryption_key = b'bits_credentials'

    # Specify an initialization vector (IV)
    iv = b'bits_credentials'

    # Create an AES-CBC cipher object with the key and IV
    cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend())

    # Encrypt the key
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_key = padder.update((cache_domain+query+str(params)).encode('utf-8')) + padder.finalize()
    cache_key = encryptor.update(padded_key) + encryptor.finalize()

    # Get cached data
    try:
        cached_response = cache.get(cache_key)
    except:
        cached_response = None

    # Serve cached data upon availability
    if cached_response is not None:
        results = cached_response
    else:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            cache.set(cache_key, results)

    return results




# # This is for manual queueing of heavy cache
# # Specify an encryption key
# encryption_key = b'bits_credentials'
#
# # Specify an initialization vector (IV)
# iv = b'bits_credentials'
#
# # Create an AES-CBC cipher object with the key and IV
# cipher = Cipher(algorithms.AES(encryption_key), modes.CBC(iv), backend=default_backend())
#
# def cached_execute_query(connection, query, params = {}, cache_domain = APP_NAME):
#
#     # Encrypt the key
#     encryptor = cipher.encryptor()
#     padder = padding.PKCS7(128).padder()
#     padded_key = padder.update((cache_domain+query+str(params)).encode('utf-8')) + padder.finalize()
#     cache_key = encryptor.update(padded_key) + encryptor.finalize()
#
#     # Get cached data
#     try:
#         cached_response = cache.get(cache_key)
#     except:
#         cached_response = None
#
#     # checking if someone is already fetching the same data
#     if cached_response == 'fetching data':
#
#         if datetime.now() - cache.get(str(cache_key) + '_timestamp') < timedelta(minutes=2):
#             time.sleep(0.5)  # 0.5 seconds
#         else:
#             cache.delete(str(cache_key) + '_timestamp')
#
#         return cached_execute_query(connection, query, params, cache_domain)
#
#     # serving data from cache if exists
#     elif cached_response is not None:
#         return cached_response
#
#     # fetching data from database if it doesn't exist in cache
#     else:
#         cache.set(cache_key, 'fetching data')
#         cache.set(str(cache_key) + '_timestamp', datetime.now())
#         with connection.cursor() as cursor:
#             cursor.execute(query, params)
#             results = cursor.fetchall()
#
#         cache.delete(str(cache_key) + '_timestamp')
#
#         return results

