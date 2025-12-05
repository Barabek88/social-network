# HW 6 WebSocket

### Общая информация

#### 1 Добавлен endpoint WebSocket с аутентификацией через JWT токен

@router.websocket("/post/feed/posted")

файл social-network\app\controllers\websocket_controller.py

#### 2 Добавлен manager для управления соединениями в websocket 

файл social-network\app\core\websocket_manager.py

#### 3 Добавлен клиент rabbitmq

библиотека aio_pika

файл social-network\app\core\rabbitmq_client.py


#### 4 Добавлен Feed Worker

файл social-network\app\services\feed_worker.py


## Поток данных

```
1. User A создает пост
   ↓
2. Сохранение в БД (posts table)
   ↓
3. Получение списка друзей (get_friend_ids)
   ↓
4. Публикация в RabbitMQ для каждого друга
   - Routing Key: user.{friend_id}
   - Exchange: post_feed (TOPIC)
   - Message: {postId, postText, author_user_id}
   ↓
5. RabbitMQ → Queue "feed_updates"
   ↓
6. Feed Worker получает сообщение (push model)
   ↓
7. Worker отправляет через WebSocket
   - ws_manager.send_post_to_user(user_id, post_data)
   ↓
8. Friend B получает обновление в реальном времени
```

---


## Архитектура RabbitMQ

### Connection & Channels
- **1 Connection** - общий для Publisher и Worker
- **2 Channels:**
  - Channel 1: Publisher (отправка сообщений)
  - Channel 2: Worker (получение сообщений)

### Exchange
- **Имя:** `post_feed`
- **Тип:** `TOPIC` (поддержка wildcards: `user.*`)
- **Durable:** `true` (сохраняется при перезапуске)

### Queue
- **Имя:** `feed_updates`
- **Durable:** `true` (сохраняется при перезапуске)
- **Binding:** `user.*` (все routing keys вида `user.{user_id}`)

### Messages
- **Delivery Mode:** `PERSISTENT` (сохраняются на диск)
- **Format:** JSON
```json
{
  "postId": "uuid",
  "postText": "text",
  "author_user_id": "uuid"
}
```

---



## Масштабируемость

### WebSocket сервис (Горизонтальное)

**Команда:**
```bash
docker-compose up -d --scale web=3
```

**Или через docker-compose.yml:**
```yaml
services:
  web:
    deploy:
      replicas: 3
```

**Как работает:**
- 3 независимых инстанса приложения
- Каждый имеет свой набор WebSocket соединений
- RabbitMQ распределяет сообщения между воркерами (round-robin)
- При падении одного инстанса, остальные продолжают работать

### RabbitMQ (Кластер)

**1. Создать кластер (3 ноды):**
```yaml
# docker-compose.rabbitmq-cluster.yml
services:
  rabbitmq1:
    hostname: rabbitmq1
    environment:
      RABBITMQ_ERLANG_COOKIE: 'secret_cookie'
  
  rabbitmq2:
    hostname: rabbitmq2
    command: >
      bash -c "rabbitmq-server & sleep 10 && 
      rabbitmqctl join_cluster rabbit@rabbitmq1"
  
  rabbitmq3:
    hostname: rabbitmq3
    command: >
      bash -c "rabbitmq-server & sleep 10 && 
      rabbitmqctl join_cluster rabbit@rabbitmq1"
```

**2. HA политика (репликация очередей):**
```bash
rabbitmqctl set_policy ha-feed "^post_feed" '{"ha-mode":"all"}'
```
- Реплицирует очереди на **все ноды** кластера
- При падении master ноды, другая автоматически становится master
- Сообщения не теряются

**3. HAProxy (балансировка):**
```yaml
haproxy:
  image: haproxy:alpine
  ports:
    - "5672:5672"
```

```
# haproxy.cfg
backend rabbitmq
    balance roundrobin
    server rmq1 rabbitmq1:5672 check
    server rmq2 rabbitmq2:5672 check
    server rmq3 rabbitmq3:5672 check
```

---