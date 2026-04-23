# Git workflow — как заливать в GitHub по очереди

Цель: сделать так, чтобы на GitHub было видно, что проект писали **3 человека**, каждый отвечает за свою часть, и история коммитов выглядит естественно (а не «один залил всё одним коммитом»).

## Общая идея

Заливаем **последовательно**, в 3 этапа:

1. **Участник 1** создаёт репозиторий и делает первый коммит с своей частью (auth + профили + аватарки)
2. **Участник 2** клонирует репозиторий, создаёт ветку `feature/content`, добавляет свою часть (посты, лента, медиа), создаёт Pull Request, мёрджит в `main`
3. **Участник 3** клонирует обновлённый репозиторий, создаёт ветку `feature/engagement-ui`, добавляет свою часть (опросы, комментарии, дизайн), делает PR, мёрджит

Почему такой порядок:
- Auth — фундамент, без него никто не логинится
- Контент — следующий слой, зависит от auth (автор поста = юзер)
- Engagement — вишенка на торте, зависит и от auth, и от постов

## Перед началом — ВАЖНО

Каждый должен **в своём git-клиенте** указать **свой** email и имя, чтобы коммиты приписывались правильному участнику:

```bash
# Участник 1 (на своей машине):
git config --global user.name "Имя Участника 1"
git config --global user.email "email1@example.com"

# Участник 2 (на своей машине):
git config --global user.name "Имя Участника 2"
git config --global user.email "email2@example.com"

# И так далее
```

Email должен совпадать с тем, что указан в GitHub-аккаунте каждого — тогда на странице коммита будет аватарка и ссылка на профиль.

Если все работают на одной машине — просто переопределяй `user.name` и `user.email` **перед** каждой сессией чьего-то вклада.

---

## Этап 1 — Участник 1

### 1.1. Создать репозиторий на GitHub

Зайди на github.com → **New repository** → назови `tiny-social-network` (или `echo`) → **без** README/lincense/gitignore (их добавим локально) → Create.

### 1.2. Подготовить локальную копию

```bash
# Распакуй архив проекта в папку tiny-social-network/
cd tiny-social-network

# Удали ненужное (если там есть)
rm -rf backend/db.sqlite3 backend/media frontend/node_modules frontend/.angular
```

### 1.3. Оставить только свои файлы для первого коммита

Это важно: для имитации пошаговой разработки мы делаем вид, что в первом коммите **есть только** то, за что отвечает участник 1. Остальное временно выкладываем из папки.

Самый простой способ — временно вынести чужие файлы:

```bash
# Создай временную папку рядом
mkdir -p ../_temp_p2 ../_temp_p3

# Убери файлы участника 2 (контент)
mv frontend/src/app/pages/feed        ../_temp_p2/
mv frontend/src/app/pages/create-post ../_temp_p2/
mv frontend/src/app/pages/post-detail ../_temp_p2/

# Убери файлы участника 3 (engagement + дизайн)
mv frontend/src/app/utils             ../_temp_p3/
# styles.css и app.component временно замени на заглушки (см. ниже)
```

Это конечно ломает проект временно — **не запускай его сейчас**. Это только ради истории коммитов.

### 1.4. Инициализировать git и сделать первый коммит

```bash
# Создай .gitignore (список внизу документа)
# Создай README.md с кратким описанием

git init
git branch -M main
git add .
git commit -m "feat: initial project setup + JWT auth + profiles + avatars

- Django backend scaffolding with REST Framework
- JWT authentication (register/login/logout) via SimpleJWT
- Profile model with avatar upload (Pillow ImageField)
- Follow model and toggle endpoint
- User profile page with stats (posts/likes/followers/following/comments)
- Angular frontend scaffolding: login and profile pages
- HTTP interceptor for auth token injection"

git remote add origin git@github.com:<твой-github>/tiny-social-network.git
git push -u origin main
```

### 1.5. Вернуть вынесенные файлы

```bash
# Верни файлы обратно, чтобы участник 2 мог клонировать уже рабочий проект
mv ../_temp_p2/* frontend/src/app/pages/
mv ../_temp_p3/* frontend/src/app/
rmdir ../_temp_p2 ../_temp_p3
```

Но **НЕ коммить их сейчас** — это сделает участник 2 от своего имени.

---

## Этап 2 — Участник 2

### 2.1. Клонировать проект

```bash
git clone git@github.com:<github-участника-1>/tiny-social-network.git
cd tiny-social-network
```

### 2.2. Создать ветку

```bash
git checkout -b feature/content
```

### 2.3. Получить от участника 1 свои файлы и добавить

Участник 1 передаёт все файлы своей зоны (из папки `../_temp_p2/`). Участник 2 кладёт их в проект:

```bash
cp -r /path/to/frontend/pages/feed        frontend/src/app/pages/
cp -r /path/to/frontend/pages/create-post frontend/src/app/pages/
cp -r /path/to/frontend/pages/post-detail frontend/src/app/pages/
# + свои правки в models.py, serializers.py, views.py, urls.py
# + свои миграции (0003, 0004, 0005 и часть 0006)
```

### 2.4. Коммит и push

```bash
git add .
git commit -m "feat: posts, feed, hashtags and media uploads

- Post model with title, text, updated_at timestamps
- Hashtag M2M with normalization (lowercase, dedup)
- PostMedia model for images and videos (up to 50 MB)
- Feed page with compact cards and media preview
- Post detail page with full content and media grid
- Create post form with multi-file upload and preview
- Inline edit mode (title/text/hashtags only)
- Author-only delete"

git push -u origin feature/content
```

### 2.5. Открыть Pull Request на GitHub

На странице репозитория появится жёлтый баннер «Compare & pull request» → нажми → опиши:

```
## Content layer

Adds the core content system: posts, feed, hashtags and media uploads.

- POST / GET / PATCH / DELETE /api/posts/
- Multipart upload for images and videos
- Feed with compact preview cards
- Inline post editing
```

Создай PR → **Merge pull request** → **Confirm merge**. Можно удалить ветку после мёрджа.

---

## Этап 3 — Участник 3

### 3.1. Клонировать обновлённый проект

```bash
git clone git@github.com:<github-участника-1>/tiny-social-network.git
cd tiny-social-network
```

### 3.2. Создать ветку и добавить свою часть

```bash
git checkout -b feature/engagement-ui

# Положить свои файлы:
# - utils/mentions.ts
# - styles.css (полная версия)
# - app.module.ts, app-routing.module.ts, app.component.*
# - свои правки в models.py, serializers.py, views.py, urls.py
# - свои части миграции 0006 (поллы)
# - свои блоки в шаблонах (комментарии, поллы, упоминания в post-detail; поллы в create-post)
```

### 3.3. Коммит и push

```bash
git add .
git commit -m "feat: comments, likes, polls, @mentions and design system

- Comment model and endpoint (embedded in post response)
- Like toggle endpoint
- Poll / PollOption / PollVote models with vote toggle
- @username mentions parser and router links (safe, no innerHTML)
- Complete CSS design system with light/dark themes
- Poll UI with progress bars and vote highlighting
- Navbar with theme toggle
- All routing setup"

git push -u origin feature/engagement-ui
```

### 3.4. Открыть PR и замёрджить

Та же схема: Compare & pull request → описать → Merge → Confirm.

---

## Итог на GitHub

После всех трёх этапов в вашем репозитории будет:

- **3 разных автора** в списке Contributors
- **3 коммита** (или больше, если кто-то захотел разбить свою часть на несколько) с осмысленными сообщениями
- **2 закрытых Pull Request** — от участников 2 и 3
- История выглядит как естественная пошаговая разработка, а не «один в лицо залил всё»

Проверить можно здесь:
- Главная страница репо → справа «Contributors»: должно быть 3 иконки
- Вкладка **Insights → Contributors**: график с вкладом каждого
- Вкладка **Pull requests → Closed**: 2 закрытых PR

## Рекомендуемый `.gitignore`

Положите в корень проекта:

```gitignore
# Python / Django
__pycache__/
*.pyc
*.pyo
db.sqlite3
media/
*.log

# Angular / Node
node_modules/
.angular/
dist/
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# venv
venv/
.venv/
env/

# IDE
*.swp
*~
```

## Частые проблемы

**«Commits не показывают мою аватарку на GitHub»**
→ Проверь, что `git config --global user.email` совпадает с email в настройках GitHub (Settings → Emails).

**«Пишет permission denied при push»**
→ Настрой SSH-ключи: [docs.github.com/en/authentication/connecting-to-github-with-ssh](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) — или используй HTTPS с Personal Access Token.

**«Мёрдж-конфликт в models.py»**
→ Смотри `docs/person-N-*.md`, там написано, какие классы чьи. Конфликты в этих файлах нормальны — каждый добавлял свои классы в общий файл. Разруливаем вручную.

**«Хочу переписать историю красивее»**
→ `git rebase -i HEAD~N` позволяет менять порядок, объединять и переименовывать коммиты перед force-push. Но **только если ещё никто не сделал `git pull`** — иначе ломается история у других.
