from django.urls import path
from . import views

app_name = "myapp"

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('users/', views.usersApi, name='users'),
    path('login/', views.login_user, name='login'),
    path('postLogin/', views.postLogin, name='postLogin'),
    path('createInvoice/', views.invoiceApi, name='createInvoice'),
    path('logout/', views.logout_user, name='logout'),
    path('summary-by-business-code/', views.summary_by_business_code, name='summary-by-business-code'),
    path('summary-by-inv-currency/', views.summary_by_inv_currency, name='summary-by-inv-currency'),
    path('summary-by-doc-type/', views.summary_by_doc_type, name='summary-by-doc-type'),
    path('summary-by-cust-category/', views.summary_by_cust_category, name='summary-by-cust-category'),
    path('invoice-delay-prediction/', views.invoice_delay_prediction, name='invoice-delay-prediction'),
]