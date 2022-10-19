import boto3


def assume_role(aws_role_arn):
    sts_client = boto3.client("sts")
    assumed_role_object = sts_client.assume_role(
        RoleArn=aws_role_arn,
        RoleSessionName="AssumeRoleSession1",
    )

    return assumed_role_object["Credentials"]
