from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['role'] = self.user.role
        data['email'] = self.user.email
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)
    role = serializers.ChoiceField(
        choices=[('VENDOR', 'Vendor'), ('COSTUMER', 'Costumer')]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password']


    def validate_role(self, value):
        if value == 'ADMIN':
            raise serializers.ValidationError('Admin registration is not allowed.')
        return value
    

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        user.role = role
        print(user)
        user.save()
        return user
    
    

# class LoginSerializer(serializers.ModelSerializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)


#     def validate(self, data):
#         user = authenticate(**data)
#         if not user:
#             raise serializers.ValidationError('Invalid Credentials')
#         return user
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role',
            'is_active',
            'date_joined',
        ]
        