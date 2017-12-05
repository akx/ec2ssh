import os
from configparser import RawConfigParser


def get_aws_parameters(args):
    if args.access_key_id or args.secret_key:
        access_key_id = args.access_key_id
        secret_key = args.secret_key
        region = args.region
    else:
        rcp = RawConfigParser()
        rcp.read(os.path.expanduser('~/.aws/credentials'))
        rcp.read(os.path.expanduser('~/.aws/config'))
        access_key_id = rcp.get(args.ami_profile, 'aws_access_key_id')
        secret_key = rcp.get(args.ami_profile, 'aws_secret_access_key')
        region = rcp.get(args.ami_profile, 'region', fallback=args.region)
    return (access_key_id, secret_key, region)
