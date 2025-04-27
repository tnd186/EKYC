from django.urls import path
from .views import challenge_response, ocr_vic, face_verification, save_view_result, check_id_exists

urlpatterns = [
    path('challenge_response/', challenge_response, name='challenge_response'),
    path('ocr_vic/', ocr_vic, name='ocr_vic'),
    path('face_verification/', face_verification, name='face_verification'),
    path('save_view_result/', save_view_result, name='save_view_result'),
    path('check_id_exists/', check_id_exists, name='check_id_exists'),  
]