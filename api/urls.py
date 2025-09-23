from django.urls import path
from . import views

urlpatterns = [

    path("agentlogin/", views.agentlogin, name="agentlogin"),
    # path('logout/', views.logout, name='logout'),
    # path('dashboard/' , views.dashboard, name='dashboard'),/


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
    path("getpilgrimcard/", views.getpilgrimcard, name="getpilgrimcard"),

    path("inserttickets/", views.inserttickets, name="inserttickets"),
   

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
    path('listyatrabuses/', views.list_yatra_buses, name='list_yatra_buses'), 
    path('createyatrabus/', views.create_yatra_bus, name='create_yatra_bus'), 

    path('modifyyatrabus/', views.modify_yatra_bus, name='modify_yatra_bus'), 
    path('insertyatra/', views.create_yatra, name='create_yatra'),
    path('modifyyatra/', views.modify_yatra, name='modify_yatra'),

    path('insertroute/', views.create_route, name='create_route'),
    path('modifyroute/', views.modify_route, name='modify_route'),
   
]