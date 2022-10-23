# Python/flask application implementing crypto shredding

## Initial Setup

### AWS setup
1. [Create a symmetric KMS key](https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.
html#create-symmetric-cmk).
#### AWS Using CLI
Create an AWS KMS master key (see aws-cli/kms.sh)

2. [Create an AWS role that you have permissions to assume](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html).
![image](./resources/create_role.png)
3. Give the role permissions for `kms:Decrypt` and `kms:Decrypt` on the kms key you created in step 1.
![image](./resources/create_policy.png)
#### AWS Using CLI
create an AWS IAM role allowing this app to encrypt / decrypt data keys (see aws-cli/iam.sh)

4. Create an Atlas cluster for application data.
5. Optional: Create a separate cluster for the keyvault.
6. Add database user in Atlas allowing access from the IAM role.
![image](./resources/db_access.png)


### Local Environment setup
The application relies on environment variables for configuration. Set the below environment variables using `export VAR_NAME=value`. Alternatively, you can add the values to an env file with `VAR_NAME=value` on each line, and replace all of the `-e VAR_NAME` in the `docker run` command with `--env-file <your_env_file_path>`.

| Env var | Description | Example | Required |
| --- | --- | --- | --- |
| AWS_ACCESS_KEY_ID | AWS access key | AKIAIOSFODNN7EXAMPLE | Yes
| AWS_SECRET_ACCESS_KEY | AWS secret key | wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY | Yes
| AWS_SESSION_TOKEN | AWS session token - required if using temporary AWS credentials | IQoJ63JpZ2luX2VjEG4aCAVzLWVhc3QtMSJHMEUCIHmo..... | No
| AWS_DEFAULT_REGION | AWS region where the KMS key is created | eu-north-1 | Yes
| ATLAS_AWS_ROLE | AWS arn of role to assume | arn:aws:iam::123456789123:role/name_of_role | Yes
| ATLAS_AWS_KMS_KEY | AWS arn of kms key | arn:aws:kms:eu-north-1:123456789123:key/a31df5ca-5759-4c4d-a4a4-cd6012b0c74f | Yes
| ATLAS_CLUSTER_HOSTNAME | atlas cluster hostname | tommcc-democluster-0.xxxx.mongodb.net | Yes
| ATLAS_KEYVAULT_CLUSTER_HOSTNAME | atlas cluster hostname (can be the same as the previous setting) | tommcc-keyvault-0.xxxx.mongodb.net | Yes
| FLASK_SECRET_KEY | Secret key for flask application session storage. Set to any random string.  | fHYPvv_g9ZN3xUV8LFTuVqenJ-4B_hWP-Ak9BV8LXaA | Yes


### Run with Docker

1. Build the docker image: `docker build --tag flask-mongodb-cryptoshredding-example:latest .`
2. Run the docker image: 
`docker run -dp 5000:5000 --name flask-mongodb-cryptoshredding -e AWS_ACCESS_KEY_ID -e AWS_SESSION_TOKEN -e AWS_DEFAULT_REGION -e AWS_SECRET_ACCESS_KEY -e FLASK_SECRET_KEY -e ATLAS_AWS_ROLE -e ATLAS_AWS_KMS_KEY -e ATLAS_CLUSTER_HOSTNAME -e ATLAS_KEYVAULT_CLUSTER_HOSTNAME flask-mongodb-cryptoshredding-example:latest`
3. Access the running container on `http://localhost:5000`
4. Optionally create some indexes to support the query patterns: `docker exec -it flask-mongodb-cryptoshredding flask --app flaskapp create-indexes`

## Using the UI

TODO