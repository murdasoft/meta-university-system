import os
import uuid
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from PIL import Image
import logging

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """
    Загрузка изображения
    
    POST /api/storage/upload/
    Body: multipart/form-data с полем 'file'
    
    Returns:
    {
        "url": "http://...",
        "file_id": "...",
        "size": 12345
    }
    """
    if 'file' not in request.FILES:
        return Response(
            {'detail': 'Файл не предоставлен', 'error_code': 'FILE_REQUIRED'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Валидация размера (максимум 5MB)
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        return Response(
            {
                'detail': f'Размер файла превышает 5MB. Ваш файл: {file.size / 1024 / 1024:.2f}MB',
                'error_code': 'FILE_TOO_LARGE'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Валидация типа файла
    valid_extensions = ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']
    ext = file.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        return Response(
            {
                'detail': f'Недопустимый формат файла. Разрешены: {", ".join(valid_extensions)}',
                'error_code': 'INVALID_FILE_TYPE'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Проверка что это валидное изображение
        img = Image.open(file)
        img.verify()
        
        # Переоткрыть после verify
        file.seek(0)
        img = Image.open(file)
        
        # Генерация уникального имени файла
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{ext}"
        
        # Путь для сохранения (по датам)
        today = datetime.now()
        upload_path = f"uploads/{today.year}/{today.month:02d}/{today.day:02d}/{filename}"
        
        # Сохранение файла
        file_content = ContentFile(file.read())
        saved_path = default_storage.save(upload_path, file_content)
        
        # URL файла
        file_url = request.build_absolute_uri(default_storage.url(saved_path))
        
        return Response({
            'url': file_url,
            'file_id': file_id,
            'size': file.size,
            'format': ext,
            'width': img.width,
            'height': img.height,
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Ошибка при загрузке файла: {str(e)}")
        return Response(
            {
                'detail': f'Ошибка при обработке изображения: {str(e)}',
                'error_code': 'PROCESSING_ERROR'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
