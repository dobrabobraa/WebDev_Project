# Echo — командный проект (3 человека)

Небольшая соц. сеть на **Django + Angular**. Проект разделён на **3 равных по весу направления**, каждый участник отвечает за свой вертикальный срез (и бэкенд, и фронтенд своей зоны).

## Распределение ролей

| # | Участник | Направление | Что делает |
|---|----------|-------------|------------|
| 1 | **Участник 1** | **Identity & Social** (идентичность и социальный граф) | Регистрация, логин, JWT, профили, аватарки, подписки, статистика |
| 2 | **Участник 2** | **Content** (контент) | Модель поста, лента, создание/редактирование поста, хэштеги, медиа (картинки/видео) |
| 3 | **Участник 3** | **Engagement & UX** (взаимодействие и дизайн) | Лайки, комментарии, опросы, упоминания @username, дизайн-система, навигация, темы |

**Принцип деления:** каждый владеет примерно третьей частью кода и по одной крупной «пользовательской зоне». Никто не работает только на фронтенде или только на бэкенде — это академически нереалистично.

## Подробно о каждой роли

Смотри отдельные документы в папке `docs/`:

- [`docs/person-1-auth-social.md`](docs/person-1-auth-social.md) — участник 1
- [`docs/person-2-content.md`](docs/person-2-content.md) — участник 2
- [`docs/person-3-engagement-ui.md`](docs/person-3-engagement-ui.md) — участник 3
- [`docs/git-workflow.md`](docs/git-workflow.md) — как заливать по очереди в GitHub

## Стек

- **Backend:** Python 3.12+, Django 5.1, Django REST Framework, SimpleJWT, Pillow, SQLite
- **Frontend:** Angular 18+, TypeScript, RxJS

## Запуск локально

```bash
# Backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver     # http://127.0.0.1:8000

# Frontend (в другом терминале)
cd frontend
npm install
npm start                      # http://localhost:4200
```

## Структура репозитория

```
tiny-social-network/
├── backend/                   # Django проект
│   ├── api/                   # приложение
│   │   ├── models.py          # общий файл, каждый владеет своими моделями
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── migrations/
│   └── config/                # settings, urls
├── frontend/                  # Angular приложение
│   └── src/app/
│       ├── pages/             # страницы (login, feed, profile, post-detail, create-post)
│       ├── services/          # сервисы для API (auth, user, post)
│       ├── models/            # TypeScript интерфейсы
│       ├── interceptors/      # HTTP interceptors
│       └── utils/             # утилиты (mentions)
├── docs/                      # командная документация (эта папка)
└── TEAM.md                    # обзор (этот файл)
```

## Как делить общие файлы

Некоторые файлы (`api/models.py`, `api/serializers.py`, `api/views.py`, `api/urls.py`) **физически делятся между всеми тремя участниками** — в них у каждого свои классы/функции. Правило простое:

> **Каждый участник правит только свой блок** в этих файлах. В случае мёрдж-конфликтов — смотри, какой класс кому принадлежит (написано в docs/person-N.md).

Всё остальное (страницы, сервисы, миграции) разделено по файлам и конфликтов быть не должно.
