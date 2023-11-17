# AWS setup

## Option 1: Using the AWS CLI

1. Create a symmetric KMS key in the region you want to use (eg `eu-north-1` for the Stockholm region): `aws kms --region $REGION create-key`. Copy the `KeyId` from the output, you'll need it in the next step. 
2. Update the JSON files [atlas-kms-role-policy.json](atlas-kms-role-policy.json) and [role-trust-policy.json](role-trust-policy.json), replacing `<AWS_ACCOUNT_ID>`, `<AWS_REGION>` and `<YOUR_KMS_KEY_ID>`.
3. Create an AWS role that you have permissions to assume: `aws iam create-role --role-name mongodb-client-side-encryption --assume-role-policy-document file://resources/role-trust-policy.json`. Copy the `Arn` from the output, you'll need it when configuring access for your application to your MongoDB cluster(s).
4. Give the role permissions to use your kms key: `aws iam put-role-policy --role-name mongodb-client-side-encryption --policy-name mongodb-kms-role-policy --policy-document file://resources/atlas-kms-role-policy.json`.


## Option 2: Using the AWS console

1. [Create a symmetric KMS key](https://docs.aws.amazon.com/kms/latest/developerguide/create-keys.html#create-symmetric-cmk).
2. [Create an AWS role that you have permissions to assume](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_create_for-user.html).
![image](/resources/create_role.png)
3. Give the role permissions for `kms:Encrypt` and `kms:Decrypt` on the kms key you created in step 1.
![image](/resources/create_policy.png)
