import argparse
import os
import sys

from ec2ssh.aws_config import get_aws_parameters
from ec2ssh.ec2 import get_ec2_instances, build_instance_map, match_machine, get_instance_identifiers
from ec2ssh.excs import UsageError


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--access-key-id', default=None)
    ap.add_argument('--secret-key', default=None)
    ap.add_argument('--ami-profile', default='default')
    ap.add_argument('--region', default=os.environ.get('AWS_REGION', 'us-east-1'))
    ap.add_argument('--ssh', default='ssh')
    ap.add_argument('--list', action='store_const', const='list', dest='action', default='connect')
    ap.add_argument('target', nargs='?')
    args = ap.parse_args()
    access_key_id, secret_key, region = get_aws_parameters(args)
    instances = get_ec2_instances(access_key_id, secret_key, region)
    instance_map = build_instance_map(instances)

    if args.action == 'list':
        for identifier in sorted(instance_map):
            print(identifier)
        return 0
    else:
        do_connect(instance_map, args.target, args.ssh)


def do_connect(instance_map, target, ssh='ssh'):
    if not target:
        raise UsageError('target is required when not listing instances')
    target_bits = target.rsplit('@', 1)
    machine_identifier = target_bits.pop(-1)
    username = (target_bits[0] if target_bits else 'ubuntu')
    machine = match_machine(instance_map, machine_identifier)
    cmd_args = [
        '/usr/bin/env',
        ssh,
        '{username}@{ip_address}'.format(
            username=username,
            ip_address=machine['ipAddress'],
        ),
    ]
    print('({})'.format(', '.join(sorted(get_instance_identifiers(machine)))))
    print('+ ' + ' '.join(cmd_args), flush=True, file=sys.stderr)
    os.execv('/usr/bin/env', cmd_args)


def wrapped_main():
    try:
        sys.exit(main() or 0)
    except UsageError as ue:
        print('{}: {}'.format(sys.argv[0], ue), file=sys.stderr)
        sys.exit(1)
