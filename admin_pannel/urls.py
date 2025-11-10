from django.urls import path
from . import views

urlpatterns =[

    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'), 
    path('Index/' , views.Index, name='Index'), 
    path('diwali_kirana/', views.diwali_kirana_list, name='diwali_kirana_list'),

    path('diwali_kirana/bulk_update/', views.proxy_bulk_update_view, name='proxy_bulk_update'),
    path('diwali_kirana/add_member/', views.proxy_add_member_view, name='proxy_add_member'),

    path('diwali_kirana/upload_voter_id/', views.proxy_upload_voter_id_view, name='proxy_upload_voter_id'),

    path('diwali_kirana/delete/<int:reg_id>/', views.proxy_delete_member_view, name='proxy_delete_member'),

]