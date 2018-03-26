import boto3
from botocore.exceptions import ClientError
import requests


class StackException(Exception):
    pass


class StackInterrogationException(StackException):
    pass


class InstanceNotInAsgException(StackException):
    pass


def is_first_instance():
    """
    Returns True if the current instance is the first instance in the ASG group,
    sorted by instance_id.
    """
    try:
        # get instance id and aws region
        instance_details = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document',
                                        timeout=5).json()
        instance_id = instance_details['instanceId']
        instance_region = instance_details['region']
    except (requests.RequestException, ValueError, KeyError) as e:
        raise StackInterrogationException(e)

    try:
        # get instance's autoscaling group
        autoscaling_client = boto3.client('autoscaling', region_name=instance_region)
        response = autoscaling_client.describe_auto_scaling_instances(InstanceIds=[instance_id])
        assert len(response['AutoScalingInstances']) == 1
        autoscaling_group = response['AutoScalingInstances'][0]['AutoScalingGroupName']
    except ClientError as e:
        raise StackInterrogationException(e)
    except AssertionError:
        raise InstanceNotInAsgException()

    try:
        # list in-service instances in autoscaling group
        # instances being launched or terminated should not be considered
        response = autoscaling_client.describe_auto_scaling_groups(AutoScalingGroupNames=[autoscaling_group])
        assert len(response['AutoScalingGroups']) == 1
        autoscaling_group_instance_ids = sorted(
            instance['InstanceId']
            for instance in response['AutoScalingGroups'][0]['Instances']
            if instance['LifecycleState'] == 'InService'
        )
    except (ClientError, AssertionError) as e:
        raise StackInterrogationException(e)

    return autoscaling_group_instance_ids and autoscaling_group_instance_ids[0] == instance_id
