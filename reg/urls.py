from django.urls import path
from django.conf.urls import url
from django import forms
from django.http import HttpResponse
from django.template import loader

from . import views

from .views import checking,goback,candidate_photo,Attendence_report,users_list,logout,login2,approve,app_submit,report,report1,GeneratePDF,GeneratePDFh,notapporve,GeneratePDF_not,sync_home,sync_server,approve_user,report_user,already_approved,clear,s3upload,clear_data,sync_images,facial,facial_submit,show_details,ghome,grievance,ghome1,grievance1

urlpatterns = [
    path('home', views.index, name='index'),
    path('', views.login1, name='login1'),
    path('login', views.login_details, name='login_details'),
    path('checking',checking, name='checking'),
    #path('view_photos', view_photos, name='view_photos'),
	path('users_list',users_list, name='users_list'),
    path('Attendence_report',Attendence_report, name='Attendence_report'),

    path('', goback, name='goback'),
    path('candidate_photo', candidate_photo, name='candidate_photo'),
    path(' logout', logout, name='logout'),
	path('loginh', login2, name='login2'),
	path('approve', approve, name='approve'),
	path('app_submit', app_submit, name='app_submit'),
	path('report', report, name='report'),
	path('report1', report1, name='report1'),
	path('pdf', GeneratePDF, name='GeneratePDF'),
	path('pdfhome', GeneratePDFh, name='GeneratePDFh'),
	path('notapphome', notapporve, name='notapporve'),
	path('pdfnot', GeneratePDF_not, name='GeneratePDF_not'),
	path('sync_home', sync_home, name='sync_home'),
	path('sync_server', sync_server, name='sync_server'),
	path('approve_user', approve_user, name='approve_user'),
	path('report_user', report_user, name='report_user'),
	path('already_approved', already_approved, name='already_approved'),
	path('s3upload', s3upload, name='s3upload'),
	path('sync_images', sync_images, name='sync_images'),
	path('clear', clear, name='clear'),
	#path('fetch_data', fetch_data, name='fetch_data'),
	path('clear_data', clear_data, name='clear_data'),
	path('facial', facial, name='facial'),
	path('facial_submit', facial_submit, name='facial_submit'),
	path('show_details',show_details , name='show_details'),
	
	path('ghome', ghome, name='ghome'),
	path('ghome1', ghome1, name='ghome1'),
	path('grievance', grievance, name='grievance'),
	path('grievance1', grievance1, name='grievance1'),
	
	
]

