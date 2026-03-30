"""
URL Configuration for transmittals app V2.
"""
from django.urls import path
from . import views
from . import views_external

app_name = 'transmittals'

urlpatterns = [
    # Create Transmittal
    path('create/', views.create_transmittal, name='create_transmittal'),
    path('success/', views.transmittal_success, name='transmittal_success'),
    
    # Transmittal Lists
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_emails, name='sent_emails'),
    
    # Know More / Flow Info
    path('flow-info/', views.transmittal_flow_info, name='flow_info'),
    
    # Transmittal Reports & Export (User & Admin)
    path('report/', views.user_transmittal_report, name='user_report'),
    
    # Transmittal Detail & Actions
    path('detail/<int:pk>/', views.transmittal_detail, name='detail'),
    path('print/<int:pk>/', views.print_transmittal, name='print'),
    
    # Status Updates
    path('mark-arrived/<int:pk>/', views.mark_arrived, name='mark_arrived'),
    path('mark-pick/<int:pk>/', views.mark_pick, name='mark_pick'),
    path('mark-received/<int:pk>/', views.mark_received, name='mark_received'),
    path('cancel/<int:pk>/', views.cancel_transmittal, name='cancel_transmittal'),
    
    # Trash Management - DISABLED
    path('delete/', views.delete_emails, name='delete_emails'),
    path('restore/', views.restore_emails, name='restore_emails'),
    path('permanent-delete/', views.permanent_delete_emails, name='permanent_delete_emails'),
    
    # Custodian Views
    path('custodian/dashboard/', views.custodian_dashboard, name='custodian_dashboard'),
    path('custodian/in-transit/', views.custodian_in_transit, name='custodian_in_transit'),
    path('custodian/arrived/', views.custodian_arrived, name='custodian_arrived'),
    path('custodian/picked/', views.custodian_picked, name='custodian_picked'),
    path('custodian/received/', views.custodian_received, name='custodian_received'),
    path('custodian/outgoing/', views.custodian_outgoing, name='custodian_outgoing'),
    path('custodian/export-received/', views.custodian_export_received, name='custodian_export_received'),
    path('custodian/report/', views.custodian_transmittal_report, name='custodian_report'),
    
    # AJAX Endpoints
    path('api/location/<int:location_id>/custodian/', views.get_location_custodian, name='get_location_custodian'),
    path('api/search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('api/update-driver/<int:pk>/', views.update_driver_remarks, name='update_driver_remarks'),
    path('api/bulk-update-driver/', views.bulk_update_driver_remarks, name='bulk_update_driver_remarks'),
    path('api/bulk-pick/', views.bulk_pick, name='bulk_pick'),
    path('api/bulk-arrived/', views.bulk_arrived, name='bulk_arrived'),
    
    # Legacy
    path('toggle-resolved/<int:pk>/', views.toggle_resolved, name='toggle_resolved'),
    
    # ========================================================================
    # EXTERNAL TRANSMITTAL SYSTEM
    # ========================================================================
    
    # External Transmittal Dashboard
    path('external/dashboard/', views_external.external_transmittal_dashboard, name='external_dashboard'),
    
    # External Transmittal Creation
    path('external/create/', views_external.external_transmittal_create, name='external_create'),
    
    # External Transmittal Lists
    path('external/inbox/', views_external.external_transmittal_inbox, name='external_inbox'),
    path('external/sent/', views_external.external_transmittal_sent, name='external_sent'),
    
    # External Transmittal Detail
    path('external/detail/<int:pk>/', views_external.external_transmittal_detail, name='external_detail'),
    
    # External Transmittal Resolution Actions
    path('external/mark-received/<int:pk>/', views_external.external_transmittal_mark_received, name='external_mark_received'),
    path('external/full-return/<int:pk>/', views_external.external_transmittal_full_return, name='external_full_return'),
    path('external/partial-return/<int:pk>/', views_external.external_transmittal_partial_return, name='external_partial_return'),
    path('external/paid-sample/<int:pk>/', views_external.external_transmittal_paid_sample, name='external_paid_sample'),
    path('external/convert-to-keep/<int:pk>/', views_external.external_transmittal_convert_to_keep, name='external_convert_to_keep'),
    path('external/<int:pk>/cancel/', views_external.cancel_external_transmittal, name='cancel_external_transmittal'),
    
    # Admin Override
    path('external/admin-override/<int:pk>/', views_external.external_transmittal_admin_override, name='external_admin_override'),
    
    # External Transmittal Report & Export
    path('external/report/', views_external.external_transmittal_report, name='external_report'),
    
    # Secure File Download (requires login)
    path('external/download/<int:transmittal_id>/<int:attachment_id>/', views_external.secure_external_file_download, name='secure_file_download'),
]
