#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для конвертации Excel файла в JSON формат для навыка Яндекс.Алисы.
Преобразует файл с двумя столбцами (номер, описание) в items.json.
"""

import pandas as pd
import json
import re
import sys
from pathlib import Path


def clean_text(text):
    """
    Очищает текст от лишних переносов строк и пробелов.
    
    Args:
        text: Исходный текст
        
    Returns:
        Очищенный текст
    """
    if pd.isna(text) or not isinstance(text, str):
        return ""
    
    # Удаляем множественные пробелы и переносы строк
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    text = text.strip()
    
    return text


def split_by_sentences(text, max_length=1024):
    """
    Разбивает текст на части по предложениям, каждая часть <= max_length символов.
    
    Args:
        text: Текст для разбиения
        max_length: Максимальная длина части (по умолчанию 1024)
        
    Returns:
        Список частей текста
    """
    if not text:
        return []
    
    # Разбиваем по знакам конца предложения
    sentences = re.split(r'([.!?]+(?:\s+|$))', text)
    
    # Объединяем предложения с их знаками препинания
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
        
        # Если одно предложение превышает max_length, разбиваем его по запятым
        if len(sentence) > max_length:
            # Добавляем текущую часть, если есть
            if current_part:
                parts.append(current_part.strip())
                current_part = ""
            
            # Разбиваем длинное предложение по запятым
            sub_sentences = re.split(r'([,;]\s+)', sentence)
            current_sub = ""
            for j in range(0, len(sub_sentences), 2):
                sub_sent = sub_sentences[j]
                if j + 1 < len(sub_sentences):
                    sub_sent += sub_sentences[j + 1]
                
                if len(current_sub) + len(sub_sent) <= max_length:
                    current_sub += sub_sent
                else:
                    if current_sub:
                        parts.append(current_sub.strip())
                    current_sub = sub_sent
            if current_sub:
                current_part = current_sub
            continue
        
        # Проверяем, поместится ли предложение в текущую часть
        if len(current_part) + len(sentence) + 1 <= max_length:
            if current_part:
                current_part += " " + sentence
            else:
                current_part = sentence
        else:
            # Сохраняем текущую часть и начинаем новую
            if current_part:
                parts.append(current_part.strip())
            current_part = sentence
    
    # Добавляем последнюю часть
    if current_part:
        parts.append(current_part.strip())
    
    return parts if parts else [text]


def convert_excel_to_json(excel_path, output_path):
    """
    Конвертирует Excel файл в JSON формат.
    
    Args:
        excel_path: Путь к Excel файлу
        output_path: Путь к выходному JSON файлу
    """
    try:
        # Читаем Excel файл
        print(f"Чтение Excel файла: {excel_path}")
        df = pd.read_excel(excel_path)
        
        # Проверяем наличие двух столбцов
        if len(df.columns) < 2:
            raise ValueError("Файл должен содержать минимум 2 столбца")
        
        # Первый столбец - номер, второй - описание
        items = {}
        
        for index, row in df.iterrows():
            # Получаем номер экспоната (первый столбец)
            number = row.iloc[0]
            
            # Пропускаем пустые строки
            if pd.isna(number):
                continue
            
            # Преобразуем номер в строку
            number_str = str(int(float(number))) if isinstance(number, (int, float)) else str(number).strip()
            
            # Пропускаем, если номер пустой
            if not number_str:
                continue
            
            # Получаем описание (второй столбец)
            description = row.iloc[1]
            
            # Очищаем описание
            description_clean = clean_text(description)
            
            # Пропускаем, если описание пустое
            if not description_clean:
                continue
            
            # Добавляем в словарь
            items[number_str] = description_clean
        
        # Сохраняем в JSON
        print(f"Сохранение JSON файла: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Конвертация завершена. Создано {len(items)} экспонатов.")
        
    except FileNotFoundError:
        print(f"✗ Ошибка: Файл {excel_path} не найден")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Ошибка при конвертации: {e}")
        sys.exit(1)


def main():
    """Главная функция скрипта."""
    # Путь к Excel файлу (по умолчанию из промпта)
    default_excel = "/mnt/data/Описание экспонатов, 2 столбца.xlsx"
    
    # Путь к выходному JSON файлу
    output_json = "items.json"
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        excel_path = sys.argv[1]
    else:
        excel_path = default_excel
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        output_path = output_json
    
    # Проверяем существование входного файла
    if not Path(excel_path).exists():
        print(f"⚠ Предупреждение: Файл {excel_path} не найден.")
        print(f"Используйте: python convert_excel_to_json.py <путь_к_excel> [путь_к_output]")
        print(f"Создаю пример items.json...")
        # Создаем пример файла
        example_items = {
            "1": "Это пример описания первого экспоната музея техники XX века.",
            "2": "Это пример описания второго экспоната с более длинным текстом, который может содержать несколько предложений и рассказывать об истории и особенностях экспоната.",
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(example_items, f, ensure_ascii=False, indent=2)
        print(f"✓ Создан пример файла {output_path}")
        return
    
    # Выполняем конвертацию
    convert_excel_to_json(excel_path, output_path)


if __name__ == "__main__":
    main()

