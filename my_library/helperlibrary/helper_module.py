from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
import boto3
import base64

class Helper:
    def __init__(self,ACCESS_KEY, SECRET_KEY, REGION):
        self.ACCESS_KEY = ACCESS_KEY
        self.SECRET_KEY = SECRET_KEY
        self.REGION = REGION
        self.S3  = boto3.client('s3', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        self.DYN = boto3.client('dynamodb', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        self.dynamoresource  = boto3.resource('dynamodb', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        self.SES  = boto3.client('ses', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
        self.SQS  = boto3.client('sqs', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
 

    def add_new_entry(self, table_name, primary_key_value, attributes):
        table = self.dynamoresource.Table(table_name)

        try:
            item = {'id': primary_key_value}
            item.update(attributes)

            response = table.put_item(Item=item)
            print(f'New entry added successfully with primary key {primary_key_value}.')
            return True
        except Exception as e:
            print(f'Error adding new entry: {e}')
            return False

    def create_table(self, table_name ):
        key_schema = [
            {'AttributeName': 'id', 'KeyType': 'HASH'},

        ]
        attribute_definitions = [
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ]
        provisioned_throughput = {
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }

        try:
            self.dynamoresource.Table(table_name).table_status
            print(f'Table {table_name} already exists.')
        except self.dynamoresource.meta.client.exceptions.ResourceNotFoundException:

            try:
                table = self.dynamoresource.create_table(
                    TableName=table_name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attribute_definitions,
                    ProvisionedThroughput=provisioned_throughput
                )
                table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
                print(f'Table {table_name} created successfully.')
            except ClientError as e:
                print(f'Error creating table: {e}')


    def fetch_all_records(self, table_name ):

        table = self.dynamoresource.Table(table_name)
        try:
            response = table.scan()
            items = response.get('Items', [])
            return items
        except Exception as e:
            print(f'Error fetching records: {e}')
            return []


    def fetch_records_by_field(self, table_name, field_name, field_value):
        table = self.dynamoresource.Table(table_name)
        try:
            response = table.scan(
                FilterExpression=Attr(field_name).eq(field_value)
            )
            items = response.get('Items', [])
            return items
        except Exception as e:
            print(f'Error fetching records by field: {e}')
            return []


    def delete_record(self, table_name, primary_key_value ):
        table = self.dynamoresource.Table(table_name)
        try:
            response = table.delete_item(
                Key={'id': primary_key_value}
            )
            print(f'Record with primary key {primary_key_value} deleted successfully.')
        except Exception as e:
            print(f'Error deleting record: {e}')    


    def update_record(self, table_name, primary_key_value, update_attribute, new_value):
        table = self.dynamoresource.Table(table_name)
        try:
            response = table.update_item(
                Key={'id': primary_key_value},
                UpdateExpression='SET #ts = :val1',
                ExpressionAttributeValues={
                    ":val1": new_value
                },
                ExpressionAttributeNames={
                    "#ts": update_attribute
                },
                ReturnValues='UPDATED_NEW'
            )
            print(f'Record with primary key {primary_key_value} updated successfully.')
        except Exception as e:
            print(f'Error updating record: {e}')


    def update_many_fields(self, table_name, primary_key_value, update_attributes):
        table = self.dynamoresource.Table(table_name)
        try:
            update_expression = 'SET '
            expression_attribute_values = {}
            expression_attribute_names = {}

            for key, value in update_attributes.items():
                update_expression += f'#{key} = :{key}, '
                expression_attribute_values[f':{key}'] = value
                expression_attribute_names[f'#{key}'] = key

            update_expression = update_expression[:-2]  # Remove the trailing comma and space

            response = table.update_item(
                Key={'id': primary_key_value},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ExpressionAttributeNames=expression_attribute_names,
                ReturnValues='UPDATED_NEW'
            )

            print(f'Record with primary key {primary_key_value} updated successfully.')
        except Exception as e:
            print(f'Error updating record: {e}')


    def sqs_create_queue(self,queue_name):
            
            try:
                response = self.SQS.get_queue_url(QueueName=queue_name)
                queue_url = response['QueueUrl']
                print(f"Queue '{queue_name}' already exists with URL: {queue_url}")
                return queue_url
            except self.SQS.exceptions.QueueDoesNotExist:
                pass  


            response = self.SQS.create_queue(QueueName=queue_name)
            queue_url = response['QueueUrl']
            print(f"Queue '{queue_name}' created with URL: {queue_url}")
            return queue_url


    def sqs_send_message_to_queue(self,queue_url, message_body):
        response = self.SQS.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body
        )

        print(f"Message sent to queue '{queue_url}' with MessageId: {response['MessageId']}")



    def upload_s3(self,base64_string,extension,bktname,key):
        try:
            binary_data = base64.b64decode(base64_string)
            filekey = key+'.'+extension
            self.S3.put_object(Body=binary_data, Bucket=bktname, Key=filekey)
            file_url = f"https://{bktname}.s3.{self.REGION}.amazonaws.com/{filekey}"
            return file_url
        except ClientError as e:
            print(e)
            return ""