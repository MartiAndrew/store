```python
import uuid
from pydantic import BaseModel
from common.rabbitmq.vector_producer import VectorProducer
from common.rabbitmq.producer import BaseProducer, RabbitPublisher


class Message(BaseModel):
    uuid: uuid.UUID
    first: str

    class Config:
        json_encoders = {
            uuid.UUID: lambda unique_id: unique_id.hex,
        }


class ExampleProducer(BaseProducer):
    publisher = RabbitPublisher(url="amqp://guest:guest@localhost:5672/", exchange="example_exchange")


async def main():
    msg = Message(uuid=uuid.uuid4(), first="first")
    vector_producer = VectorProducer("amqp://guest:guest@localhost:5672/")
    example_producer = ExampleProducer()
    await vector_producer.publish_to_exchange("vector-test", msg)
    await example_producer.publish_to_exchange("example-test", msg)
```
