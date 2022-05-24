class APIAnswerError(Exception):
    """Ошибка при незапланированной работе API.
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message"""
    pass


class HWStatusError(Exception):
    """Недокументированный статус домашнего задания"""
    pass


class ApiRequestError(Exception):
    """ошибка запроса АРI."""
    pass
