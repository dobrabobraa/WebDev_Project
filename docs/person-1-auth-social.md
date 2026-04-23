# Участник 1 — Identity & Social

**Зона ответственности:** всё, что связано с пользователем — регистрация, вход, профиль, аватарка, подписки, статистика.

## Что я сделал

### Аутентификация и JWT

Реализовал полный цикл auth:
- Регистрация нового пользователя (`POST /api/auth/register/`)
- Вход по username/password с выдачей JWT-токенов access + refresh (`POST /api/auth/login/`)
- Выход с blacklist-ом refresh-токена (`POST /api/auth/logout/`)
- Angular-интерсептор, который автоматически подкладывает access-токен в заголовок `Authorization: Bearer ...` ко всем запросам, кроме `/auth/login` и `/auth/register`

### Профили пользователей

Создал модель `Profile` (1-к-1 с `User`) с полем `avatar = ImageField`. Профиль создаётся автоматически через Django-сигнал `post_save` при создании пользователя. Аватарка загружается multipart-запросом и хранится в `media/avatars/`.

Настроил `MEDIA_URL` / `MEDIA_ROOT` в `config/settings.py` и обслуживание media-файлов через `config/urls.py` в DEBUG-режиме. Добавил `Pillow` в зависимости.

### Страница профиля со статистикой

На странице профиля (`/profile` — свой, `/profile/:username` — чужой) показываются карточки:

- **Posts** — количество постов автора
- **Likes** — сколько всего лайков собрали его посты (через `annotate + aggregate`)
- **Followers** / **Following** — подписчики и подписки
- **Comments** — сколько комментариев оставил

Всё считается в одном сериализаторе `UserProfileSerializer` с использованием `obj.posts.count()`, `annotate(Count)`, `aggregate(Sum)`.

### Система подписок

Модель `Follow(follower, following, created_at)` с `unique_together`. Эндпоинт `POST /api/users/<username>/follow/` работает как toggle: если подписан — отписывает, если нет — подписывает. Ответ содержит `is_following: bool` для синхронизации кнопки в UI.

Флаг `is_following` в `UserProfileSerializer` вычисляется относительно текущего запрашивающего — для anonymous всегда `false`.

## Файлы, за которые я отвечаю

### Backend

| Файл | Что моё |
|------|---------|
| `backend/api/models.py` | классы `Profile`, `Follow`, сигнал `create_profile_for_new_user` |
| `backend/api/serializers.py` | `RegistrationSerializer`, `LoginSerializer`, `UserProfileSerializer`, `AvatarUploadSerializer`, вспомогательная функция `_avatar_url` |
| `backend/api/views.py` | `register_view`, `login_view`, `logout_view`, `UserProfileView`, `ToggleFollowView`, `AvatarUploadView` |
| `backend/api/urls.py` | маршруты `auth/*`, `users/<username>/*`, `profile/avatar/` |
| `backend/api/migrations/0002_profile_follow.py` | создание таблиц `Profile` и `Follow` |
| `backend/config/settings.py` | `MEDIA_URL`, `MEDIA_ROOT`, `SIMPLE_JWT` блок |
| `backend/config/urls.py` | подключение media-роутинга в DEBUG |
| `backend/requirements.txt` | строчка с `Pillow` |

### Frontend

| Файл | Что делает |
|------|-----------|
| `frontend/src/app/pages/login/*` | Страница входа/регистрации |
| `frontend/src/app/pages/profile/*` | Страница профиля (своего и чужого), карточки со статистикой, загрузка/удаление аватарки, кнопка Follow/Unfollow |
| `frontend/src/app/services/auth.service.ts` | Обёртки над auth-эндпоинтами, хранение токенов в `localStorage` |
| `frontend/src/app/services/user.service.ts` | `getProfile`, `toggleFollow`, `uploadAvatar`, `removeAvatar` |
| `frontend/src/app/interceptors/auth.interceptor.ts` | Подставляет `Authorization: Bearer` кроме auth-эндпоинтов |
| `frontend/src/app/models/user-profile.ts` | Интерфейс `UserProfile` |

## Технические решения, которые я принял

1. **JWT вместо сессий** — удобнее для SPA, не требует CSRF-защиты на API.
2. **Сигнал `post_save`** для автосоздания профиля — гарантия, что у каждого юзера всегда есть профиль, даже если его создали через Django-shell или админку.
3. **Интерсептор не подставляет токен на login/register** — иначе при протухшем токене юзер вообще не мог бы залогиниться заново (получал бы 401 на логин).
4. **Toggle-семантика follow** — один эндпоинт вместо двух (`/follow` + `/unfollow`). Меньше роутов, меньше багов.
5. **Аватарка как `ImageField`**, не `FileField` — Pillow сам валидирует, что это действительно изображение.

## API, которое я предоставил

```
POST   /api/auth/register/         { username, password }                  → 201 + user_id
POST   /api/auth/login/            { username, password }                  → { access, refresh, username }
POST   /api/auth/logout/           { refresh }                             → 200
GET    /api/users/<username>/                                              → { username, avatar, posts_count, likes_received, comments_count, followers_count, following_count, is_following, is_self }
POST   /api/users/<username>/follow/                                       → { message, is_following }
POST   /api/profile/avatar/        multipart: avatar=<File>                → { message, avatar: url }
DELETE /api/profile/avatar/                                                → 200
```

Эти эндпоинты используют все три участника — через мою авторизацию работает весь проект.
