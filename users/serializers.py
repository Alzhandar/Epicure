from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from cities.serializers import CitySerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'last_name', 'city', 'email', 
                  'is_active', 'language', 'created_at']
        read_only_fields = ['created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'last_name', 'full_name', 'city', 
                 'image', 'email', 'is_active', 'language', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['phone_number', 'name', 'last_name', 'city', 'email', 'password', 
                  'password_confirm', 'language']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'last_name', 'city', 'email', 'image', 'language']


class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают"})
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'name', 'last_name', 'full_name', 'city', 
                 'image', 'email', 'language', 'is_active', 'is_staff', 'is_superuser']