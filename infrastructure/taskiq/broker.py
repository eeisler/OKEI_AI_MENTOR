from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend, ListRedisScheduleSource

from config.config import Config

cfg = Config.load()

broker = ListQueueBroker(
    url=f"{cfg.redis}/0",
    socket_timeout=None,
    socket_connect_timeout=5,
).with_result_backend(RedisAsyncResultBackend(redis_url=f"{cfg.redis}/1"))

scheduler = TaskiqScheduler(broker, sources=[LabelScheduleSource(broker)])
