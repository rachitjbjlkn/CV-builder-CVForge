from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.home,        name='home'),
    path('auth/',               views.auth_view,    name='auth'),
    path('signup/',            views.signup,      name='signup'),
    path('signin/',            views.signin,     name='signin'),
    path('signout/',           views.signout,    name='signout'),
    path('upgrade/',           views.upgrade,     name='upgrade'),
    path('builder/',             views.cv_builder,  name='cv_builder'),
    path('builder/<int:pk>/',    views.cv_builder,  name='cv_edit'),
    path('save/',                views.save_cv,     name='save_cv'),
    path('save/<int:pk>/',       views.save_cv,     name='save_cv_update'),
    path('preview/<int:pk>/',    views.cv_preview,  name='cv_preview'),
    path('print/<int:pk>/',      views.cv_print,    name='cv_print'),
    path('print/demo/',          views.cv_print_demo, name='cv_print_demo'),
    path('delete/<int:pk>/',    views.delete_cv,   name='delete_cv'),
    path('ats/',                 views.ats_checker, name='ats_checker'),
    path('ats/<int:pk>/',       views.ats_checker, name='ats_checker_cv'),
    path('ats/analyze/',         views.analyze_ats, name='analyze_ats'),
    path('ats/external/',       views.analyze_external_cv, name='analyze_external'),
]
