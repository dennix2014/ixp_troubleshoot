from django.urls import path

from . import views

urlpatterns = [
    path('list_switches/', views.list_switches, name='list_switches'),
    path('list_peers/', views.list_peers, name='list_peers'),
    path('l3_reachability/', views.l3_reachability, name='l3_reachability'),
    path('add_switch/', views.add_or_edit_switch, name='add_switch'),
    path('edit_switch/<int:pk>/', views.add_or_edit_switch, name='edit_switch'),
    path('add_member/', views.add_or_edit_member, name='add_member'),
    path('edit_member/<int:pk>/', views.add_or_edit_member, name='edit_member'),
    
]
