# Участник 3 — Engagement & UX

**Зона ответственности:** то, как пользователи взаимодействуют с контентом — лайки, комментарии, опросы, упоминания — а также **общая дизайн-система** сайта.

## Что я сделал

### Комментарии

Модель `Comment(post, author, text, created_at)`. Эндпоинт `POST /api/posts/<post_id>/comments/` добавляет комментарий. Читаются комментарии прямо внутри `PostSerializer` — я вложил их как массив в ответ поста, чтобы лишний раз не бегать на сервер.

Комментарии идут в обратном хронологическом порядке (самые свежие сверху). В комментариях можно использовать `@username` — парсится моей утилитой `splitMentions`.

### Лайки

Модель `Like(post, user, created_at)` с `unique_together=(post, user)`. Эндпоинт `POST /api/posts/<id>/like/` работает как toggle: если лайк уже есть — удаляет, нет — ставит. В ленте и на детальной странице показывается счётчик.

### Опросы (polls)

Три модели:
- `Poll(post, question)` — 1-к-1 с Post
- `PollOption(poll, text, order)` — варианты ответа
- `PollVote(poll, option, user)` — голоса, `unique_together=(poll, user)`

В форме создания поста — поле вопроса и `<textarea>` с вариантами (один на строку, минимум 2, максимум 10). Бэкенд парсит это в `PollSerializer._apply_poll()`.

Эндпоинт `POST /api/posts/<id>/vote/` с `{option_id}` — тоже toggle:
- клик по своему варианту → снимает голос
- клик по другому → переключает (удаляет старый голос, ставит новый)
- первый клик → ставит голос

На UI варианты отрисовываются как кнопки с фоновым прогресс-баром: ширина пропорциональна проценту голосов. Свой голос выделен галочкой ✓ и акцентной рамкой. Счётчик «N votes» внизу.

### Упоминания пользователей

Утилита `splitMentions(text)` парсит строку и возвращает массив фрагментов:

```ts
[
  { type: 'text', value: 'Hello ' },
  { type: 'mention', value: '@alice', username: 'alice' },
  { type: 'text', value: ', how are you?' },
]
```

Angular рендерит упоминания как `routerLink="/profile/<username>"` — без `innerHTML`, без XSS. Применяется и в теле поста, и в тексте каждого комментария.

Regex: `@([A-Za-z0-9_]{1,150})` — та же семантика, что у Django-юзернеймов.

### Дизайн-система

Я автор всего `src/styles.css` (почти 900 строк). Там:

- **CSS-переменные** для тем (светлая/тёмная). Все цвета через `var(--accent)`, `var(--text-2)`, `var(--surface)` и т.д. — переключение темы меняет одну строку `[data-theme="dark"]`.
- **Система компонентов**: `.btn`, `.btn-primary`, `.btn-ghost`, `.btn-danger`, `.btn-sm`, `.btn-like`; `.card`, `.input`, `.form-group`, `.form-hint`
- **Страничные сетки**: `.media-grid`, `.media-preview-grid`, `.stats-grid`, `.post-preview-card`
- **Специфические компоненты**: `.poll-option` с прогресс-баром, `.mention-link`, `.author-row` с аватаркой и никнеймом, `.category-badge` для хэштегов
- **Адаптивность**: мобильная вёрстка через `@media (min-width: 480px)`
- **Состояния**: hover, focus, disabled, loading — для каждого интерактивного элемента
- **Тёмная тема** — вся палитра пересчитана для комфортного чтения

### Навигация и скелет приложения

- `app.module.ts` — регистрация всех компонентов и `HttpClientModule`, подключение интерсептора
- `app-routing.module.ts` — все маршруты (`/login`, `/feed`, `/create`, `/posts/:id`, `/profile`, `/profile/:username`)
- `app.component.html` / `.ts` — верхняя навигационная панель, переключатель темы 🌙/☀️ (сохраняет выбор в `localStorage`)
- `index.html`, `main.ts` — точка входа

## Файлы, за которые я отвечаю

### Backend

| Файл | Что моё |
|------|---------|
| `backend/api/models.py` | классы `Comment`, `Like`, `Poll`, `PollOption`, `PollVote` |
| `backend/api/serializers.py` | `CommentSerializer`, `LikeSerializer`, `PollReadSerializer`, `PollOptionReadSerializer`, поле `comments` и функции `_apply_poll` внутри общего `PostSerializer` |
| `backend/api/views.py` | `CommentListCreateView`, `ToggleLikeView`, `PollVoteView` |
| `backend/api/urls.py` | маршруты `posts/<id>/comments/`, `posts/<id>/like/`, `posts/<id>/vote/` |
| `backend/api/migrations/0001_initial.py` | базовые таблицы Comment, Like (стартовая миграция) |
| `backend/api/migrations/0006_media_poll.py` (часть про Poll) | таблицы `Poll`, `PollOption`, `PollVote` |

### Frontend

| Файл | Что делает |
|------|-----------|
| `frontend/src/app/utils/mentions.ts` | Парсер `@username` в фрагменты |
| `frontend/src/styles.css` | Вся дизайн-система, темы, компоненты, анимации |
| `frontend/src/app/app.module.ts` | Регистрация компонентов и модулей |
| `frontend/src/app/app-routing.module.ts` | Маршруты |
| `frontend/src/app/app.component.*` | Навбар, переключатель темы |
| `frontend/src/index.html`, `main.ts` | HTML-шаблон, бутстрап Angular |
| Блоки внутри `pages/post-detail/*.html` | Рендер комментариев, опроса с голосованием, упоминаний в тексте — это мои вставки в шаблон участника 2 |
| Блок «Poll» внутри `pages/create-post/*.html` | Форма создания опроса (вопрос + textarea опций) — моя вставка |

## Технические решения, которые я принял

1. **Комментарии внутри PostSerializer, не отдельный endpoint** — на детальной странице они всегда нужны, лишний запрос только замедлит рендер.
2. **Toggle-семантика для лайков и голосов** — одна кнопка вместо двух («поставить» / «снять»). Меньше кода, меньше багов.
3. **Опрос нельзя редактировать после создания** — иначе у проголосовавших «потеряется» смысл. Если надо — пересоздавай пост.
4. **Mentions рендерятся через Angular-шаблон, не innerHTML** — безопасно от XSS. Вредоносный `<script>` в тексте комментария не выполнится, потому что Angular экранирует всё.
5. **CSS-переменные вместо SCSS/Less** — чтобы не было зависимости от препроцессора и темы переключались мгновенно.
6. **Дизайн-система однофайловая** — удобнее искать и менять, чем 20 файлов по компонентам. Всё равно стилей немного.
7. **`prefers-color-scheme` НЕ используется как дефолт** — я сохраняю выбор юзера в localStorage, чтобы его желание было важнее, чем системная тема.

## API, которое я предоставил

```
POST /api/posts/<id>/comments/     { text }               → 201 Comment
POST /api/posts/<id>/like/                                → toggle, 200/201 { message }
POST /api/posts/<id>/vote/         { option_id }          → toggle, 200/201 { message, my_vote_option_id }
```

Структура `Poll`, которую я добавил в ответ `Post`:

```ts
{
  id,
  question,
  options: [
    { id, text, order, votes_count },
    ...
  ],
  total_votes,
  my_vote_option_id,   // null если ещё не голосовал
}
```

И структура `CommentItem`:

```ts
{
  id,
  text,
  created_at,
  author_username,
  author_avatar,
}
```
