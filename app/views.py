import os
import zipfile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from parser import conv

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
