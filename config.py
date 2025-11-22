# -*- coding: utf-8 -*-
"""
Конфигурационный файл для навыка Яндекс.Алисы "Музей техники XX века".
"""

import os

# Настройки Object Storage
BUCKET_NAME = os.environ.get('BUCKET', 'museum-tech-xx')
JSON_FILE_NAME = os.environ.get('FILE', 'items.json')

# Лимит длины одной части описания (символов)
# Учитываем запас для служебных фраз:
# - " Рассказать дальше?" = 19 символов
# - " Это всё про этот экспонат. Назови другой номер на наклейке." = 60 символов
# Используем 964 как безопасный лимит (1024 - 60)
MAX_PART_LENGTH = 964

# Настройки AWS S3 (Yandex Object Storage использует S3 API)
S3_ENDPOINT = os.environ.get('S3_ENDPOINT', 'https://storage.yandexcloud.net')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_REGION = os.environ.get('AWS_REGION', 'ru-central1')

# Режим работы (local для тестирования без Object Storage)
WORK_MODE = os.environ.get('WORK_MODE', 'cloud')  # 'cloud' или 'local'

# Локальный путь к JSON файлу (для режима local)
LOCAL_JSON_PATH = 'items.json'

