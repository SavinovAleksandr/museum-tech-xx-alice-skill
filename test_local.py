#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для локального тестирования навыка Яндекс.Алисы.
"""

import json
import os
import sys

# Устанавливаем режим работы в local
os.environ['WORK_MODE'] = 'local'

# Импортируем обработчик
from main import handler


def test_handler(event_name, event_data):
    """
    Тестирует обработчик с заданным событием.
    
    Args:
        event_name: Название теста
        event_data: Данные события
    """
    print(f"\n{'='*60}")
    print(f"ТЕСТ: {event_name}")
    print(f"{'='*60}")
    print(f"Запрос: {json.dumps(event_data, ensure_ascii=False, indent=2)}")
    print(f"\n--- Ответ ---")
    
    try:
        result = handler(event_data, None)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n✓ Тест выполнен успешно")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Главная функция для запуска тестов."""
    
    # Проверяем наличие items.json
    if not os.path.exists('items.json'):
        print("⚠ Предупреждение: Файл items.json не найден.")
        print("Создайте файл items.json или используйте пример из проекта.")
        sys.exit(1)
    
    print("Запуск тестов навыка Яндекс.Алисы 'Музей техники XX века'")
    print("=" * 60)
    
    # Тест 1: Приветствие при новом сеансе
    test_handler(
        "Приветствие при запуске",
        {
            "session": {
                "new": True,
                "session_id": "test-session-1",
                "user_id": "test-user-1"
            },
            "request": {
                "command": "",
                "original_utterance": ""
            },
            "version": "1.0"
        }
    )
    
    # Тест 2: Запрос номера экспоната
    test_handler(
        "Запрос номера экспоната",
        {
            "session": {
                "new": False,
                "session_id": "test-session-2",
                "user_id": "test-user-2"
            },
            "request": {
                "command": "номер 1",
                "original_utterance": "номер 1",
                "nlu": {
                    "intents": {
                        "get_number": {
                            "slots": {
                                "number": {
                                    "value": 1
                                }
                            }
                        }
                    }
                }
            },
            "version": "1.0",
            "state": {
                "session": {
                    "awaiting_number": True,
                    "current_item": None,
                    "current_part": 0
                }
            }
        }
    )
    
    # Тест 3: Команда "дальше"
    test_handler(
        "Команда 'дальше'",
        {
            "session": {
                "new": False,
                "session_id": "test-session-3",
                "user_id": "test-user-3"
            },
            "request": {
                "command": "дальше",
                "original_utterance": "дальше",
                "nlu": {
                    "intents": {
                        "next": {}
                    }
                }
            },
            "version": "1.0",
            "state": {
                "session": {
                    "awaiting_number": False,
                    "current_item": 1,
                    "current_part": 0
                }
            }
        }
    )
    
    # Тест 4: Команда "повтори"
    test_handler(
        "Команда 'повтори'",
        {
            "session": {
                "new": False,
                "session_id": "test-session-4",
                "user_id": "test-user-4"
            },
            "request": {
                "command": "повтори",
                "original_utterance": "повтори",
                "nlu": {
                    "intents": {
                        "repeat": {}
                    }
                }
            },
            "version": "1.0",
            "state": {
                "session": {
                    "awaiting_number": False,
                    "current_item": 1,
                    "current_part": 0
                }
            }
        }
    )
    
    # Тест 5: Команда "сначала"
    test_handler(
        "Команда 'сначала'",
        {
            "session": {
                "new": False,
                "session_id": "test-session-5",
                "user_id": "test-user-5"
            },
            "request": {
                "command": "сначала",
                "original_utterance": "сначала",
                "nlu": {
                    "intents": {
                        "restart": {}
                    }
                }
            },
            "version": "1.0",
            "state": {
                "session": {
                    "awaiting_number": False,
                    "current_item": 1,
                    "current_part": 1
                }
            }
        }
    )
    
    # Тест 6: Несуществующий номер
    test_handler(
        "Запрос несуществующего номера",
        {
            "session": {
                "new": False,
                "session_id": "test-session-6",
                "user_id": "test-user-6"
            },
            "request": {
                "command": "номер 999",
                "original_utterance": "номер 999",
                "nlu": {
                    "intents": {
                        "get_number": {
                            "slots": {
                                "number": {
                                    "value": 999
                                }
                            }
                        }
                    }
                }
            },
            "version": "1.0",
            "state": {
                "session": {
                    "awaiting_number": True,
                    "current_item": None,
                    "current_part": 0
                }
            }
        }
    )
    
    # Тест 7: Непонятная команда
    test_handler(
        "Непонятная команда",
        {
            "session": {
                "new": False,
                "session_id": "test-session-7",
                "user_id": "test-user-7"
            },
            "request": {
                "command": "привет",
                "original_utterance": "привет",
                "nlu": {
                    "intents": {}
                }
            },
            "version": "1.0",
            "state": {
                "session": {
                    "awaiting_number": True,
                    "current_item": None,
                    "current_part": 0
                }
            }
        }
    )
    
    print(f"\n{'='*60}")
    print("Все тесты завершены!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

