# Python/flask application implementing crypto shredding

## Initial Setup

### AWS
Follow the instructions in [AWS_Setup.md](./resources/AWS_Setup.md)

### MongoDB Atlas
1. Create an Atlas cluster for application data.
2. Optional: Create a separate cluster for the keyvault.
3. Add database user in Atlas allowing access from the IAM role.
![image](./resources/db_access.png)


### Local Environment
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


## Run the Application

1. Build the docker image: `docker build --tag flask-mongodb-cryptoshredding-example:latest .`
2. Run the docker image: 
`docker run -dp 5000:5000 --name flask-mongodb-cryptoshredding -e AWS_ACCESS_KEY_ID -e AWS_SESSION_TOKEN -e AWS_DEFAULT_REGION -e AWS_SECRET_ACCESS_KEY -e FLASK_SECRET_KEY -e ATLAS_AWS_ROLE -e ATLAS_AWS_KMS_KEY -e ATLAS_CLUSTER_HOSTNAME -e ATLAS_KEYVAULT_CLUSTER_HOSTNAME flask-mongodb-cryptoshredding-example:latest`
3. Access the running container in your browser on `http://localhost:5000`
4. Optionally create some indexes to support the query patterns (this requires the container to be running already): `docker exec -it flask-mongodb-cryptoshredding flask --app flaskapp create-indexes`
