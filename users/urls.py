from django.urls import path
from .views import SignUpView, VerifyCode, NewVerifyCode, UserChangeView, UserPhotoView

urlpatterns = [
    path('signup/', SignUpView.as_view()),
    path('code_verify/',VerifyCode.as_view()),
    path('new_code_verify/',NewVerifyCode.as_view()),
    path('user_change_info/',UserChangeView.as_view()),
    path('user_change_photo/',UserPhotoView.as_view()),

]

