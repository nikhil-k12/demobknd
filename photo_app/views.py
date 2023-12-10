from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from photo_app.serializers import UserSerializer
from photo_app.models import User
from .models import User
import secrets
import string
from django.contrib.auth.hashers import make_password
import base64

# from helperlibrary.helper_module import Helper
import json
import time
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
import boto3

ACCESS_KEY = "AKIA4YY3D4A4WJRDC4OA"
SECRET_KEY = "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"
REGION = "ap-south-1"
CONFIGURED_PUBLIC_BUCKET='testbkth101'

class Helper:
        def __init__(self,ACCESS_KEY, SECRET_KEY, REGION):
            self.ACCESS_KEY = ACCESS_KEY
            self.SECRET_KEY = SECRET_KEY
            self.REGION = REGION
            self.S3  = boto3.client('s3', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
            self.DYN = boto3.client('dynamodb', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
            self.dynamoresource  = boto3.resource('dynamodb', region_name=REGION, aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

        def newrecordinDatabase(self, table_name, primary_key_value, attributes):
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



      


helper_instance = Helper(ACCESS_KEY,SECRET_KEY,REGION)
      

def intializeTables():
    tbl_list = ['TBLphotos','TBLcompititions','TBLvotes']
    print("Initialization of tables")
    for tbl in tbl_list:
        print(tbl)
        helper_instance.create_table(tbl)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    intializeTables()

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def register(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"success":False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=False, methods=["post"])
    def addphoto(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        id = serializer.data['username']
        imgurl = request.data.get('imgurl')
        desc = request.data.get('desc')
        compid = request.data.get('compid')
        attr = {'imgurl':imgurl,'desc':desc,'compid':compid,'submittedby':id}
        helper_instance.update_many_fields('TBLphotos',id+'|'+compid,attr)
        return Response({'success':True}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["post"])
    def deletephoto(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        id = serializer.data['username']
        compid = request.data.get('compid')
        helper_instance.delete_record('TBLphotos',id+'|'+compid)
        return Response({'success':True}, status=status.HTTP_202_ACCEPTED)
    

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def fetchphoto(self, request, *args, **kwargs):
        res= helper_instance.fetch_all_records('TBLphotos')
        return Response({'result':res}, status=status.HTTP_202_ACCEPTED)

    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def uploadimg(self, request, *args, **kwargs):
        b64 = request.data.get('b64')
        ext = request.data.get('ext')
        res= helper_instance.upload_s3(b64,ext,CONFIGURED_PUBLIC_BUCKET,str(int(time.time())))
        return Response({'success':res}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"])
    def uservote(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        id = serializer.data['username']
        compid = request.data.get('compid')
        votedfor = request.data.get('votedfor')
        attr = {'votedfor':votedfor,'compid':compid,'submittedby':id}
        helper_instance.update_many_fields('TBLvotes',id+'|'+compid,attr)
        return Response({'success':True}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def viewallsubmissions(self, request, *args, **kwargs):
        res = helper_instance.fetch_all_records('TBLvotes')
        return Response({'result':res}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def createcompitition(self, request, *args, **kwargs):
        compname = request.data.get('compname')
        desc = request.data.get('desc')
        attr = {'compname':compname,'desc':desc,'isactive':True}
        helper_instance.update_many_fields('TBLcompititions',str(int(time.time())),attr)
        return Response({'success':True}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def changecompititionstate(self, request, *args, **kwargs):
        compid = request.data.get('compid')
        newstate = request.data.get('newstate')
        attr = {'isactive':newstate}
        helper_instance.update_many_fields('TBLcompititions',compid,attr)
        return Response({'success':True}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def viewcompitition(self, request, *args, **kwargs):
        res = helper_instance.fetch_all_records('TBLcompititions')
        return Response({'result':res}, status=status.HTTP_202_ACCEPTED)



def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

class CustomizedTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user_serializer = UserSerializer(instance=serializer.user)
        print(user_serializer.data)
        serializer.validated_data.update(user_serializer.data)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            print(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            raise e
            
