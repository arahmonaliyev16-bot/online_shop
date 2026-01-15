from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from django.core.serializers import serialize
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, NEW, CODE_VERIFIED, VIA_PHONE, VIA_EMAIL, DONE, PHOTO_DONE
from .serializers import SignUpSerializer, UserChangeInfoSerializer, UserPhotoSerializer, VerifyCodeSerializer
from rest_framework import permissions
from rest_framework import status


class SignUpView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny, )



class VerifyCode(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify_code(user, code)
        data = {
            'success': True,
            'auth_status': user.auth_status,
            'access_token': user.token()['access'],
            'refresh': user.token()['refresh_token']
        }
        return Response(data)

    @swagger_auto_schema(request_body=VerifyCodeSerializer)
    def post(self, request, *args, **kwargs):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        code = serializer.validated_data['code']

        self.check_verify_code(user, code)

        data = {
            'success': True,
            'auth_status': user.auth_status,
            'access_token': user.token()['access'],
            'refresh': user.token()['refresh_token']
        }
        return Response(data)


    @staticmethod
    def check_verify_code(user, code):
        verify = user.verify_codes.filter(code=code, confirmed=False, expiration_time__gte=datetime.now())
        if not verify.exists():
            data = {
                'success': False,
                'message': 'Kod eskirgan yoki xato',
            }
            raise ValidationError(data)
        else:
            verify.update(confirmed=True)

        if user.auth_status == NEW:
            user.auth_status = CODE_VERIFIED
            user.save()

        return True


class NewVerifyCode(APIView):
    permissions_class = (permissions.IsAuthenticated,)


    def get(self, request):
        user = request.user
        self.check_code(user)
        if user.auth_type == VIA_EMAIL:
            code = user.generate_code(VIA_EMAIL)
            # send_email(users.email, code)
            print(code)
        elif user.auth_type == VIA_PHONE:
            code = user.generate_code(VIA_PHONE)
            # send_email(users.email, code)
            print(code)

        data = {
            'success': True,
            'message': 'Code yuborildi'
        }
        return Response(data)


    @staticmethod
    def check_code(user):
        verify = user.verify_codes.filter(confirmed=False, expiration_time__gte=datetime.now())
        if verify.exists():
            data = {
                'success': False,
                'message': 'Sizda active code bor',
            }
            raise ValidationError(data)
        if user.auth_status in (CODE_VERIFIED, DONE, PHOTO_DONE):
            data = {
                'success': False,
                'message': 'Sizda code tasdiqlangan',
            }
            raise ValidationError(data)

        return True


class UserChangeView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserChangeInfoSerializer


    def get_object(self):
        return self.request.user     #token orqali idni aniqlash

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'malumotlaringiz yangilandi'
        }
        return Response(data)

    def partial_update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        data = {
            'success': True,
            'message': 'malumotlaringiz qisman yangilandi'
        }
        return Response(data)



class UserPhotoView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request):
        user = self.request.user
        serializer = UserPhotoSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(user, serializer.validated_data)

        data = {
            'status': status.HTTP_200_OK,
            'message': 'rasm ozgartirildi'
        }
        return Response(data)



