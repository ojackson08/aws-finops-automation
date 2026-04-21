import boto3
import logging
from datetime import datetime, timezone

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_unattached_volumes(ec2_client):
    """
    Retrieve a list of all unattached EBS volumes in the region.
    """
    unattached_volumes = []
    try:
        # Describe volumes with the 'available' status
        response = ec2_client.describe_volumes(
            Filters=[
                {
                    'Name': 'status',
                    'Values': ['available']
                }
            ]
        )
        
        for volume in response['Volumes']:
            unattached_volumes.append({
                'VolumeId': volume['VolumeId'],
                'Size': volume['Size'],
                'VolumeType': volume['VolumeType'],
                'CreateTime': volume['CreateTime']
            })
            
        return unattached_volumes
    except Exception as e:
        logger.error(f"Error retrieving volumes: {str(e)}")
        raise

def send_sns_notification(sns_client, topic_arn, volumes):
    """
    Send an SNS notification with the list of volumes to be deleted.
    """
    if not volumes:
        return
        
    message = "The following unattached EBS volumes have been identified for cleanup:\n\n"
    for vol in volumes:
        message += f"- Volume ID: {vol['VolumeId']}, Size: {vol['Size']} GB, Created: {vol['CreateTime']}\n"
        
    message += "\nThese volumes will be deleted to optimize AWS costs."
    
    try:
        sns_client.publish(
            TopicArn=topic_arn,
            Subject="AWS FinOps: Unattached EBS Volumes Cleanup",
            Message=message
        )
        logger.info("SNS notification sent successfully.")
    except Exception as e:
        logger.error(f"Error sending SNS notification: {str(e)}")

def lambda_handler(event, context):
    """
    Main Lambda handler function.
    """
    logger.info("Starting EBS volume cleanup process...")
    
    # Initialize boto3 clients
    ec2_client = boto3.client('ec2')
    sns_client = boto3.client('sns')
    
    # NOTE: In a real environment, this should be an environment variable
    SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:123456789012:FinOps-Alerts"
    
    try:
        # Step 1: Identify unattached volumes
        unattached_volumes = get_unattached_volumes(ec2_client)
        
        if not unattached_volumes:
            logger.info("No unattached volumes found. Cost optimization complete.")
            return {
                'statusCode': 200,
                'body': 'No unattached volumes found.'
            }
            
        logger.info(f"Found {len(unattached_volumes)} unattached volumes.")
        
        # Step 2: Send notification before deletion (Safety measure)
        send_sns_notification(sns_client, SNS_TOPIC_ARN, unattached_volumes)
        
        # Step 3: Delete the volumes
        deleted_count = 0
        for vol in unattached_volumes:
            vol_id = vol['VolumeId']
            logger.info(f"Deleting volume: {vol_id}")
            # Uncomment the following line to actually delete the volumes
            # ec2_client.delete_volume(VolumeId=vol_id)
            deleted_count += 1
            
        logger.info(f"Successfully processed {deleted_count} volumes.")
        
        return {
            'statusCode': 200,
            'body': f"Successfully processed {deleted_count} unattached volumes."
        }
        
    except Exception as e:
        logger.error(f"Lambda execution failed: {str(e)}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }
