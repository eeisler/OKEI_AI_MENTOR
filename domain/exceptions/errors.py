class DomainError(Exception):
    pass

class UserNotFound(DomainError):
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(f'User {self.user_id} not found')