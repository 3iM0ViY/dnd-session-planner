# dnd-session-planner

### Сайт планування днд сесій (а також можливо інших НРІ) для виконання ТЗ Join.IT

<details>
  <summary>Ілюстрації</summary>

  <br/>
  
  <img width="80%" height="auto" alt="image" src="https://github.com/user-attachments/assets/6612e9fb-c8d4-48f7-935b-20c0f2bd1a19" />
  
  <img width="80%" height="auto" alt="image" src="https://github.com/user-attachments/assets/3740b844-a820-4ff5-92dc-fdb779e2d3b1" />
  
  <img width="80%" height="auto" alt="image" src="https://github.com/user-attachments/assets/491b21db-c8d2-4b0e-a261-cb3ad5134c1c" />
  
  <img width="80%" height="auto" alt="image" src="https://github.com/user-attachments/assets/aeeed9b5-1fc1-455a-bec1-dbedebabf15c" />
</details>


---

## Запуск проєкту через Docker

1. Через термінал перейдіть у директорію проєкту, куди завантажили цей репозиторій:

```bash
cd C:\...\dnd-session-planner
```

2. Згенеруйте файл .env з секретним ключем Django. Це потрібно зробити перед збіркою Docker:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())" > backend/.env
```

> Файл `.env` буде створений у папці `backend/` і міститиме змінну `SECRET_KEY`, необхідну для запуску Django.

3. Запустіть Docker Compose для збірки та запуску контейнера:

```bash
docker compose up --build
```

4. Після цього Django сервер буде доступний за адресою:

```
http://127.0.0.1:8000
```
