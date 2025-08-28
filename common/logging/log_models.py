from pydantic import BaseModel


class LogData(BaseModel):
    """
    Данные, для обогащения инфы в логе.

    Эта модель обязательна для передачи в kiq().
    В API находится в api.state.lod_data
    Необходимы для передачи из реквеста данных для проброса.
    """

    client_id: str = ""
    request_id: str = ""
    user: str = ""
    device_id: str = ""
