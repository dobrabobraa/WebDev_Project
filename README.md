# Tiny Social Network

Tiny Social Network is a mini fullstack web app for anonymous posting.  
Users authenticate with JWT, create posts, comment on posts, like posts, and browse the anonymous feed.  
The backend keeps actions linked to authenticated users, while the frontend hides author names.

## Stack

- Frontend: Angular 17+, FormsModule, Routing, HttpClient, JWT Interceptor
- Backend: Django, Django REST Framework, Simple JWT, CORS
- Testing: Postman
- Version control: GitHub

## Requirements Coverage

### Frontend
- 4 click events: create post, delete post, like post, logout
- 4 ngModel bindings: username, password, post text, comment text
- Routing with 3 named routes: `/login`, `/feed`, `/create`
- `@for` and `@if` used in templates
- Angular service with HttpClient
- JWT interceptor
- API error handling
- Basic CSS styling

### Backend
- 4 models: Category, Post, Comment, Like
- 2+ ForeignKey relations
- 2 serializers from `Serializer`: RegistrationSerializer, LoginSerializer
- 2+ serializers from `ModelSerializer`: PostSerializer, CommentSerializer, CategorySerializer, LikeSerializer
- 2 FBV: register/login/logout
- 2+ CBV with APIView: PostListCreateView, PostDetailView, CommentListCreateView, ToggleLikeView
- JWT auth
- Full CRUD for Post
- `request.user` used on create
- CORS configured

## Folder Structure

```text
tiny-social-network/
  backend/
  frontend/
  README.md
  tiny-social-network.postman_collection.json
```

## Backend Run

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

Create categories in shell:
```python
from api.models import Category
for name in ["General", "Confession", "Study", "Fun"]:
    Category.objects.get_or_create(name=name)
exit()
```

Start server:
```bash
python manage.py runserver
```

## Frontend Run

```bash
cd frontend
npm install
npm start
```

Angular app runs on `http://localhost:4200`  
Django API runs on `http://127.0.0.1:8000`

## Main API Endpoints

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET /api/posts/`
- `POST /api/posts/`
- `POST /api/posts/` — body: `{ title, text, category? }` (title and text required)
- `GET /api/posts/{id}/`
- `PUT /api/posts/{id}/`
- `DELETE /api/posts/{id}/`
- `POST /api/posts/{id}/comments/`
- `POST /api/posts/{id}/like/`
- `GET /api/categories/`
- `GET /api/users/{username}/` — public profile with stats (posts, likes received, comments, followers, following, is_following)
- `POST /api/users/{username}/follow/` — toggle follow / unfollow
- `POST /api/profile/avatar/` — multipart upload (field `avatar`) to set current user's avatar
- `DELETE /api/profile/avatar/` — remove current user's avatar

## Defense Tips

Show this order during live demo:
1. Register a user
2. Login
3. Create post
4. Open feed
5. Add comment
6. Like a post
7. Delete your own post
8. Show GitHub repo + Postman collection

## Notes

The original idea had 3 custom models, but the assignment document asks for at least 4 models, so `Category` was added to satisfy the rubric cleanly.
