# Scoring API

Scoring API - это простой скоринговый сервис на основе HTTP с проверкой запросов и декларативными описаниями.  
Пользователи взаимодействуют с API, отправляя **POST** запросы со структурированной **JSON полезной нагрузкой**.

---

## Установка

1. Клонируйте репозиторий

```sh
git clone https://github.com/therealalexmois/scoring-api.git
cd scoring-api
```

2. Установите зависимости с помощью Poetry

```sh
poetry install
```

## Запуск API

```sh
make start
```

или в ручную:

```sh
python -m scoring_api.server
```

## Запуск тестов

Выполнить все тесты

```sh
make test
```

или

```sh
pytest
```

Запуск интеграционных тестов с помощью Docker

```sh
pytest tests/integration --docker-compose tests/docker/docker-compose.yml
```

## Использование Memcached в Docker

Запустите Memcached

```sh
docker run --rm -d --name memcached -p 11211:11211 memcached:latest
```

Проверьте, запущен ли Memcached

```sh
echo "stats" | nc localhost 11211
```

## Обзор API

Структура запроса

Все запросы API должны отправляться в виде POST-запросов к конечной точке /method с полезной нагрузкой в формате JSON.

```json
{
  "account": "<partner company name>",
  "login": "<username>",
  "method": "<method name>",
  "token": "<authentication token>",
  "arguments": { <dictionary with method arguments> }
}
```

| Поле      | Тип    | Требуется | Описаине                                         |
|-----------|--------|-----------|--------------------------------------------------|
| account   | string | ❌        | Необязательное название компании-партнера.       |
| login     | string | ❌        | Имя пользователя.                                |
| method    | string | ✅        | Имя метода API.                                  |
| token     | string | ✅        | Токен аутентификации.                            |
| arguments | dict   | ✅        | Словарь с аргументами метода.                    |

## Методы API

### online_score

Возвращает оценку, основанную на информации о пользователе.

#### Аргументы

| Поле       | Тип       | Обязательное | Валидация                                      |
|------------|----------|--------------|------------------------------------------------|
| phone      | строка/число | ❌ | 11-значное число, начинающееся с `7`.         |
| email      | строка   | ❌ | Должен содержать `@`.                          |
| first_name | строка   | ❌ | \-                                             |
| last_name  | строка   | ❌ | \-                                             |
| birthday   | строка   | ❌ | Формат `DD.MM.YYYY`, возраст не более 70 лет.  |
| gender     | число    | ❌ | Должно быть `0, 1 или 2`.                      |

Валидация: Должна быть указана хотя бы одна пара из следующих данных:
- (phone, email)
- (first_name, last_name)
- (gender, birthday)

#### Ответ

Успех

```json
{ "code": 200, "response": { "score": <number> } }
```

Если пользователь является администратором, то всегда возвращается значение 42:

```json
{ "code": 200, "response": { "score": 42 } }
```

Ошибка валидации

```sh
{ "code": 422, "error": "<Invalid field details>" }
```

#### Пример запроса

```sh
curl -X POST -H "Content-Type: application/json" -d '
{
  "account": "horns&hoofs",
  "login": "h&f",
  "method": "online_score",
  "token": "55cc9ce545bcd144300fe9efc28e...",
  "arguments": {
    "phone": "79175002040",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "birthday": "01.01.1990",
    "gender": 1
  }
}' http://127.0.0.1:8080/method/
```

#### Пример ответа

```json
{ "code": 200, "response": { "score": 5.0 } }
```

### clients_interests

Возвращает список интересов для заданных идентификаторов клиентов.

#### Аргументы

| Поле       | Тип           | Обязательное | Валидация                  |
|------------|--------------|--------------|----------------------------|
| client_ids | список [int] | ✅           | Не должно быть пустым.     |
| date       | строка       | ❌           | Формат `DD.MM.YYYY`.       |

#### Ответ

Успех

```json
{ "code": 200, "response": { "1": ["books", "hi-tech"], "2": ["pets", "tv"] } }
```

Ошибка валидации

```json
{ "code": 422, "error": "<Invalid field details>" }
```

#### Пример запроса

```sh
curl -X POST -H "Content-Type: application/json" -d '
{
  "account": "horns&hoofs",
  "login": "admin",
  "method": "clients_interests",
  "token": "d3573aff1555cd67dccf21b95fe8c...",
  "arguments": {
    "client_ids": [1, 2, 3, 4],
    "date": "07.20.2017"
  }
}' http://127.0.0.1:8080/method/
```

#### Пример ответа

```json
{ "code": 200, "response": { "1": ["books", "hi-tech"], "2": ["pets", "tv"] } }
```
