class BaseError(Exception):
    pass

class DataBaseError(BaseError):
    def __init__(self, message: str, **context):
        self.context = context
        self.message = message
        super().__init__(f"DATA BASE ERROR:{self.message} - {self.context}")
    

class NoDataError(DataBaseError):
    def __init__(self, **context):
        super().__init__("NO DATA ERROR", **context)


class DataBaseConnectionError(DataBaseError):
    pass

class DataBaseCommitError(DataBaseError):
    pass

class RollbackError(DataBaseError):
    pass

class ObjectNotFound(DataBaseError):
    pass

class SessionNotFoundError(BaseError):
    def __init__(self, session_id):
        pass