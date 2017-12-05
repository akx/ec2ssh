"""
Based on Amazon docs' example code.
"""
import datetime
import hashlib
import hmac
from urllib.parse import urlparse, urlencode


def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signature_key(key, datestamp, region, service):
    k_date = sign(('AWS4' + key).encode('utf-8'), datestamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')
    return k_signing


def get_aws4_signature_headers(access_key, secret_key, method, service, region, endpoint, parameters, payload=b''):
    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')
    parsed = urlparse(endpoint)
    canonical_uri = (parsed.path or '/')
    canonical_querystring = urlencode(sorted(parameters.items()))
    host = parsed.hostname
    canonical_headers = 'host:{host}\nx-amz-date:{amzdate}\n'.format(host=host, amzdate=amzdate)
    signed_headers = 'host;x-amz-date'
    payload_hash = hashlib.sha256(payload).hexdigest()
    canonical_request = '\n'.join(
        (method, canonical_uri, canonical_querystring, canonical_headers, signed_headers, payload_hash))
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = '/'.join((datestamp, region, service, 'aws4_request'))
    string_to_sign = '\n'.join(
        (algorithm, amzdate, credential_scope, hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()))
    signing_key = get_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, (string_to_sign).encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = '{algorithm} Credential={access_key}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}'.format(
        algorithm=algorithm,
        access_key=access_key,
        credential_scope=credential_scope,
        signed_headers=signed_headers,
        signature=signature,
    )

    return {
        'host': host,
        'x-amz-date': amzdate,
        'Authorization': authorization_header,
    }
