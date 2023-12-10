from django.urls import path
from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.views import TokenRefreshView
from photo_app.views import UserViewSet, CustomizedTokenObtainPairView, LogoutView


user_register = UserViewSet.as_view({"post": "register"}, permission_classes=[AllowAny])
uploadimg = UserViewSet.as_view({"post": "uploadimg"}, permission_classes=[AllowAny])

addphoto = UserViewSet.as_view({"post": "addphoto"})
deletephoto = UserViewSet.as_view({"post": "deletephoto"})
fetchphoto = UserViewSet.as_view({"get": "fetchphoto"}, permission_classes=[AllowAny])

uservote = UserViewSet.as_view({"post": "uservote"})

createcompitition = UserViewSet.as_view({"post": "createcompitition"}, permission_classes=[AllowAny])
viewcompitition = UserViewSet.as_view({"get": "viewcompitition"}, permission_classes=[AllowAny])
viewallsubmissions = UserViewSet.as_view({"get": "viewallsubmissions"}, permission_classes=[AllowAny])
changecompititionstate = UserViewSet.as_view({"post": "changecompititionstate"}, permission_classes=[AllowAny])

urlpatterns = [
    path("auth/login/", CustomizedTokenObtainPairView.as_view(), name="user_login"),
    path("auth/register/", user_register, name="user_register"),

    #user photo crud
    path("user/addphoto/", addphoto, name="addphoto"),
    path("user/deletephoto/", deletephoto, name="deletephoto"),
    
    path("user/uploadimg/", uploadimg, name="uploadimg"),

    #user voting
    path("user/vote/", uservote, name="uservote"),

    #admin
    path("admin/createcompitition/", createcompitition, name="createcompitition"),
    path("admin/viewcompitition/", viewcompitition, name="viewcompitition"),
    path("admin/changecompititionstate/", changecompititionstate, name="changecompititionstate"),
    path("admin/viewallsubmissions/", viewallsubmissions, name="viewallsubmissions"),

    path("admin/fetchphoto/", fetchphoto, name="fetchphoto"),
]

