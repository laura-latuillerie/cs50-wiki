from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('wiki/<entry_title>', views.entry_page, name='entry_page'),
    path('random_page/', views.random_page, name='random_page'),
    path('create/', views.create_page, name='create_page'),
    path('search/', views.search, name='search'),
    path('edit/<entry_title>', views.edit, name='edit')
]
