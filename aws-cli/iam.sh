aws iam create-role --role-name mongodb-client-side-encryption --assume-role-policy-document file://role-trust-policy.json
aws iam put-role-policy --role-name mongodb-client-side-encryption --policy-name mongodb-kms-role-policy --policy-document file://atlas-kms-role-policy.json
