from django.urls import path
from . import views
urlpatterns = [
    # path('', views.home, name="home"),
    path('', views.HomePageView.as_view(), name="home"),
    # path('detail/<int:id>/', views.detail, name="detail"),
    path('detail/<int:pk>/', views.ContactDetailView.as_view(), name="detail"),
    path('search/', views.search, name="search"),
    path('contacts/create', views.ContactCreateView.as_view(), name="create"),
    path('contacts/update/<int:pk>',
         views.ContactUpdateView.as_view(), name="update"),
    path('contacts/delete/<int:pk>',
         views.ContactDeleteView.as_view(), name="delete"),
    path('signup/', views.SignUpView.as_view(), name="signup"),
]
