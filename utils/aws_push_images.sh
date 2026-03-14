# 1. Get your AWS Account ID and define the region
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

# 2. Authenticate your local Docker daemon to AWS ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

# 3. Create the repositories in AWS
aws ecr create-repository --repository-name ngs-alignment > /dev/null 2>&1 || true
aws ecr create-repository --repository-name ngs-python-runner > /dev/null 2>&1 || true

# 4. Tag your local images with the AWS ECR URI
docker tag ngs-alignment:latest $ECR_URI/ngs-alignment:latest
docker tag ngs-python-runner:latest $ECR_URI/ngs-python-runner:latest

# 5. Push the images to the cloud! (This may take a minute or two depending on your upload speed)
docker push $ECR_URI/ngs-alignment:latest
docker push $ECR_URI/ngs-python-runner:latest

echo "✅ Images successfully pushed to: $ECR_URI"