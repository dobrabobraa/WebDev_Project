# Участник 2 — Content

**Зона ответственности:** контент сайта — модель поста, лента, создание и редактирование поста, хэштеги, медиа-файлы (картинки и видео).

## Что я сделал

### Модель поста и лента

Создал модель `Post` с полями `title`, `text`, `author`, `created_at`, `updated_at`. Заголовок обязателен (валидация в сериализаторе: `required=True, allow_blank=False, max_length=200`).

Лента (`GET /api/posts/`) отдаёт посты в обратном хронологическом порядке. В API для оптимизации использую `select_related` (для FK) и `prefetch_related` (для M2M / reverse FK) — это убирает N+1 запросы при загрузке автора, хэштегов, медиа, опроса и комментариев одним махом.

На фронтенде лента — это **компактные карточки**: заголовок крупно, под ним одна строка с `@автор`, ♥ лайки, 💬 комментарии, дата и хэштеги. Если у поста есть медиа — показываю превью первой картинки/видео-бейдж. Вся карточка кликабельна и ведёт на `/posts/:id`.

### Страница полного поста

На `/posts/:id` рендерю полный контент: заголовок, тело, медиа-сетку, хэштеги, дату, кнопки лайка/редактирования/удаления.

### Редактирование и удаление

Добавил поле `updated_at = DateTimeField(auto_now=True)` в модель. Если `updated_at` отличается от `created_at` больше чем на пару секунд — показываю метку «edited» с датой правки.

Редактировать/удалять может **только автор поста** (проверка `post.author != request.user → 403`). В UI — inline edit-форма прямо на странице поста (не отдельный роут). PATCH-запрос с обновлёнными полями, затем перезагрузка данных.

Важное решение: **медиа и опросы при редактировании НЕ меняются**. Иначе сломается логика тех, кто уже проголосовал в опросе, и интерсептор получит конфликт с уже загруженными файлами. Пользователь может изменить только `title`, `text` и `hashtags`.

### Хэштеги

Модель `Hashtag(name)` с M2M к Post. Пользователь пишет их в свободной строке (`#python #django cool`), я их парсю: разбиваю по пробелам/запятым, убираю `#`, нижний регистр, дедуп. На каждый новый тег делаю `get_or_create` — старые переиспользуются, новые создаются.

В API хэштеги отдаются как массив строк: `["python", "django", "cool"]`. На фронтенде рендерятся как бейджи с `#`.

### Медиа: картинки и видео

Модель `PostMedia(post, file, kind, order)`. Поле `kind` — `image` или `video`, определяется по расширению файла. В форме создания поста — multi-file picker, превью-сетка с возможностью удалить файл до отправки.

На стороне сервера `PostListCreateView` и `PostDetailView` теперь принимают multipart (не только JSON), файлы приходят списком под ключом `media_files`. Для видео поднял лимиты загрузки до 50 МБ в `settings.py`:

```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
```

В ленте показываю превью первого медиа-файла. В детальной странице — сетку всех файлов: `<img>` для картинок, `<video controls>` для видео.

## Файлы, за которые я отвечаю

### Backend

| Файл | Что моё |
|------|---------|
| `backend/api/models.py` | классы `Post`, `Hashtag`, `PostMedia` |
| `backend/api/serializers.py` | `PostSerializer`, `PostMediaReadSerializer`, вспомогательные `_absolute`, `_detect_kind`, константы `IMAGE_EXTS`, `VIDEO_EXTS` |
| `backend/api/views.py` | `PostListCreateView`, `PostDetailView` (включая multipart-парсеры, проверку прав на edit/delete, prefetch_related цепочки) |
| `backend/api/urls.py` | маршруты `posts/` и `posts/<int:pk>/` |
| `backend/api/migrations/0003_post_title.py` | добавление `title` |
| `backend/api/migrations/0004_post_updated_at.py` | добавление `updated_at` |
| `backend/api/migrations/0005_hashtags_remove_category.py` | добавление `Hashtag` |
| `backend/api/migrations/0006_media_poll.py` (часть про `PostMedia`) | создание таблицы медиа |
| `backend/config/settings.py` (блок `FILE_UPLOAD_MAX_MEMORY_SIZE`) | лимиты на видео-загрузки |

### Frontend

| Файл | Что делает |
|------|-----------|
| `frontend/src/app/pages/feed/*` | Лента с компактными карточками и превью медиа |
| `frontend/src/app/pages/post-detail/*` | Просмотр и редактирование поста (основная часть; комментарии/опросы/упоминания — у участника 3) |
| `frontend/src/app/pages/create-post/*` | Форма создания поста (title, body, hashtags, media upload; поллы — у участника 3, но шаблон мой) |
| `frontend/src/app/services/post.service.ts` | `getPosts`, `getPost`, `createPost` (multipart), `updatePost`, `deletePost`, `likePost`, `addComment`, `votePoll` |
| `frontend/src/app/models/post.ts` | интерфейсы `Post`, `PostMedia`, `CommentItem` (+ `Poll`, `PollOption` от участника 3) |

## Технические решения, которые я принял

1. **Title обязателен, хэштеги нет** — чтобы лента всегда была читаемой (без заголовков посты сливались бы в кашу).
2. **Редактирование не трогает медиа и опросы** — иначе пришлось бы делать логику «заменить, сохранить старые, перезагрузить голоса». Упростил.
3. **Хэштеги нормализуются к lowercase** — `#Python`, `#python`, `#PYTHON` — это один тег.
4. **Медиа хранится в отдельной модели, не массивом JSONField** — чтобы можно было делать prefetch и не загружать base64 в каждом запросе.
5. **FormData на фронте, multipart на бэке** — единственный нормальный способ заливать файлы. JSON с base64 — это 33%-раздутие трафика и боль при больших видео.
6. **Лимит в 50 МБ** — компромисс между «можно залить клип» и «нельзя зафлудить сервер гигабайтами». Можно будет настроить выше в продакшене.

## API, которое я предоставил

```
GET    /api/posts/                                       → [Post, ...]
POST   /api/posts/    multipart:                         → 201 Post
                      title, text, hashtags_input_text,
                      media_files=[...], poll_question,
                      poll_options_text
GET    /api/posts/<id>/                                  → Post
PATCH  /api/posts/<id>/   JSON: title, text, hashtags    → Post
DELETE /api/posts/<id>/                                  → 204
```

Структура `Post` в ответе:
```ts
{
  id, title, text, created_at, updated_at,
  hashtags: string[],
  media: [{ id, kind, url, order }, ...],
  poll: null | { ...от участника 3 },
  comments: [...от участника 3],
  comments_count, likes_count,
  author_username, author_avatar,
}
```
