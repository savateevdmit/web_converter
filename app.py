import os
import zipfile
from django.conf import settings
from django.conf.urls.static import static
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.views import View
from django.core.wsgi import get_wsgi_application
from test import conv

# Проверяем, если настройки уже конфигурированы, тогда пропускаем
if not settings.configured:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = 'your-secret-key'
    DEBUG = True

    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    CSRF_TRUSTED_ORIGINS = []

    # Добавляем ngrok URL в ALLOWED_HOSTS и CSRF_TRUSTED_ORIGINS
    NGROK_HOST = 'd3ce-46-242-12-86.ngrok-free.app'
    if NGROK_HOST:
        ALLOWED_HOSTS.append(NGROK_HOST)
        CSRF_TRUSTED_ORIGINS.append(f'https://{NGROK_HOST}')

    INSTALLED_APPS = [
        'django.contrib.staticfiles',
        'django.contrib.sessions',
    ]

    MIDDLEWARE = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.security.SecurityMiddleware',
    ]

    ROOT_URLCONF = __name__
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(BASE_DIR, 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.template.context_processors.media',
                ],
            },
        },
    ]

    WSGI_APPLICATION = 'app.application'

    STATIC_URL = '/static/'
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

    # Минимальная конфигурация базы данных
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

    settings.configure(
        SECRET_KEY=SECRET_KEY,
        DEBUG=DEBUG,
        ALLOWED_HOSTS=ALLOWED_HOSTS,
        CSRF_TRUSTED_ORIGINS=CSRF_TRUSTED_ORIGINS,
        INSTALLED_APPS=INSTALLED_APPS,
        MIDDLEWARE=MIDDLEWARE,
        ROOT_URLCONF=ROOT_URLCONF,
        TEMPLATES=TEMPLATES,
        WSGI_APPLICATION=WSGI_APPLICATION,
        STATIC_URL=STATIC_URL,
        STATICFILES_DIRS=STATICFILES_DIRS,
        MEDIA_URL=MEDIA_URL,
        MEDIA_ROOT=MEDIA_ROOT,
        DATABASES=DATABASES,
    )
else:
    print(1)

class Image:
    def __init__(self, image):
        self.image = image

class UploadZipView(View):
    def get(self, request):
        return render(request, 'upload_zip.html')

    def post(self, request):
        if request.method == 'POST' and request.FILES['zip_file']:
            zip_file = request.FILES['zip_file']
            if not zip_file.name.endswith('.zip'):
                return render(request, 'upload_zip.html', {'error': 'Пожалуйста, загрузите ZIP файл.'})

            fs = FileSystemStorage()
            filename = fs.save(zip_file.name, zip_file)
            folder_name = os.path.splitext(filename)[0]
            file_path = fs.path(filename)

            folder_name = conv(filename)
            os.remove(f'media/{filename}')

            request.session['folder_name'] = folder_name
            return redirect('gallery')
        return render(request, 'upload_zip.html', {'error': 'No file uploaded.'})

class GalleryView(View):
    def get(self, request):
        folder_name = request.session.get('folder_name')
        if not folder_name:
            return redirect('upload_zip')

        images = []
        folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)
        for file_name in os.listdir(folder_path):
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                images.append(os.path.join(folder_name, file_name))
        return render(request, 'gallery.html', {'images': images})

    def post(self, request):
        folder_name = request.session.get('folder_name')
        if not folder_name:
            return redirect('upload_zip')

        folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)
        zip_path = os.path.join(settings.MEDIA_ROOT, f'{folder_name}.zip')

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(('.png', '.jpg', '.jpeg')):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))

        with open(zip_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{folder_name}.zip"'
            return response

class ViewImageView(View):
    def get(self, request, image_id):
        folder_name = request.session.get('folder_name')
        if not folder_name:
            return redirect('upload_zip')

        images = []
        folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)
        for file_name in os.listdir(folder_path):
            if file_name.endswith(('.png', '.jpg', '.jpeg')):
                images.append(os.path.join(folder_name, file_name))

        if image_id < 0 or image_id >= len(images):
            return redirect('gallery')

        image = images[image_id]
        image_url = os.path.join(settings.MEDIA_URL, image)

        prev_image_id = image_id - 1 if image_id > 0 else None
        next_image_id = image_id + 1 if image_id < len(images) - 1 else None

        return render(request, 'view_image.html', {
            'image_url': image_url,
            'prev_image_id': prev_image_id,
            'next_image_id': next_image_id,
        })

# URL Configuration
urlpatterns = [
    path('', UploadZipView.as_view(), name='upload_zip'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('image/<int:image_id>/', ViewImageView.as_view(), name='view_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

application = get_wsgi_application()

if __name__ == '__main__':
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver'])
