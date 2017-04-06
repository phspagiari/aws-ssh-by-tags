import StringIO
import paramiko
import boto3
import argparse
import json


def _cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", help="AWS Region", required=True)
    parser.add_argument("--user", help="SSH Username", required=True)
    parser.add_argument("--tags", help="AWS Tags to filter, in json format.", required=True)
    parser.add_argument("--privatekey", help="relative path of privatekey", required=True)
    parser.add_argument("--cmd-list", help="list of commands comma separated", required=False)
    parser.add_argument("--file-origin", help="relative path of the file you will send", required=False)
    parser.add_argument("--file-dest", help="absolute path of the destination", required=False)
    return parser.parse_args()


def filter_by_tag(resource, key_value_filter):
    custom_filter = [
        {
            'Name': 'tag:%s' % k, 'Values': [v]
        }
        for k, v in key_value_filter.iteritems()
    ]
    resp = resource.filter(Filters=custom_filter)
    return list(resp)


def connect(ssh_privatekey, ssh_hostname, ssh_username, command_list=None, file_origin=None, file_destination=None):
    k = StringIO.StringIO(ssh_privatekey)
    key = paramiko.RSAKey.from_private_key(k)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_hostname, username=ssh_username, pkey=key)
    if file_origin:
        print("[%s] Sending: %s" % (ssh_hostname, file_origin))
        sftp = ssh.open_sftp()
        sftp.put(file_origin, file_destination)
    if command_list:
        for cmd in command_list:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print("%s" % (stdout.read()))
            if stderr:
                print("%s" % (stderr.read()))
    ssh.close()


def get_private_key(key_file_location):
    with open(key_file_location, 'r') as fp:
        ssh_privatekey = fp.read()
    return ssh_privatekey


def instances_info(ec2, tags):
    instances = filter_by_tag(ec2.instances, tags)
    " - Instances found %s" % len(instances)
    details = {}
    for instance in instances:
        tags = {tag['Key']: tag['Value'] for tag in instance.tags}
        details[instance.id] = {'tags': tags, 'ip': instance.public_ip_address}
    return details


def conn(region):
    session = boto3.Session(region_name=region)
    return session.resource(service_name='ec2')


def main():
    args = _cli()
    region = args.region
    user = args.user
    tags = json.loads(args.tags)
    privatekey = args.privatekey
    cmd_list = args.cmd_list.replace(", ", ",").split(",")
    file_origin = args.file_origin
    file_dest = args.file_dest

    ec2 = conn(region)
    ssh_privatekey = get_private_key(privatekey)
    details = instances_info(ec2, tags)
    for i_id, info in details.iteritems():
        print("[{}]({}): {}".format(info['ip'], i_id, info['tags']['Name']))
        connect(
            ssh_privatekey=ssh_privatekey,
            ssh_hostname=info['ip'],
            ssh_username=user,
            file_origin=file_origin,
            file_destination=file_dest,
            command_list=cmd_list,
        )


if __name__ == '__main__':
    main()