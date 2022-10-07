from django.contrib import admin
from django.urls import path
from qrscan import views
from django.urls import path
from django.views.generic import TemplateView
from rest_framework import routers
from django.contrib.auth.views import LogoutView  
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('book/', views.book,name="homepage"),
    path('', views.homepage,name="home"),
    path('pay/',views.pay),
    path("payment/", views.book, name="payment"),
    # path('scan/',views.ScanQR, name='scan'),
    path('Call_Scan/',views.Call_Scan, name='Call_Scan'),
    path('scan',views.ScanQR, name='scan'),
    path('payment-status', views.payment_status, name='payment-status'),
    path("login/",views.login_page,name="login"),
    path("logout/",LogoutView.as_view(next_page="react_app"),name="logout"),
    path("Counter/", views.Counter, name="Counter"),
    path("adminpage/", views.Admin, name="AdminPage"),
    path('Ticket/',views.TaskList.as_view(),name='ticket'),
    path("react", views.MyReactView.as_view(), name='react_app'),  
    # this route catches any url below the main one, so the path can be passed to the front end
    path(r'react/<path:path>', views.MyReactView.as_view(), name='react_app_with_path'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

