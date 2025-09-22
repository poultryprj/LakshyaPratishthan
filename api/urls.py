from django.urls import path
from . import views

urlpatterns = [

    # path('AgentLogin', views.AgentLogin, name='AgentLogin'),
    # path('logout/', views.logout, name='logout'),
    # path('dashboard/' , views.dashboard, name='dashboard'),/


    path("fi_insert_area/",views.fi_insert_area, name="fi_insert_area"),
    path("fi_list_area/", views.fi_list_area, name="fi_list_area"),
    path("fi_list_areaAll/", views.fi_list_areaAll, name="fi_list_areaAll"),
    path("fi_modify_area/", views.fi_modify_area, name="fi_modify_area"),
    path("fi_delete_area/", views.fi_delete_area, name="fi_delete_area"),

    path("fi_list_gender/", views.fi_list_gender, name="fi_list_gender"),
    path("fi_list_bloodgroup/", views.fi_list_bloodgroup, name="fi_list_bloodgroup"),

    path("fi_insert_user/", views.fi_insert_user, name="fi_insert_user"),
    path("fi_modify_user/", views.fi_modify_user, name="fi_modify_user"),
    path("fi_delete_user/", views.fi_delete_user, name="fi_delete_user"),
    path("fi_list_userAll/", views.fi_list_userAll, name="fi_list_userAll"),


    path("fi_agent_login/", views.fi_agent_login, name="fi_agent_login"),
    path("fi_search_registration/", views.fi_search_registration, name="fi_search_registration"),
    path("fi_list_yatra_status/", views.fi_list_yatra_status, name="fi_list_yatra_status"),

    path("fi_pilgrims_registration/", views.fi_pilgrims_registration, name="fi_pilgrims_registration"),
    path("fi_pilgrim_card/", views.fi_pilgrim_card, name="fi_pilgrim_card"),

    path("fi_insert_ticket/", views.fi_insert_ticket, name="fi_insert_ticket"),
    path("fi_cancel_ticket/", views.fi_cancel_ticket, name="fi_cancel_ticket"),
    path("fi_remove_ticket/", views.fi_remove_ticket, name="fi_remove_ticket"),

    path("fi_totals/", views.fi_totals, name="fi_totals"),
    path("fi_total_routeyatrabus/", views.fi_total_routeyatrabus, name="fi_total_routeyatrabus"),

    path("fi_routeyatrabus_tickets/", views.fi_routeyatrabus_tickets, name="fi_routeyatrabus_tickets"),
    path("fi_agent_bookings/", views.fi_agent_bookings, name="fi_agent_bookings"),
   
]