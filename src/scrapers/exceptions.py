class TimeoutException(Exception):
    def __init__(
        self,
        timeout: int = 0,
        message: str = "Timed out waiting {timeout}s for page to load",
    ):
        self.timeout = timeout
        super().__init__(message.format(timeout=timeout))
