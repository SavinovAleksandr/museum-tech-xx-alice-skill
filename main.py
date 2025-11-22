# -*- coding: utf-8 -*-
"""
Основной обработчик Cloud Function для навыка Яндекс.Алисы "Музей техники XX века".
"""

import json
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Optional

import config
import utils

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения данных экспонатов
# Загружается при холодном старте
items_dict: Optional[Dict[str, list]] = None


def load_items_from_s3() -> Dict[str, list]:
    """
    Загружает items.json из Yandex Object Storage.
    
    Returns:
        Словарь {номер: [часть1, часть2, ...]}
    """
    try:
        # Создаем S3 клиент
        s3_client = boto3.client(
            's3',
            endpoint_url=config.S3_ENDPOINT,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION
        )
        
        # Загружаем файл из Object Storage
        logger.info(f"Загрузка {config.JSON_FILE_NAME} из bucket {config.BUCKET_NAME}")
        response = s3_client.get_object(Bucket=config.BUCKET_NAME, Key=config.JSON_FILE_NAME)
        content = response['Body'].read().decode('utf-8')
        
        # Парсим JSON
        items_json = json.loads(content)
        
        # Подготавливаем словарь с разбитыми на части описаниями
        prepared = utils.prepare_items_dict(items_json, config.MAX_PART_LENGTH)
        
        logger.info(f"Загружено {len(prepared)} экспонатов из Object Storage")
        return prepared
        
    except ClientError as e:
        logger.error(f"Ошибка при загрузке из Object Storage: {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при обработке данных: {e}")
        raise


def load_items_local() -> Dict[str, list]:
    """
    Загружает items.json из локального файла (для тестирования).
    
    Returns:
        Словарь {номер: [часть1, часть2, ...]}
    """
    try:
        with open(config.LOCAL_JSON_PATH, 'r', encoding='utf-8') as f:
            items_json = json.load(f)
        
        prepared = utils.prepare_items_dict(items_json, config.MAX_PART_LENGTH)
        logger.info(f"Загружено {len(prepared)} экспонатов из локального файла")
        return prepared
        
    except FileNotFoundError:
        logger.error(f"Файл {config.LOCAL_JSON_PATH} не найден")
        return {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке локального файла: {e}")
        return {}


def load_items() -> Dict[str, list]:
    """
    Загружает данные экспонатов в зависимости от режима работы.
    
    Returns:
        Словарь {номер: [часть1, часть2, ...]}
    """
    if config.WORK_MODE == 'local':
        return load_items_local()
    else:
        return load_items_from_s3()


def handle_get_number(number: int, session_state: dict) -> dict:
    """
    Обрабатывает запрос на получение описания экспоната по номеру.
    
    Args:
        number: Номер экспоната
        session_state: Текущее состояние сессии
        
    Returns:
        Ответ навыка
    """
    global items_dict
    
    number_str = str(number)
    
    # Проверяем наличие экспоната
    if number_str not in items_dict or not items_dict[number_str]:
        utils.log_request(number, 'no_description')
        
        response_text = (
            f"Про экспонат с номером {number} рассказа пока нет. "
            "Назови номер, который есть на наклейках в зале."
        )
        
        session_state['awaiting_number'] = True
        session_state['current_item'] = None
        session_state['current_part'] = 0
        
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    
    # Получаем первую часть описания
    parts = items_dict[number_str]
    current_part = parts[0]
    
    session_state['awaiting_number'] = False
    session_state['current_item'] = number
    session_state['current_part'] = 0
    
    utils.log_request(number, 'ok', part=0)
    
    # Если есть несколько частей, упоминаем об этом
    if len(parts) > 1:
        response_text = f"{current_part} Рассказать дальше?"
    else:
        response_text = current_part
    
    return utils.format_response(
        response_text,
        session_state=session_state
    )


def handle_next(session_state: dict) -> dict:
    """
    Обрабатывает команду "дальше" для получения следующей части описания.
    
    Args:
        session_state: Текущее состояние сессии
        
    Returns:
        Ответ навыка
    """
    global items_dict
    
    current_item = session_state.get('current_item')
    current_part = session_state.get('current_part', 0)
    
    # Проверяем, что есть текущий экспонат
    if current_item is None:
        utils.log_request(None, 'invalid_phrase')
        response_text = (
            "Сначала назови номер на наклейке — например, номер 7."
        )
        session_state['awaiting_number'] = True
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    
    number_str = str(current_item)
    
    if number_str not in items_dict:
        utils.log_request(current_item, 'no_description')
        response_text = (
            "К сожалению, информация об этом экспонате отсутствует. "
            "Назови другой номер на наклейке."
        )
        session_state['awaiting_number'] = True
        session_state['current_item'] = None
        session_state['current_part'] = 0
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    
    parts = items_dict[number_str]
    next_part_index = current_part + 1
    
    # Проверяем, есть ли следующая часть
    if next_part_index < len(parts):
        next_part = parts[next_part_index]
        session_state['current_part'] = next_part_index
        
        utils.log_request(current_item, 'ok', part=next_part_index)
        
        # Если это последняя часть
        if next_part_index == len(parts) - 1:
            response_text = f"{next_part} Это всё про этот экспонат. Назови другой номер на наклейке."
        else:
            response_text = f"{next_part} Рассказать дальше?"
        
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    else:
        # Нет больше частей
        utils.log_request(current_item, 'ok', part=current_part)
        response_text = (
            "Это всё про этот экспонат. "
            "Назови другой номер на наклейке."
        )
        session_state['awaiting_number'] = True
        return utils.format_response(
            response_text,
            session_state=session_state
        )


def handle_repeat(session_state: dict) -> dict:
    """
    Обрабатывает команду "повтори" для повторения текущей части.
    
    Args:
        session_state: Текущее состояние сессии
        
    Returns:
        Ответ навыка
    """
    global items_dict
    
    current_item = session_state.get('current_item')
    current_part = session_state.get('current_part', 0)
    
    # Проверяем, что есть текущий экспонат
    if current_item is None:
        utils.log_request(None, 'invalid_phrase')
        response_text = (
            "Сначала назови номер на наклейке — например, номер 7."
        )
        session_state['awaiting_number'] = True
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    
    number_str = str(current_item)
    
    if number_str not in items_dict:
        utils.log_request(current_item, 'no_description')
        response_text = (
            "К сожалению, информация об этом экспонате отсутствует. "
            "Назови другой номер на наклейке."
        )
        session_state['awaiting_number'] = True
        session_state['current_item'] = None
        session_state['current_part'] = 0
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    
    parts = items_dict[number_str]
    
    if current_part < len(parts):
        part_text = parts[current_part]
        utils.log_request(current_item, 'ok', part=current_part)
        
        if current_part < len(parts) - 1:
            response_text = f"{part_text} Рассказать дальше?"
        else:
            response_text = part_text
        
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    else:
        # Неожиданная ситуация
        return handle_get_number(current_item, session_state)


def handle_restart(session_state: dict) -> dict:
    """
    Обрабатывает команду "сначала" для повторения описания с начала.
    
    Args:
        session_state: Текущее состояние сессии
        
    Returns:
        Ответ навыка
    """
    current_item = session_state.get('current_item')
    
    if current_item is None:
        utils.log_request(None, 'invalid_phrase')
        response_text = (
            "Сначала назови номер экспоната."
        )
        session_state['awaiting_number'] = True
        return utils.format_response(
            response_text,
            session_state=session_state
        )
    
    # Начинаем с первой части
    return handle_get_number(current_item, session_state)


def handle_invalid(session_state: dict) -> dict:
    """
    Обрабатывает нераспознанную команду.
    
    Args:
        session_state: Текущее состояние сессии
        
    Returns:
        Ответ навыка
    """
    utils.log_request(None, 'invalid_phrase')
    
    response_text = (
        "Назови номер на наклейке — например, номер 7."
    )
    
    return utils.format_response(
        response_text,
        session_state=session_state
    )


def handler(event, context):
    """
    Главный обработчик Cloud Function.
    
    Args:
        event: Событие от Яндекс.Диалогов
        context: Контекст выполнения функции
        
    Returns:
        Ответ для Яндекс.Диалогов
    """
    global items_dict
    
    # Загружаем данные при холодном старте
    if items_dict is None:
        try:
            items_dict = load_items()
            if not items_dict:
                logger.error("Не удалось загрузить данные экспонатов")
                return utils.format_response(
                    "Извините, произошла ошибка. Попробуйте позже.",
                    end_session=True
                )
        except Exception as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
            return utils.format_response(
                "Извините, произошла ошибка при загрузке данных. Попробуйте позже.",
                end_session=True
            )
    
    # Проверяем тип запроса
    if isinstance(event, str):
        try:
            event = json.loads(event)
        except json.JSONDecodeError:
            logger.error("Не удалось распарсить событие")
            return utils.format_response(
                "Извините, произошла ошибка обработки запроса.",
                end_session=True
            )
    
    # Проверяем, что это запрос от Яндекс.Диалогов
    if 'request' not in event:
        logger.error("Некорректный формат запроса")
        return utils.format_response(
            "Извините, произошла ошибка.",
            end_session=True
        )
    
    # Проверяем новый сеанс (приветствие)
    is_new_session = event.get('session', {}).get('new', False)
    session_state = utils.get_session_state(event)
    
    # Если новый сеанс, приветствуем пользователя
    if is_new_session:
        welcome_text = (
            "Это музей Музей техники и предметов быта XX века. "
            "Назови номер на наклейке — например, номер 5."
        )
        session_state = {
            'awaiting_number': True,
            'current_item': None,
            'current_part': 0
        }
        return utils.format_response(
            welcome_text,
            session_state=session_state
        )
    
    # Определяем интент
    intent, number = utils.get_intent_from_request(event)
    
    # Обрабатываем интент
    if intent == 'get_number':
        return handle_get_number(number, session_state)
    elif intent == 'next':
        return handle_next(session_state)
    elif intent == 'repeat':
        return handle_repeat(session_state)
    elif intent == 'restart':
        return handle_restart(session_state)
    else:
        return handle_invalid(session_state)

