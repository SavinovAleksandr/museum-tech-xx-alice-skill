# -*- coding: utf-8 -*-
"""
Вспомогательные функции для навыка Яндекс.Алисы.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


def split_description_by_sentences(text: str, max_length: int = 1024) -> List[str]:
    """
    Разбивает описание экспоната на части по предложениям.
    Каждая часть не превышает max_length символов.
    
    Args:
        text: Текст описания
        max_length: Максимальная длина части в символах
        
    Returns:
        Список частей текста
    """
    if not text or not isinstance(text, str):
        return []
    
    # Разбиваем по знакам конца предложения
    sentences = re.split(r'([.!?]+(?:\s+|$))', text)
    
    parts = []
    current_part = ""
    
    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        if i + 1 < len(sentences):
            sentence += sentences[i + 1]
            i += 2
        else:
            i += 1
        
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Если предложение превышает лимит, разбиваем по запятым
        if len(sentence) > max_length:
            if current_part:
                parts.append(current_part.strip())
                current_part = ""
            
            # Разбиваем длинное предложение по запятым и точкам с запятой
            sub_parts = re.split(r'([,;]\s+)', sentence)
            current_sub = ""
            for j in range(0, len(sub_parts), 2):
                sub_sent = sub_parts[j]
                if j + 1 < len(sub_parts):
                    sub_sent += sub_parts[j + 1]
                
                if len(current_sub) + len(sub_sent) <= max_length:
                    current_sub += sub_sent
                else:
                    if current_sub:
                        parts.append(current_sub.strip())
                    current_sub = sub_sent
            if current_sub:
                current_part = current_sub
            continue
        
        # Добавляем предложение к текущей части
        if len(current_part) + len(sentence) + 1 <= max_length:
            if current_part:
                current_part += " " + sentence
            else:
                current_part = sentence
        else:
            # Начинаем новую часть
            if current_part:
                parts.append(current_part.strip())
            current_part = sentence
    
    # Добавляем последнюю часть
    if current_part:
        parts.append(current_part.strip())
    
    # Если частей нет, возвращаем весь текст (даже если он длиннее лимита)
    # Это может произойти только если весь текст без разделителей
    if not parts:
        # Принудительно разбиваем по словам, если текст слишком длинный
        if len(text) > max_length:
            words = text.split()
            current_chunk = ""
            for word in words:
                if len(current_chunk) + len(word) + 1 <= max_length:
                    current_chunk += (" " if current_chunk else "") + word
                else:
                    if current_chunk:
                        parts.append(current_chunk)
                    current_chunk = word
            if current_chunk:
                parts.append(current_chunk)
        else:
            parts.append(text)
    
    return parts


def prepare_items_dict(items_json: Dict[str, str], max_length: int = 1024) -> Dict[str, List[str]]:
    """
    Подготавливает словарь экспонатов с разбитыми на части описаниями.
    
    Args:
        items_json: Словарь {номер: описание}
        max_length: Максимальная длина части описания
        
    Returns:
        Словарь {номер: [часть1, часть2, ...]}
    """
    prepared = {}
    
    for number, description in items_json.items():
        parts = split_description_by_sentences(description, max_length)
        if parts:
            prepared[str(number)] = parts
    
    return prepared


def get_intent_from_request(request: dict) -> Tuple[str, Optional[int]]:
    """
    Определяет интент из запроса Яндекс.Диалогов.
    
    Args:
        request: Объект запроса от Яндекс.Диалогов
        
    Returns:
        Кортеж (интент, номер_экспоната)
        Интенты: 'get_number', 'next', 'repeat', 'restart', 'invalid'
    """
    # Проверяем наличие интентов
    intents = request.get('request', {}).get('nlu', {}).get('intents', {})
    
    # Проверяем интент get_number
    if 'get_number' in intents:
        slots = intents['get_number'].get('slots', {})
        number_slot = slots.get('number', {})
        if number_slot:
            number = number_slot.get('value')
            if number is not None:
                return 'get_number', int(number)
    
    # Проверяем интент next (дальше)
    if 'next' in intents:
        return 'next', None
    
    # Проверяем интент repeat (повтори)
    if 'repeat' in intents:
        return 'repeat', None
    
    # Проверяем интент restart (сначала)
    if 'restart' in intents:
        return 'restart', None
    
    # Проверяем прямой ввод номера в тексте
    text = request.get('request', {}).get('command', '').lower().strip()
    
    # Ищем числа в тексте
    numbers = re.findall(r'\d+', text)
    if numbers:
        try:
            number = int(numbers[0])
            return 'get_number', number
        except ValueError:
            pass
    
    # Проверяем ключевые слова
    if any(word in text for word in ['дальше', 'следующ', 'продолжи', 'продолж']):
        return 'next', None
    
    if any(word in text for word in ['повтори', 'ещё раз', 'снова']):
        return 'repeat', None
    
    if any(word in text for word in ['сначала', 'заново', 'первый', 'начать']):
        return 'restart', None
    
    return 'invalid', None


def get_session_state(request: dict) -> dict:
    """
    Получает состояние сессии из запроса.
    
    Args:
        request: Объект запроса от Яндекс.Диалогов
        
    Returns:
        Словарь состояния сессии
    """
    return request.get('state', {}).get('session', {
        'awaiting_number': True,
        'current_item': None,
        'current_part': 0
    })


def format_response(text: str, tts: Optional[str] = None, end_session: bool = False, session_state: Optional[dict] = None, version: str = '1.0') -> dict:
    """
    Форматирует ответ для Яндекс.Диалогов.
    
    Args:
        text: Текст ответа
        tts: Текст для озвучивания (если отличается от text)
        end_session: Завершить сессию
        session_state: Состояние сессии
        version: Версия протокола (по умолчанию '1.0')
        
    Returns:
        Отформатированный ответ
    """
    response = {
        'response': {
            'text': text,
            'tts': tts if tts else text,
            'end_session': end_session
        },
        'version': version
    }
    
    if session_state:
        response['session_state'] = session_state
    
    return response


def log_request(number: Optional[int], status: str, part: Optional[int] = None):
    """
    Логирует запрос в формате: [time] number=N status=ok|no_description|invalid_phrase part=K
    
    Args:
        number: Номер экспоната
        status: Статус обработки (ok, no_description, invalid_phrase)
        part: Номер части описания
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    number_str = str(number) if number is not None else 'None'
    part_str = f" part={part}" if part is not None else ""
    
    log_message = f"[{timestamp}] number={number_str} status={status}{part_str}"
    print(log_message)
    logger.info(log_message)

