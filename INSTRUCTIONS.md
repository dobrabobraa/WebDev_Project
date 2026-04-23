# 📘 Инструкция для Участника 1 (Auth & Social)

Ты делаешь **первый** коммит. Твоя задача — создать репозиторий на GitHub и запушить туда начальную версию проекта, содержащую **только твою часть** (auth, профили, аватарки, подписки).

## Что у тебя в архиве

- **`tiny-social-network/`** — полная финальная версия проекта (чтобы ты мог его запустить и посмотреть как он работает целиком)
- **`tiny-social-network/MY_FILES/`** — папка со всеми твоими файлами, скопированными по их правильным путям
- **`tiny-social-network/TEAM.md`** и **`docs/`** — командная документация

## Шаг за шагом

### 1. Создай папку для своей работы

Скопируй только то, что нужно для первого коммита:

```bash
# На любое удобное место
mkdir ~/tiny-social-network-push1
cd ~/tiny-social-network-push1
```

### 2. Собери проект из файлов MY_FILES

Тебе нужны:

- **Всё из `MY_FILES/`** (скопируй с сохранением путей)
- **Скелет Django** (`backend/manage.py`, `backend/api/__init__.py`, `backend/api/apps.py`, `backend/api/migrations/__init__.py`, `backend/api/migrations/0001_initial.py`, `backend/config/__init__.py`, `backend/config/asgi.py`, `backend/config/wsgi.py`) — **возьми их из основного проекта `tiny-social-network/`**
- **Скелет Angular** (`frontend/angular.json`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/tsconfig*.json`, `frontend/src/index.html`, `frontend/src/main.ts`, `frontend/src/styles.css`, `frontend/src/app/app.component.*`, `frontend/src/app/app.module.ts`, `frontend/src/app/app-routing.module.ts`) — **тоже из основного проекта** (это временно, там будут заглушки для постов; участник 3 в конце их обновит)
- **`TEAM.md`**, **`docs/`**, **`README.md`**, **`.gitignore`** — тоже из основного проекта

**Самый простой способ**:

```bash
# Скопируй весь проект
cp -r /path/to/tiny-social-network/* ~/tiny-social-network-push1/
cd ~/tiny-social-network-push1

# УДАЛИ файлы, которые не принадлежат тебе (это файлы участников 2 и 3).
# Список удаляемых файлов — ниже.
```

### 3. Удали чужие файлы перед коммитом

Ниже — файлы НЕ твои. Их должны коммитить другие. Удали их в своей копии:

**Файлы участника 2 (контент):**
```bash
# Backend
rm -f backend/api/migrations/0003_post_title.py
rm -f backend/api/migrations/0004_post_updated_at.py
rm -f backend/api/migrations/0005_hashtags_remove_category.py

# Frontend
rm -rf frontend/src/app/pages/feed
rm -rf frontend/src/app/pages/create-post
rm -rf frontend/src/app/pages/post-detail
rm -f  frontend/src/app/models/post.ts
rm -f  frontend/src/app/services/post.service.ts
```

**Файлы участника 3 (engagement):**
```bash
# Backend
rm -f backend/api/migrations/0006_media_poll.py

# Frontend
rm -rf frontend/src/app/utils
```

### 4. Замени общие файлы на свою версию

Твои версии лежат в `MY_FILES/`. Скопируй их поверх:

```bash
# Скопировать все файлы из MY_FILES/ на их правильные пути
cp -r MY_FILES/backend/ ./
cp -r MY_FILES/frontend/ ./

# Удали саму папку MY_FILES — она нужна была только для транспорта
rm -rf MY_FILES
```

Теперь у тебя:
- `backend/api/models.py` — только `Profile`, `Follow` и сигнал
- `backend/api/serializers.py` — только auth и profile сериализаторы
- `backend/api/views.py` — только auth и profile views
- `backend/api/urls.py` — только auth/profile/follow роуты
- `backend/api/admin.py` — регистрация `Profile`, `Follow`
- `backend/config/settings.py` — с `MEDIA_URL` / `MEDIA_ROOT`
- `backend/config/urls.py` — с подключением media в DEBUG

### 5. Проверь что всё работает

Это важно — **твоя часть должна запускаться самостоятельно**.

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Должен стартовать на `http://127.0.0.1:8000`. Проверь в браузере:
- `http://127.0.0.1:8000/admin/` — админка Django должна открываться
- В новом терминале:
  ```bash
  curl -X POST http://127.0.0.1:8000/api/auth/register/ -H "Content-Type: application/json" -d '{"username":"test","password":"test1234"}'
  ```
  Должен вернуть 201.

Frontend пока не запустится целиком (нет страниц feed и create-post), но TypeScript компилируется — это ОК для первого коммита.

### 6. Настрой Git со своим именем

```bash
git config --global user.name "Имя Участника 1"
git config --global user.email "твой_email@example.com"
```

Email должен совпадать с email твоего GitHub-аккаунта (Settings → Emails) — иначе аватарка и ссылка на профиль в коммитах не подтянутся.

### 7. Создай репозиторий на GitHub

1. Зайди на [github.com](https://github.com) → **New repository**
2. Название: `tiny-social-network` (или `echo`)
3. НЕ добавляй README, .gitignore, LICENSE — они уже есть в проекте
4. Create

### 8. Инициализируй git и запушь

```bash
cd ~/tiny-social-network-push1

git init
git branch -M main
git add .
git status   # убедись что добавились только твои файлы

git commit -m "feat: initial project setup + JWT auth + profiles + avatars

- Django + DRF scaffolding
- JWT authentication (register/login/logout) via SimpleJWT
- Profile model with avatar upload (Pillow ImageField)
- Follow model and toggle endpoint
- User profile page with follow/unfollow button
- Avatar upload/remove endpoints
- Angular login and profile pages
- HTTP interceptor for auth token injection"

git remote add origin https://github.com/ТВОЙ-НИК/tiny-social-network.git
git push -u origin main
```

### 9. Дай ссылку участнику 2

Участник 2 начинает свою работу после того, как ты залил свою часть. Отправь ему URL репозитория.

---

## Что входит в твой коммит (проверь список)

**Backend:**
```
backend/manage.py
backend/requirements.txt              (твоя версия с Pillow)
backend/api/__init__.py
backend/api/apps.py
backend/api/admin.py                   (твоя — только Profile, Follow)
backend/api/models.py                  (твоя — Profile, Follow, сигнал)
backend/api/serializers.py             (твоя — auth + profile)
backend/api/views.py                   (твоя — auth + profile + follow + avatar)
backend/api/urls.py                    (твоя — только auth/profile/follow)
backend/api/migrations/__init__.py
backend/api/migrations/0001_initial.py
backend/api/migrations/0002_profile_follow.py     ← ТВОЯ МИГРАЦИЯ
backend/config/__init__.py
backend/config/asgi.py
backend/config/wsgi.py
backend/config/settings.py             (твоя версия — с MEDIA_URL/MEDIA_ROOT)
backend/config/urls.py                 (твоя — с media в DEBUG)
```

**Frontend:**
```
frontend/angular.json
frontend/package.json
frontend/package-lock.json
frontend/tsconfig.json
frontend/tsconfig.app.json
frontend/src/index.html
frontend/src/main.ts
frontend/src/styles.css                (временная заглушка — финальная у участника 3)
frontend/src/app/app.module.ts         (временная — финальная у участника 3)
frontend/src/app/app-routing.module.ts (временная — финальная у участника 3)
frontend/src/app/app.component.ts
frontend/src/app/app.component.html
frontend/src/app/interceptors/auth.interceptor.ts  ← ТВОЙ
frontend/src/app/models/user-profile.ts             ← ТВОЙ
frontend/src/app/pages/login/*                      ← ТВОЯ СТРАНИЦА
frontend/src/app/pages/profile/*                    ← ТВОЯ СТРАНИЦА
frontend/src/app/services/auth.service.ts           ← ТВОЙ
frontend/src/app/services/user.service.ts           ← ТВОЙ
```

**Документация:**
```
README.md
TEAM.md
docs/person-1-auth-social.md
docs/person-2-content.md
docs/person-3-engagement-ui.md
docs/git-workflow.md
.gitignore
tiny-social-network.postman_collection.json
```

---

## ⚠️ Если что-то пошло не так

**«У меня ошибка при `python manage.py migrate`»**
→ Проверь что ты применил обе миграции (`0001_initial` и `0002_profile_follow`). Версия 0001 пока пустая (создаёт Category, Post и прочее что тебе не нужно), но она должна остаться для совместимости с миграциями участников 2 и 3.

**«У меня Pillow не устанавливается»**
→ Если у тебя Python 3.14, замени в `requirements.txt` строчку `Pillow==11.0.0` на `Pillow>=12.0.0`.

**«Я уже запушил, но потом увидел что забыл удалить чужие файлы»**
→ Удали их, сделай `git add .`, `git commit -m "chore: remove files belonging to others"`, `git push`. Но лучше заранее проверь список в шаге 3.
