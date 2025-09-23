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
   
]