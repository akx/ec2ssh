from fnmatch import fnmatch

from ec2ssh.aws_request import do_aws_request, convert_response_node
from ec2ssh.excs import UsageError


def get_ec2_instances(access_key_id, secret_key, region):
    params = {'Version': '2016-11-15', 'Action': 'DescribeInstances'}
    resp = do_aws_request(access_key_id, secret_key, 'ec2', region, params)
    tree = resp.as_etree()
    for instance_set in tree.findall('.//instancesSet'):
        yield from convert_response_node(instance_set)[1]


def get_instance_identifiers(instance):
    identifiers = {
        instance.get(key)
        for key in ('instanceId', 'dnsName', 'privateDnsName')
    }
    tags = {t['key'].lower(): t['value'] for t in instance.get('tagSet', ())}
    identifiers.add(tags.get('name'))
    yield from (identifier for identifier in identifiers if identifier)


def build_instance_map(instances):
    instance_map = {}

    for instance in instances:
        instance_map.update((identifier, instance) for identifier in get_instance_identifiers(instance))

    return instance_map


def match_machine(instance_map, machine_identifier):
    if machine_identifier in instance_map:  # It's a direct hit!!
        return instance_map[machine_identifier]

    matching_machines = {
        identifier
        for (identifier, instance)
        in instance_map.items()
        if identifier.startswith(machine_identifier) or fnmatch(identifier, machine_identifier)
    }
    if not matching_machines:
        raise UsageError(
            'No machines match "%s". Use `--list` to see all identifiers.' % machine_identifier
        )
    if len(matching_machines) > 1:
        identifiers = sorted(set('* "%s"' % identifier for identifier in matching_machines))
        raise UsageError(
            'More than one machine matches "%s":\n%s\nBe more specific.' % (
                machine_identifier,
                '\n'.join(identifiers)
            )
        )
    return instance_map[matching_machines.pop()]
