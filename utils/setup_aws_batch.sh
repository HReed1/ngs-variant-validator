#!/bin/bash

# --- 1. CONFIGURATION ---
# Change this to be globally unique!
BUCKET_NAME="ngs-variant-validator-work"
REGION="us-east-1"
QUEUE_NAME="ngs-spot-queue"

echo "🚀 Starting AWS Infrastructure Provisioning for NGS Pipeline..."

# --- 2. S3 & FINOPS ---
echo "📦 Creating S3 Bucket: $BUCKET_NAME..."
aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION > /dev/null

cat <<EOF > lifecycle.json
{
    "Rules": [{
        "ID": "Archive-Nextflow-Work",
        "Prefix": "",
        "Status": "Enabled",
        "Transitions": [{"Days": 14, "StorageClass": "GLACIER"}]
    }]
}
EOF
aws s3api put-bucket-lifecycle-configuration --bucket $BUCKET_NAME --lifecycle-configuration file://lifecycle.json
echo "✅ S3 Bucket created and 14-day Glacier FinOps rule applied."

# --- 3. IAM ROLES ---
echo "🔐 Creating IAM Roles & Profiles..."
cat <<EOF > ec2-trust.json
{
  "Version": "2012-10-17",
  "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]
}
EOF

# Create role (ignore error if it already exists from a previous run)
aws iam create-role --role-name NextflowECSInstanceRole --assume-role-policy-document file://ec2-trust.json 2>/dev/null || true
aws iam attach-role-policy --role-name NextflowECSInstanceRole --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name NextflowECSInstanceRole --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

aws iam create-instance-profile --instance-profile-name NextflowECSInstanceProfile 2>/dev/null || true
aws iam add-role-to-instance-profile --instance-profile-name NextflowECSInstanceProfile --role-name NextflowECSInstanceRole 2>/dev/null || true

# Give AWS IAM a few seconds to propagate the new role globally
sleep 10
echo "✅ IAM Roles configured."

# --- 4. AWS BATCH COMPUTE ENVIRONMENT ---
echo "⚙️  Auto-discovering Default VPC & Subnets..."
VPC_ID=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
SUBNETS=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[*].SubnetId' --output json)
SG_ID=$(aws ec2 describe-security-groups --filters Name=vpc-id,Values=$VPC_ID Name=group-name,Values=default --query 'SecurityGroups[0].GroupId' --output text)

echo "☁️  Creating AWS Batch EC2 Spot Environment..."
cat <<EOF > compute_env.json
{
  "computeEnvironmentName": "NGS-Spot-Env",
  "type": "MANAGED",
  "state": "ENABLED",
  "computeResources": {
    "type": "SPOT",
    "allocationStrategy": "SPOT_CAPACITY_OPTIMIZED",
    "minvCpus": 0,
    "maxvCpus": 64,
    "instanceTypes": ["optimal"],
    "subnets": $SUBNETS,
    "securityGroupIds": ["$SG_ID"],
    "instanceRole": "NextflowECSInstanceProfile"
  }
}
EOF

aws batch create-compute-environment --cli-input-json file://compute_env.json > /dev/null

# Wait for Compute Environment to be VALID
echo "⏳ Waiting for Compute Environment to initialize (takes ~30 seconds)..."
while true; do
  STATE=$(aws batch describe-compute-environments --compute-environments NGS-Spot-Env --query 'computeEnvironments[0].state' --output text)
  if [ "$STATE" == "ENABLED" ]; then break; fi
  sleep 5
done

# --- 5. AWS BATCH JOB QUEUE ---
echo "🚦 Creating Job Queue ($QUEUE_NAME)..."
cat <<EOF > job_queue.json
{
  "jobQueueName": "$QUEUE_NAME",
  "state": "ENABLED",
  "priority": 1,
  "computeEnvironmentOrder": [
    {
      "order": 1,
      "computeEnvironment": "NGS-Spot-Env"
    }
  ]
}
EOF

aws batch create-job-queue --cli-input-json file://job_queue.json > /dev/null

# Clean up temp files
rm ec2-trust.json lifecycle.json compute_env.json job_queue.json

echo "========================================================"
echo "🎉 AWS Batch Infrastructure Successfully Provisioned!"
echo "Nextflow Profile Config:"
echo "process.queue = '$QUEUE_NAME'"
echo "workDir = 's3://$BUCKET_NAME/work'"
echo "========================================================"