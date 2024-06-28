from django.urls import path
from StyleAndBeautyApp.views import *

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('registration/', RegistrationView.as_view(), name='registration'),

    path('profile/client', ClientProfileView.as_view(), name='client_profile'),
    path('profile/client/services', ClientServicesView.as_view(), name='client_services'),
    path('profile/client/masters', ClientMastersView.as_view(), name='client_masters'),
    path('profile/client/sign_record/', SignRecordView.as_view(), name='SignRecord'),
    path('profile/client/sign_record/<int:service_id>/', SignRecordView.as_view(), name='SignRecord'),

    path('profile/master', MasterProfileView.as_view(), name='master_profile'),

    path('profile/manager', ManagerProfileView.as_view(), name='manager_profile'),
    path('download-statistics/', download_statistics, name='download_statistics'),
]
