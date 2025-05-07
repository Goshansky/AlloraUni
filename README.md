# API Маркетплейса E-Commerce

Backend на FastAPI для маркетплейса электронной коммерции, аналогичного Ozon, с использованием PostgreSQL, SQLAlchemy ORM, Pydantic и JWT аутентификации.

## Функциональность

- Аутентификация пользователей с JWT (регистрация, вход, обновление токена)
- Управление товарами с категориями
- Корзина покупок
- Обработка заказов
- Отзывы о товарах
- Избранное/список желаний
- Эндпоинты администратора для управления товарами и категориями

## Технологии

- FastAPI - Веб-фреймворк
- PostgreSQL - База данных
- SQLAlchemy - ORM
- Alembic - Миграции базы данных
- Pydantic - Валидация данных
- Passlib + Bcrypt - Хеширование паролей
- Python-jose - JWT токены
- Uvicorn - ASGI сервер

## Структура проекта

```
.
├── alembic.ini                  # Конфигурация Alembic
├── migrations/                  # Миграции Alembic
├── requirements.txt             # Зависимости проекта
├── app/
│   ├── api/                     # API маршруты
│   │   ├── deps/                # Зависимости для API маршрутов
│   │   └── endpoints/           # Эндпоинты API
│   ├── core/                    # Основной функционал
│   │   ├── config.py            # Конфигурация проекта
│   │   └── security.py          # Утилиты безопасности
│   ├── db/                      # Настройка базы данных
│   │   └── base.py              # Подключение к базе данных
│   ├── models/                  # Модели SQLAlchemy
│   ├── schemas/                 # Схемы Pydantic
│   ├── services/                # Сервисы бизнес-логики
│   └── main.py                  # Настройка приложения FastAPI
```

## Начало работы

### Предварительные требования

- Python 3.9+
- Docker и Docker Compose

### Установка

1. Клонировать репозиторий

2. Создать и активировать виртуальное окружение
   ```bash
   python -m venv venv
   source venv/bin/activate  # В Windows: venv\Scripts\activate
   ```

3. Установить зависимости
   ```bash
   pip install -r requirements.txt
   ```

4. Создать файл `.env` на основе примера
   ```bash
   cp env.txt .env
   ```

5. Запустить базу данных через Docker
   ```bash
   docker-compose up -d
   ```

6. Выполнить миграции
   ```bash
   alembic upgrade head
   ```

7. Запустить приложение
   ```bash
   uvicorn app.main:app --reload
   ```

8. Открыть браузер и перейти по адресу http://localhost:8000/docs для просмотра документации API

## Эндпоинты API

### Аутентификация

- `POST /api/register` - Зарегистрировать нового пользователя
- `POST /api/login` - Вход с JWT
- `GET /api/profile` - Получить профиль текущего пользователя
- `PUT /api/profile` - Обновить профиль текущего пользователя

### Товары

- `GET /api/products` - Список товаров
- `GET /api/products/{id}` - Детали товара
- `POST /api/products` - Создать товар (только админ)
- `PUT /api/products/{id}` - Обновить товар (только админ)
- `DELETE /api/products/{id}` - Удалить товар (только админ)

### Категории

- `GET /api/categories` - Список категорий
- `GET /api/categories/{id}` - Детали категории
- `GET /api/categories/{id}/products` - Товары в категории
- `POST /api/categories` - Создать категорию (только админ)
- `PUT /api/categories/{id}` - Обновить категорию (только админ)
- `DELETE /api/categories/{id}` - Удалить категорию (только админ)

### Корзина

- `GET /api/cart` - Получить содержимое корзины
- `POST /api/cart/add` - Добавить товар в корзину
- `POST /api/cart/remove` - Удалить товар из корзины
- `POST /api/cart/clear` - Очистить корзину

### Заказы

- `POST /api/orders` - Создать заказ из корзины
- `GET /api/orders` - Список заказов пользователя
- `GET /api/orders/{id}` - Детали заказа
- `PUT /api/orders/{id}` - Обновить статус заказа (только админ)

### Отзывы

- `GET /api/reviews/{product_id}` - Получить отзывы о товаре
- `POST /api/reviews/{product_id}` - Создать отзыв о товаре
- `DELETE /api/reviews/{product_id}` - Удалить отзыв пользователя о товаре

### Избранное

- `GET /api/favorites` - Получить список избранного пользователя
- `POST /api/favorites/{product_id}` - Добавить товар в избранное
- `DELETE /api/favorites/{product_id}` - Удалить товар из избранного
