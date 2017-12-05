import xml.etree.ElementTree as ET
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from ec2ssh.aws_signing import get_aws4_signature_headers
from ec2ssh.excs import AWSError


def convert_response_node(node):
    # TODO: assumes there are no attributes on nodes
    if not node.getchildren():
        return (node.tag, node.text)
    if all(c.tag == 'item' for c in node.getchildren()):
        children = [convert_response_node(child)[1] for child in node.getchildren()]
    else:
        children = dict(convert_response_node(c) for c in node.getchildren())
    return (node.tag, children)


class AWSResponse:
    def __init__(self, response_data, error=None, headers=None):
        self.response_data = response_data
        self.error = error
        self.headers = (headers or {})

    def as_etree(self, strip_namespaces=True):
        tree = ET.fromstring(self.response_data)
        if strip_namespaces:
            for node in tree.iter():
                node.tag = node.tag.split('}')[-1]
        return tree


def do_aws_request(access_key_id, secret_key, service, region, params, payload=b'', raise_errors=True):
    endpoint = 'https://{service}.{region}.amazonaws.com'.format(service=service, region=region)
    headers = get_aws4_signature_headers(
        access_key_id,
        secret_key,
        method=('POST' if payload else 'GET'),
        service=service,
        region=region,
        endpoint=endpoint,
        parameters=params,
        payload=payload,
    )
    request = Request(endpoint + '?' + urlencode(params), headers=headers)
    try:
        ur = urlopen(request)
        resp = AWSResponse(ur.read(), error=None, headers=dict(ur.info()))
    except HTTPError as he:
        resp = AWSResponse(he.fp.read(), error=he.code, headers=he.headers)
    if resp.error and raise_errors:
        raise AWSError(resp)
    return resp
