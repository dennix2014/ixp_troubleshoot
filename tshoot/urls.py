from django.urls import path

from . import views

urlpatterns = [
    path('list_switches/', views.list_switches, name='list_switches'),
    path('list_peers/', views.list_peers, name='list_peers'),
    path('update_peers/', views.update_peers, name='update_peers'),
    path('bgp_neighbor_received/', views.bgp_neighbor_received, name='bgp_neighbor_received'),
    path('bgp_status/', views.bgp_status, name='bgp_status'),
    path('update_switches/', views.update_switches, name='update_switches'),
    path('l1_l2_test/<int:pk>', views.l1_l2_test, name='l1_l2_test'),
    path('fetch_logs/<int:pk>', views.fetch_logs, name='fetch_logs'),
    path('l3_basic_test/<int:pk>', views.l3_basic_test, name='l3_basic_test'),
    path('l3_reachability/', views.l3_reachability, name='l3_reachability'),
    
]
