# AWS Cost Optimization & FinOps Automation

## Project Overview
This project demonstrates the ability to apply FinOps principles by automating the identification and remediation of wasted cloud spend. Specifically, it uses AWS Lambda and Python (Boto3) to find and delete unattached Elastic Block Store (EBS) volumes.

It solves the business problem of "cloud sprawl," where orphaned resources continue to incur monthly charges long after the associated compute instances have been terminated.

## Architecture Details
1.  **Event Trigger:** Amazon EventBridge triggers the Lambda function on a scheduled basis (e.g., weekly).
2.  **Compute Logic:** An AWS Lambda function executes a Python script using the Boto3 SDK.
3.  **Resource Identification:** The script queries the EC2 API to find all EBS volumes with a status of `available` (unattached).
4.  **Notification:** Before taking destructive action, the script publishes a message to an Amazon SNS topic, alerting administrators of the impending cleanup.
5.  **Remediation:** The script deletes the orphaned volumes, immediately stopping the associated billing charges.

## Business Impact
By automating this FinOps process, organizations can reduce their monthly AWS storage costs by up to 20% (depending on the scale of orphaned resources). It shifts the burden of cost optimization from manual audits to automated, continuous compliance.
