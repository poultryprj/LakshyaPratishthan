from django.urls import path
from . import views

urlpatterns = [
    path('agent-login/', views.agent_login_api, name='agent_login_api'),
    path('get-registration-list/', views.get_registration_list, name='get_registration_list'),
    path('get-area-list/', views.get_area_list, name='get_area_list'),

    path('get-grid-data/', views.get_grid_data, name='get_grid_data'),
    path('update-grid-cell/', views.update_grid_cell, name='update_grid_cell'),

    path('get-excel-data/', views.get_excel_data, name='get_excel_data'),
    path('save-excel-data/', views.save_excel_data, name='save_excel_data'),

    path('get-telecalling-data/', views.get_telecalling_data, name='get_telecalling_data'),
    path('update-call-status/', views.update_call_status, name='update_call_status'),

    path('get-telecalling-report/', views.get_telecalling_report, name='get_telecalling_report'),

    path('get-voter-calling-data/', views.get_voter_calling_data, name='get_voter_calling_data'),
    path('update-voting-status/', views.update_voting_status, name='update_voting_status'),
]