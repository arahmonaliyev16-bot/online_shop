from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import User, VIA_EMAIL, VIA_PHONE, CODE_VERIFIED, DONE, PHOTO_DONE
from shared.utility import email_or_phone
from shared.utility import send_email


# auth_validate --> phone_number or email
# create  ---> send_mail or sendPhone
# validate_email_phone_number= --> email or phone_number exists


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    auth_type = serializers.CharField(read_only=True, required=False)
    auth_status = serializers.CharField(read_only=True, required=False)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'auth_type',
            'auth_status',
        ]

    def create(self, validated_data):
        user = super(SignUpSerializer, self).create(validated_data)
        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(VIA_EMAIL)
            # send_email(users.email, code)
            print(code)
        elif user.auth_type == VIA_PHONE:
            code = user.generate_code(VIA_PHONE)
            # send_email(users.email, code)
            print(code)
        else:
            data = {
                'success': 'False',
                'message': 'Telefon raqam yoki email kiriting'
            }
            raise ValidationError(data)
        user.save()
        return user

    # def create(self, validated_data):
    #     validated_data.pop('email_phone_number', None)
    #
    #     users = User.objects.create_user(username='temp', **validated_data)
    #
    #     if users.auth_type == VIA_EMAIL:
    #         code = users.generate_code(VIA_EMAIL)
    #         # send_email(users.email, code)
    #         print(code)
    #
    #     elif users.auth_type == VIA_PHONE:
    #         code = users.generate_code(VIA_PHONE)
    #         # send_phone_number_sms(users.phone_number, code)
    #         print(code)
    #
    #     return users

    def validate(self, data):
        data = self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email_phone_number'))
        user_input_type = email_or_phone(user_input)
        print(user_input_type)
        if user_input_type == 'email':
            data = {
                'email' : user_input,
                'auth_type': VIA_EMAIL
            }
        elif user_input_type == 'phone':
            data = {
                'phone_number' : user_input,
                'auth_type' : VIA_PHONE
            }
        else:
            data = {
                'success': 'False',
                'message': 'Telefon raqam yoki email kiriting'
            }
            raise ValidationError(data)
        return data

    def validate_email_phone_number(self, value):
        value=value.lower()
        if value and User.objects.filter(email=value).exists():
            raise ValidationError('Bu email allaqachon mavjud')
        elif value and User.objects.filter(phone_number=value).exists():
            raise ValidationError('Bu telefon raqam allaqachon mavjud')
        return value


    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())
        return data


class UserChangeInfoSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    confirm_password = serializers.CharField(required=False)


    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('password', None)
        if password and confirm_password and password != confirm_password:
            data = {
                'success': False,
                'message': 'parollar mos emas'
            }
            raise ValidationError(data)

        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data


    def validate_username(self, username):
        user = User.objects.filter(username=username).exists()
        if user:
            raise ValidationError('Username allaqachon mavjud')
        if username.isdigit() or len(username) < 5:
            data = {
                'success': False,
                'message': 'username talabga mos kelmaydi'
            }
            raise ValidationError(data)
        return username

    def validate_first_name(self, first_name):
        if len(first_name) < 5:
            raise serializers.ValidationError(
                "Username kamida 5 ta belgidan iborat bo‘lishi kerak"
            )
        return first_name

    def validate_last_name(self, last_name):
        if len(last_name) < 5:
            raise serializers.ValidationError(
                "Username kamida 5 ta belgidan iborat bo‘lishi kerak"
            )
        return last_name


    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)
        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return  instance



class UserPhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()

    def update(self, instance, validated_data):
        photo = validated_data.get('photo')
        if photo:
            instance.photo = photo
        if instance.auth_status == DONE:
            instance.auth_status = PHOTO_DONE
        instance.save()
        return instance


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)