from importlib.metadata import requires
from wsgiref.validate import validator

from pyasn1.type.useful import ObjectDescriptor
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', "email", 'password', 'password_confirm'
            'first_name', 'last_name'
        )


    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Password fields didnt match.'}
            )
        return attrs


    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validator(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            if user is None:
                raise serializers.ValidationError(
                    "user not found"
                )
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled'
                )
            attrs['user'] = User
            return attrs

        else:
            raise serializers.ValidationError(
                'mast include "email" and "password".'
            )


class  UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyFIeld()
    posts_count = serializers.SerializerMetodField()
    comments_count = serializers.SerializerMetodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'avatar', 'bio', 'created_ap', 'updated_ap',
            'posts_count', 'comments_count'
        )
        read_only_fields =('id', 'created_ap', 'updated_ap')


    def get_posts_count(self, obj):
        return obj.posts.count()

    def get_comments_count(self, obj):
        return obj.comments.count()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'avatar', 'bio'
        )

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class ChangePasswordSerializer(serializers.serializer):
    odl_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)


    def validate_old_password(self,  value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {'now_password': 'error password is incorrect'}
            )
        return value

    def validate(self, attrs):
        if attrs['mew_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'mew_password': 'Password didn match' }
            )

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user



