import json
import redis

redis_client = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

ad_id = "7221277157"
ad_data = redis_client.get(ad_id)

if ad_data:
    details = json.loads(ad_data)  # Преобразуем JSON-строку обратно в словарь
    print(details)
