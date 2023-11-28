from django.urls import path
from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.views import TokenRefreshView
from apiapp.views import UserViewSet, CustomizedTokenObtainPairView, LogoutView


user_register = UserViewSet.as_view({"post": "register"}, permission_classes=[AllowAny])
user_myprofile = UserViewSet.as_view({"get": "myprofile"})

product = UserViewSet.as_view({"get": "allproduct"}, permission_classes=[AllowAny])
category = UserViewSet.as_view({"get": "allcategory"}, permission_classes=[AllowAny])
submitform = UserViewSet.as_view({"post": "submitform"}, permission_classes=[AllowAny])
addcategory = UserViewSet.as_view({"post": "addcategory"}, permission_classes=[AllowAny])
addproduct = UserViewSet.as_view({"post": "addproduct"}, permission_classes=[AllowAny])
marktopselling = UserViewSet.as_view({"post": "marktopselling"}, permission_classes=[AllowAny])
completeorder = UserViewSet.as_view({"post": "completeorder"})
viewallorders = UserViewSet.as_view({"get": "viewallorders"}, permission_classes=[AllowAny])
uploadimg = UserViewSet.as_view({"post": "uploadimg"}, permission_classes=[AllowAny])
editproduct = UserViewSet.as_view({"post": "editproduct"}, permission_classes=[AllowAny])


urlpatterns = [


    path("auth/login/", CustomizedTokenObtainPairView.as_view(), name="user_login"),
    path("auth/register/", user_register, name="user_register"),
    path("users/myprofile/", user_myprofile, name="user_myprofile"),

    path("product/", product, name="product"),
    path("category/", category, name="category"),
    path("admin/viewallorders", viewallorders, name="viewallorders"),


    path("submitform/", submitform, name="submitform"),
    path("addcategory/", addcategory, name="addcategory"),
    path("addproduct/", addproduct, name="addproduct"),

    path("editproduct/", editproduct, name="editproduct"),

    path("marktopselling/", marktopselling, name="marktopselling"),

    path("users/completeorder", completeorder, name="completeorder"),

    path("uploadimg/", uploadimg, name="uploadimg"),
    
    
]
