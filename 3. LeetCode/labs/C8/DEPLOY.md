# Deploying the summarizer Lambda

## Prerequisites
- AWS account on the free tier, an IAM user with admin rights for this exercise, `aws configure` done.
- `sam --version` works (AWS SAM CLI).
- Your Anthropic API key, kept out of the repo.

## Steps
1. `sam build` from this folder.
2. `sam deploy --guided`. Stack name `gecko-summarizer`, region of your choice, accept the defaults, and when it asks for `AnthropicApiKey`, paste the key. It's stored as a Lambda environment variable; for a real system you'd use Secrets Manager.
3. Note the bucket name from the stack outputs: _(you)_
4. `aws s3 cp ../C6/data/standup.txt s3://<bucket>/incoming/standup.txt`
5. Wait ten seconds, then `aws s3 ls s3://<bucket>/incoming/`. You should see `standup.txt.summary.json`.
6. `aws s3 cp s3://<bucket>/incoming/standup.txt.summary.json -` to print it.
7. `aws logs tail /aws/lambda/<function name> --since 10m` to read the logs.
8. Tear down: empty the bucket (`aws s3 rm s3://<bucket> --recursive`) then `sam delete`.

## What it cost
_(you)_

## What confused me
_(you)_
