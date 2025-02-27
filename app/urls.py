from django.urls import path
from .views import UploadZipView, GalleryView, ViewImageView

urlpatterns = [
    path('', UploadZipView.as_view(), name='upload_zip'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('image/<int:image_id>/', ViewImageView.as_view(), name='view_image'),
]
