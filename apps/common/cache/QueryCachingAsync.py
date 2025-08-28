from django.core.cache import cache, CacheKeyWarning
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import warnings
from mf_analytics.settings import APP_NAME
from channels.db import database_sync_to_async
from django.db import connections
from django.db import close_old_connections
from asgiref.sync import sync_to_async

warnings.filterwarnings('ignore', category=CacheKeyWarning)

async def async_cached_execute_query(connection, query, params = {}, cache_domain = APP_NAME):

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

    # Check for cached response
    cached_response = await sync_to_async(cache.get)(cache_key)

    if cached_response is not None:
        return cached_response

    # Use database_sync_to_async to run the execute_query in a synchronous context
    results = await database_sync_to_async(execute_query)(connection, query, params)

    # Cache the results
    await sync_to_async(cache.set)(cache_key, results)
    return results


def execute_query(connection, query, params):
    connection = connections[f'{connection}']  # Use the correct database alias here
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        data = cursor.fetchall()
    close_old_connections()
    return data

