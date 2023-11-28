from rest_framework.serializers import ModelSerializer
from apiapp.models import User


class UserSerializer(ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.pop("username"),
            fname=validated_data.pop("fname"),
            lname=validated_data.pop("lname"),
            **validated_data,
        )
        return user

    class Meta:
        model = User
        fields = ["email", "username", "fname", "lname", "password"]
        extra_kwargs = {"password": {"write_only": True}}
