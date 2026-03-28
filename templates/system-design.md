# System Design

**Проект:** [Название проекта]
**Версия:** [Номер версии]
**Дата:** [YYYY-MM-DD]
**Автор:** Architect

---

## Связь с ADR

Данный документ является графической иллюстрацией архитектурных решений, описанных в:
- [docs/architecture/ADR.md](../architecture/ADR.md)

---

## C4 Model

### Level 1: System Context

```mermaid
graph TB
    User[Пользователь] --> System[Система]
    System --> ExternalAPI[Внешние API]
```

**Описание:**
[Кто использует систему, с чем она интегрируется]

---

### Level 2: Containers

```mermaid
graph TB
    subgraph "Система"
        Frontend[Web App<br/>React]
        Mobile[Mobile App<br/>React Native]
        API[API Server<br/>Node.js]
        DB[(Database<br/>PostgreSQL)]
        Cache[(Cache<br/>Redis)]
    end
    
    User --> Frontend
    User --> Mobile
    Frontend --> API
    Mobile --> API
    API --> DB
    API --> Cache
```

**Описание контейнеров:**

| Контейнер | Технология | Назначение |
|-----------|-----------|------------|
| Web App | React | Веб-интерфейс |
| Mobile App | React Native | Мобильное приложение |
| API Server | Node.js | Бэкенд, бизнес-логика |
| Database | PostgreSQL | Хранение данных |
| Cache | Redis | Кэширование |

---

### Level 3: Components

```mermaid
graph TB
    subgraph "API Server"
        Auth[Auth Module]
        Users[Users Module]
        Products[Products Module]
        Orders[Orders Module]
    end
    
    Auth --> DB[(Database)]
    Users --> DB
    Products --> DB
    Orders --> DB
```

**Описание компонентов:**

| Компонент | Модуль | Назначение |
|-----------|--------|------------|
| Auth | auth | Аутентификация, авторизация |
| Users | users | Управление пользователями |
| Products | products | Каталог продуктов |
| Orders | orders | Заказы |

---

## ER-диаграмма

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER {
        uuid id PK
        string email
        string password_hash
        datetime created_at
    }
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER {
        uuid id PK
        uuid user_id FK
        string status
        decimal total
        datetime created_at
    }
    ORDER_ITEM }|--|| PRODUCT : includes
    ORDER_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
        decimal price
    }
    PRODUCT {
        uuid id PK
        string name
        string description
        decimal price
    }
```

---

## API Design

### Обзор эндпоинтов

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /auth/login | Аутентификация |
| POST | /auth/register | Регистрация |
| GET | /users/me | Профиль пользователя |
| GET | /products | Список продуктов |
| GET | /products/:id | Детали продукта |
| POST | /orders | Создать заказ |
| GET | /orders | Список заказов |

### OpenAPI спецификация

Полная спецификация API: [docs/api/openapi.yaml](../api/openapi.yaml)

---

## Changelog

| Дата | Изменение | Автор |
|------|-----------|-------|
| YYYY-MM-DD | Initial version | Architect |
