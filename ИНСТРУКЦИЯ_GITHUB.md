# Инструкция: Как отправить проект на GitHub

## 🚀 Быстрый способ (через командную строку)

### Шаг 1: Инициализация Git (если еще не сделано)

```bash
cd "/Users/anna/Documents/Фриланс/Музей в Алисе"
git init
```

### Шаг 2: Добавить все файлы

```bash
git add .
```

### Шаг 3: Создать первый коммит

```bash
git commit -m "Навык Яндекс.Алисы: Музей техники XX века - полная версия"
```

### Шаг 4: Создать репозиторий на GitHub

1. Откройте [GitHub.com](https://github.com)
2. Нажмите **"+"** → **"New repository"**
3. Заполните:
   - **Repository name:** `museum-tech-xx-alice-skill` (или любое другое имя)
   - **Description:** "Навык Яндекс.Алисы для музея техники и предметов быта XX века"
   - **Visibility:** Public или Private (на ваш выбор)
   - **НЕ** ставьте галочки на "Initialize with README", "Add .gitignore", "Choose a license"
4. Нажмите **"Create repository"**

### Шаг 5: Подключить локальный репозиторий к GitHub

GitHub покажет инструкции. Выполните команды (замените `YOUR_USERNAME` на ваш GitHub username):

```bash
git remote add origin https://github.com/YOUR_USERNAME/museum-tech-xx-alice-skill.git
git branch -M main
git push -u origin main
```

Если GitHub попросит авторизацию:
- Используйте Personal Access Token (не пароль)
- Или настройте SSH ключи

---

## 📋 Альтернативный способ (через GitHub Desktop)

1. Установите [GitHub Desktop](https://desktop.github.com/)
2. Откройте GitHub Desktop
3. File → Add Local Repository
4. Выберите папку проекта
5. Нажмите "Publish repository"
6. Заполните данные и опубликуйте

---

## 🔐 Настройка авторизации GitHub

### Вариант 1: Personal Access Token (рекомендуется)

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Выберите права: `repo` (полный доступ к репозиториям)
4. Скопируйте токен
5. При `git push` используйте токен вместо пароля

### Вариант 2: SSH ключи

```bash
# Создать SSH ключ
ssh-keygen -t ed25519 -C "your_email@example.com"

# Добавить ключ в ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Скопировать публичный ключ
cat ~/.ssh/id_ed25519.pub

# Добавить ключ в GitHub:
# Settings → SSH and GPG keys → New SSH key
```

---

## 📝 Что будет в репозитории

✅ **Включено:**
- Все `.py` файлы (main.py, utils.py, config.py и т.д.)
- Все `.json` файлы (intents.json, items.json)
- Все `.md` файлы (README.md, документация)
- requirements.txt
- .gitignore

❌ **Исключено (благодаря .gitignore):**
- `venv/` - виртуальное окружение
- `__pycache__/` - кэш Python
- `*.pyc` - скомпилированные файлы
- `.env` - переменные окружения (если есть)

---

## 🔄 Обновление репозитория

После изменений:

```bash
git add .
git commit -m "Описание изменений"
git push
```

---

## ⚠️ Важные замечания

1. **items.json содержит данные** - если репозиторий публичный, данные будут видны всем
   - Для приватных данных используйте Private репозиторий
   - Или вынесите items.json в .gitignore и загружайте отдельно

2. **Переменные окружения** - не коммитьте файлы с секретами:
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - Они должны быть только в переменных окружения Cloud Function

3. **Размер файлов:**
   - items.json весит ~1.1 МБ - это нормально для GitHub
   - Если файл больше 100 МБ, GitHub может предупредить

---

## 📦 Готовые команды (скопируйте и выполните)

```bash
# Перейдите в папку проекта
cd "/Users/anna/Documents/Фриланс/Музей в Алисе"

# Инициализация (если еще не сделано)
git init

# Добавить все файлы
git add .

# Создать коммит
git commit -m "Навык Яндекс.Алисы: Музей техники XX века - полная версия"

# Подключить к GitHub (замените YOUR_USERNAME и REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Отправить на GitHub
git branch -M main
git push -u origin main
```

---

## ✅ Проверка

После отправки:
1. Откройте ваш репозиторий на GitHub
2. Убедитесь, что все файлы на месте
3. Проверьте, что README.md отображается корректно

---

**Готово!** 🎉

