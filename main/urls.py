"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from stockroom import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.ClientListView.as_view(), name='client_list'),
    path('client/<int:pk>/', views.ClientHolderProductBatchListView.as_view(), name='client_detail'),
    path('relocation_list/', views.RelocationListView.as_view(), name='relocation_list'),
    path('generate/', views.GenerateDataFormView.as_view(), name='generate_data')
]
