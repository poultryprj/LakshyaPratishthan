from django.urls import path
from . import views

urlpatterns = [

    path("agentlogin/", views.agentlogin, name="agentlogin"),
    path("update-pin/", views.update_pin_api, name="update_pin_api"),
    path("insertarea/",views.insertarea, name="insertarea"),
    path("listarea/", views.listarea, name="listarea"),
    path("listareaall/", views.listareaall, name="listareaall"),
    path("modifyarea/", views.modifyarea, name="modifyarea"),

    path("listgender/", views.listgender, name="listgender"),
    path("listbloodgroup/", views.listbloodgroup, name="listbloodgroup"),

    path("insertuser/", views.insertuser, name="insertuser"),
    path("modifyuser/", views.modifyuser, name="modifyuser"),
    path("deleteuser/", views.deleteuser, name="deleteuser"),
    path("listuserall/", views.listuserall, name="listuserall"),

    path("searchregistrations/", views.searchregistrations, name="searchregistrations"),
 
    path("pilgrimregistration/", views.pilgrimregistration, name="pilgrimregistration"),
    # path("update_pilgrimregistration/", views.update_pilgrimregistration, name="update_pilgrimregistration"),
    path("getpilgrimcard/", views.getpilgrimcard, name="getpilgrimcard"),

    path("CheckTicketsForReg/", views.CheckTicketsForReg, name="CheckTicketsForReg"),

    path("insertblanktickets/", views.insertblanktickets, name="insertblanktickets"),
    path("inserttickets/", views.inserttickets, name="inserttickets"),
    path("cancelticket/", views.cancelticket, name="cancelticket"),
   
    path("totals/", views.totals, name="totals"),
    path("totalrouteyatrabus/", views.totalrouteyatrabus, name="totalrouteyatrabus"),

    path("routeyatrabustickets/", views.routeyatrabustickets, name="routeyatrabustickets"),
    path("agentbookings/", views.agentbookings, name="agentbookings"),
    path("yatrabookings/", views.yatrabookings, name="yatrabookings"),


    path("routeyatradates/", views.route_yatra_dates, name="route_yatra_dates"),
    path('listroute/', views.list_routes, name='list_routes'),
    path('listrouteall/', views.list_routes_all, name='list_routes_all'),
    path('listroutebus/', views.list_buses, name='list_buses'),
    path('listyatra/', views.list_yatras, name='list_yatras'),
    path('listyatraall/', views.list_yatras_all, name='list_yatras_all'), 

    path('listyatrabuses/', views.listyatrabuses, name='listyatrabuses'), 
    path('createyatrabus/', views.createyatrabus, name='createyatrabus'), 
    path('modifyyatrabus/', views.modifyyatrabus, name='modifyyatrabus'), 
    path('deleteyatrabus/', views.deleteyatrabus, name='deleteyatrabus'),

    path("fetch_bus_seats/", views.fetch_bus_seats, name="fetch_bus_seats"),

    path('insertyatra/', views.create_yatra, name='create_yatra'),
    path('modifyyatra/', views.modify_yatra, name='modify_yatra'),

    path('insertroute/', views.create_route, name='create_route'),
    path('modifyroute/', views.modify_route, name='modify_route'),

    ########################################################################

    # path("change_ticket/", views.change_ticket, name="change_ticket"),

    # path("update_ticket_payment/", views.update_ticket_payment, name="update_ticket_payment"),

    path("list_pilgrim_tickets/", views.list_pilgrim_tickets, name="list_pilgrim_tickets"),

    path("list_available_tickets/", views.list_available_tickets, name="list_pilgrim_tickets"),


    
    ########################### LakshyaPratishthan ######################################

    path("diwaliregistration/", views.diwaliregistration, name="diwaliregistration"),
    
    path('check_rationcard/', views.check_rationcard, name='check_rationcard'),

    path('check_diwali_token/', views.check_diwali_token, name='check_diwali_token'),

    path('change_diwali_token/', views.change_diwali_token, name='change_diwali_token'),

    path('list_diwalikirana/', views.list_diwalikirana, name='list_diwalikirana'),

    path('list_family/', views.list_family, name='list_family'),

    path('update_token_status/', views.update_token_status, name='update_token_status'),

    path('add_diwali_kirana/', views.add_diwali_kirana, name='add_diwali_kirana'),

    path('add_diwali_kirana_sms/', views.add_diwali_kirana_sms, name='add_diwali_kirana_sms'),

    path("delete_diwali_member/<int:reg_id>/", views.delete_diwali_member, name='api_delete_diwali_member'),

    path('bulk_update_diwali_kirana/', views.bulk_update_diwali_kirana, name='api_bulk_update_diwali_kirana'),

    path('add_diwali_family_member/', views.add_diwali_family_member, name='api_add_diwali_family_member'),

    path('upload_voter_id/', views.upload_voter_id, name='api_upload_voter_id'),

    path('list_all_registrations/', views.list_all_registrations, name='api_list_all_registrations'),


    
# #########  Event Managment ###################

    path('event_create/', views.create_event, name='create_event'),
    
    path('event_list/', views.event_list, name='get_events'),
    
    path('event_update/', views.update_event, name='update_event'),
    
    path('event_delete/', views.delete_event, name='delete_event'),

    path('event_configure/<int:event_id>/',views. configure_event_fields_api, name='configure_event_fields_api'),

    path('event_register/<int:event_id>/',views. event_registration_api, name='event_registration_api'),

    path('event_registrations/<int:event_id>/', views.view_event_registrations_api, name='api_event_registrations'),

    path('public/verify/<int:event_id>/<int:registration_id>/', views.get_public_registration_details, name='get_public_registration_details'),

    path('public/update_status/<int:event_id>/<int:registration_id>/', views.update_registration_status, name='update_registration_status'),
    
    path('public/cancel/<int:event_id>/<int:registration_id>/', views.cancel_registration, name='cancel_registration'),
   
]