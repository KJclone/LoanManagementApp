"""LoanManagement URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from application import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.homepage,name="homepage"),
    path('homepage',views.homepage,name="homepage"),
    path('signup',views.signup,name="signup"),
    path('signin',views.signin,name="signin"),
    path('otplogin',views.otplogin,name="otplogin"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('applyloan',views.applyloan,name="applyloan"),
    path('viewapplications',views.viewapplications,name="viewapplications"),
    path('sanctionloan/<int:id>',views.sanctionloan,name="sanctionloan"),
    path('myloans',views.myloans,name="myloans"),
    path('updateterms/<int:id>',views.updateterms,name="updateterms"),
    path('trackrepayments',views.trackrepayments,name='trackrepayments'),
    path('deposit',views.deposit),
    path('success/<int:amount>',views.success),
    path('report',views.report),
    path('notification',views.notification),
    path('killsession',views.killsession),
    path('chat',views.chat,name="chat"),
    path('manageroom/<str:email>',views.manageroom,name="manageroom"),
    path('message',views.message,name='message'),
    path('getmessages',views.getmessages,name="getmessages"),
    path('sendmessage',views.sendmessage,name="sendmessage"),
    path('getbalance',views.getbalance,name='getbalance')
]
