import boto3
from config import S3_BUCKET, S3_KEY, S3_SECRET
from flask import session

def _get_s3_resource():
    if S3_KEY and S3_SECRET:
        return boto3.resource(
            's3',
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
    else:
        return boto3.resource('s3')


def get_bucket():
    s3_resource = _get_s3_resource()
    if 'bucket' in session:
        bucket = session['bucket']
    else:
        bucket = S3_BUCKET

    return s3_resource.Bucket(bucket)


def get_buckets_list():
    client = boto3.client('s3')
    return client.list_buckets().get('Buckets')

def get_url(s3_file):
    client = boto3.client('s3')
    return client.generate_presigned_url("get_object",
                                         Params={"Bucket":s3_file.bucket_name,
                                                 "Key": s3_file.key})
def get_queue_elem():
    sqs = boto3.resource("sqs")
    client = boto3.client("sqs")
    queuename = "test"

    try:
        queue = sqs.get_queue_by_name(QueueName=queuename)
    except client.exceptions.QueueDoesNotExist as e:
        print("queue does not exist. Creating")
        queue = sqs.create_queue(QueueName=queuename, Attributes={"DelaySeconds": "5"})
    # print(queue.url)

    # queue.send_message(MessageBody=body)
    # print "pushed'", body, "'to queue:", queuename
    # queue.send_message(MessageBody="hello2")


    msgs = queue.receive_messages()
    try:
        return msgs[0]
    except:
        return None
    
        # 
    # return msg
    # while len(msgs) > 0:
        # print(msg.body)
        # msg.delete()
        # msgs = queue.receive_messages()
