import boto3
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_idle_instances(ec2_client, cloudwatch_client, cpu_threshold=5.0, days=7):
    """
    Identify EC2 instances with average CPU utilization below the threshold
    over the past N days — a strong signal that the instance is idle.
    """
    idle_instances = []

    response = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days)

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]

            metrics = cloudwatch_client.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=["Average"]
            )

            if metrics["Datapoints"]:
                avg_cpu = sum(d["Average"] for d in metrics["Datapoints"]) / len(metrics["Datapoints"])
                if avg_cpu < cpu_threshold:
                    idle_instances.append({
                        "InstanceId": instance_id,
                        "AvgCPU": round(avg_cpu, 2),
                        "InstanceType": instance["InstanceType"],
                        "LaunchTime": str(instance["LaunchTime"])
                    })
                    logger.info(f"Idle instance found: {instance_id} | Avg CPU: {avg_cpu:.2f}%")

    return idle_instances


def lambda_handler(event, context):
    ec2_client = boto3.client("ec2")
    cloudwatch_client = boto3.client("cloudwatch")
    sns_client = boto3.client("sns")

    SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:FinOps-Alerts"

    idle = get_idle_instances(ec2_client, cloudwatch_client)

    if not idle:
        return {"statusCode": 200, "body": "No idle instances found."}

    message = f"FinOps Alert: {len(idle)} idle EC2 instance(s) detected (avg CPU < 5% over 7 days):\n\n"
    for inst in idle:
        message += f"- {inst['InstanceId']} ({inst['InstanceType']}) | Avg CPU: {inst['AvgCPU']}%\n"
    message += "\nReview and consider stopping or rightsizing these instances to reduce costs."

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject="AWS FinOps: Idle EC2 Instances Detected",
        Message=message
    )

    return {"statusCode": 200, "body": f"Reported {len(idle)} idle instances via SNS."}
