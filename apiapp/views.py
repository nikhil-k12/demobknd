from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from apiapp.serializers import UserSerializer
from apiapp.models import User
from .models import User
import secrets
import string
from django.contrib.auth.hashers import make_password
from helperlibrary.helper_module import Helper
import json
import time
import moment

ACCESS_KEY = "AKIA4YY3D4A42BD3MGEK"
SECRET_KEY = "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"
REGION = "ap-south-1"
CONFIGURED_EMAIL='abc@gmail.com'
CONFIGURED_PUBLIC_BUCKET='testbkth101'

Q_NAME='test_q'

helper_instance = Helper(ACCESS_KEY,SECRET_KEY,REGION)

def intializeTables():
    tbl_list = ['TBLcategory','TBLproduct','TBLorder','TBLcontactform']
    print("Checking tables, might take time for 1st run")
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

    @action(detail=False, methods=["get"])
    def myprofile(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def allcategory(self, request, *args, **kwargs):
        res = helper_instance.fetch_all_records('TBLcategory')
        return Response(res, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def allproduct(self, request, *args, **kwargs):
        res = helper_instance.fetch_all_records('TBLproduct')
        return Response(res, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def submitform(self, request, *args, **kwargs):
        name = request.data.get('name')
        email = request.data.get('email')
        message = request.data.get('message')
        attr = {'name':name,'email':email,'message':message}
        res = helper_instance.add_new_entry('TBLcontactform',str(int(time.time())),attr)
        send_email(CONFIGURED_EMAIL,CONFIGURED_EMAIL,'New Contact Form Received',attr)
        return Response({'success':res}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def addproduct(self, request, *args, **kwargs):
        categoryid = request.data.get('categoryid')
        categoryname = request.data.get('categoryname')
        name = request.data.get('name')
        desc = request.data.get('desc')
        imgurl = request.data.get('imgurl')
        price = request.data.get('price')
        attr = {'name':name,'categoryid':categoryid,'categoryname':categoryname,'desc':desc,'imgurl':imgurl,'price':price}
        res = helper_instance.add_new_entry('TBLproduct',str(int(time.time())),attr)
        return Response({'success':res}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def addcategory(self, request, *args, **kwargs):
        catname = request.data.get('catname')
        res = helper_instance.add_new_entry('TBLcategory',str(int(time.time())),{'catname':catname})
        return Response({'success':res}, status=status.HTTP_202_ACCEPTED)

    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def marktopselling(self, request, *args, **kwargs):
        productid = request.data.get('productid')
        newvalue = request.data.get('newvalue')
        helper_instance.update_record('TBLproduct',productid,'isTopSelling',newvalue)
        return Response({'success':True}, status=status.HTTP_202_ACCEPTED)
    

    @action(detail=False, methods=["post"])
    def completeorder(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        id = serializer.data['username']
        totalamount = request.data.get('totalamount')
        orderlist = request.data.get('orderlist')
        pincode = request.data.get('pincode')
        addrtype = request.data.get('addrtype')
        address = request.data.get('address')
        paymentmode = request.data.get('paymentmode')
        attr = {'orderedby':id,'totalamount':totalamount,'orderlist':orderlist,'pincode':pincode,'addrtype':addrtype,'address':address,'paymentmode':paymentmode}
        res = helper_instance.add_new_entry('TBLorder',str(int(time.time())),attr)
        return Response({'success':res}, status=status.HTTP_202_ACCEPTED)
    

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def viewallorders(self, request, *args, **kwargs):
        res = helper_instance.fetch_all_records('TBLorder')
        return Response(res, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def uploadimg(self, request, *args, **kwargs):
        b64 = request.data.get('b64')
        ext = request.data.get('ext')
        res= helper_instance.upload_s3(b64,ext,CONFIGURED_PUBLIC_BUCKET,str(int(time.time())))
        return Response({'success':res}, status=status.HTTP_202_ACCEPTED)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def editproduct(self, request, *args, **kwargs):
        attr = {'categoryid':request.data.get('categoryid'),'categoryname':request.data.get('categoryname'),'price':request.data.get('price'),'name':request.data.get('name'),'imgurl':request.data.get('imgurl'),'isTopSelling':request.data.get('isTopSelling'),'desc':request.data.get('desc')}
        res= helper_instance.update_many_fields('TBLproduct',request.data.get('id'),attr)
        return Response({'success':res}, status=status.HTTP_202_ACCEPTED)
    


def send_password_email(email, password):
    subject = 'Your Current Password'
    message = f'Your current password is: {password}'
    from_email = 'your@email.com'
    print(subject, message, from_email, [email])
    # send_mail(subject, message, from_email, [email])

def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def send_email(fromEmail,toEmail,subject,body):
    q_url = helper_instance.sqs_create_queue(Q_NAME)
    helper_instance.sqs_send_message_to_queue(q_url,str({'subject': subject, 'message': body, 'fromEmail': fromEmail,'toEmail':toEmail}))

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
            # return Response(status=status.HTTP_400_BAD_REQUEST)
