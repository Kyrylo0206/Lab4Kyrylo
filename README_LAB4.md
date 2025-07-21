# Звіт до лабораторної роботи №4

## 1. Мета роботи
Розробити та впровадити функціональність Function Calling та Model Context Protocol (MCP) сервер з безпекою та guardrails, використовуючи безкоштовні рішення для AI інтеграції.

## 2. Завдання роботи

### Task 1: Function Calling з Google AI Studio
- Реалізувати Function Calling з мінімум 5 функціями для todo API
- **Level 1**: Впровадити guardrails на кількість запитів (50 на сесію)
- **Level 2**: Реалізувати chaining - пошук todo + оновлення/створення в одному запиті
- **Level 3**: Додати захист від prompt injection

### Task 2: Model Context Protocol (MCP) Server (9 балів)
- Створити MCP сервер з 5 tools, 2 resources, 2 prompts
- Впровадити SecurityGuard з rate limiting, input validation, injection protection
- Забезпечити сумісність з MCP Inspector для тестування
- Реалізувати як STDIO так і HTTP варіанти сервера

## 3. Оформлення результатів роботи

### Структура проекту:
```
Lab4Kyrylo/
├── function-calling-client/
│   └── google_function_calling.py    # Google AI Function Calling клієнт
├── server/
│   ├── todo_mcp_server_stdio.py      # STDIO MCP сервер
│   └── todo_mcp_server_http.py       # HTTP MCP сервер
├── simple_todo_server.py             # FastAPI тест сервер
├── test_lab4.py                      # Тести для всіх компонентів
├── requirements.txt                  # Залежності проекту
├── .env                             # Конфігурація (Google API key)
└── README_LAB4.md                   # Документація
```

## 4. Діаграма архітектури

### Function Calling архітектура:
```
[User Input] 
     |
     v
[GuardrailManager] -----> [Request Limiting] + [Injection Detection]
     |                           |                    |
     v                           v                    v
[Google AI Studio] -----> [Function Selection] -----> [TodoAPIClient]
     |                           |                    |
     v                           v                    v
[Response] <------ [Function Execution] <------ [Todo API:8000]
```

### MCP Server архітектура:
```
[MCP Inspector]
     |
     v
[MCP Server:8001] -----> [SecurityGuard] -----> [Rate Limiting]
     |                        |                      |
     v                        v                      v
[5 Tools]              [Input Validation]      [Todo API:8000]
[2 Resources] -----> [Injection Protection] -----> [Response]
[2 Prompts]
```

## 5. Опис коду програми

### Основні компоненти:

#### Function Calling (`google_function_calling.py`):
- **TodoAPIClient** — HTTP клієнт для взаємодії з todo API
- **GuardrailManager** — система безпеки з лімітами запитів та детекцією ін'єкцій
- **Google AI Integration** — використання безкоштовного Google AI Studio
- **5 Functions**: create_todo, get_todos, update_todo, search_todos, delete_todo

#### Test Server (`simple_todo_server.py`):
- **FastAPI Backend** — RESTful API для todo операцій
- **CRUD Operations** — повний функціонал створення, читання, оновлення, видалення
- **Search Functionality** — пошук todo за ключовими словами

## 6. Результати тестування

### Автоматичні тести (`python test_lab4.py`):
```
✅ Level 1: Request limit guardrails implemented
✅ Level 2: Multiple tools with chaining capability  
✅ Level 3: Prompt injection protection
✅ MCP Server: Comprehensive security guardrails
✅ FREE: Uses Google AI Studio (no cost)
```

### Function Calling демонстрація:
- ✅ Створення todo з високим пріоритетом
- ✅ Отримання списку всіх todo
- ✅ Пошук todo за ключовими словами
- ✅ Intelligent chaining: автоматичне створення якщо не знайдено

### MCP Server можливості:
- ✅ 5 secure tools з валідацією
- ✅ 2 resources для доступу до даних
- ✅ 2 prompts для допомоги користувачам
- ✅ Повна сумісність з MCP Inspector
