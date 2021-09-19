from django.urls import path

from .views import AddImageView, ListImageView, SearchImagesView, ShareImageView

urlpatterns = [
    path('add/', AddImageView.as_view(), name='add_image'),
    path('my_images/', ListImageView.as_view(), name='my_image'),
    path('search/', SearchImagesView.as_view(), name='search_image'),
    path('share/', ShareImageView.as_view(), name='share_image')    
]