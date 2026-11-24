

from dataclasses import dataclass
from datetime import date, timedelta

from application.repositories.user_repository import UserRepository
from domain.entities.user import User


@dataclass
class ResetExpiredStreaksResult:
    checked: int
    reset: int


class ResetExpiredStreaks:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def execute(self):
        today = date.today()
        yesterday = today - timedelta(days=1)

        users: list[User] = await self.user_repo.find_active_streak()
        reset_count = 0

        for user in users:
            last = user.last_activity_date
            if last is None or (last != today and last != yesterday):
                user.current_streak = 0
                await self.user_repo.update(user)

                reset_count += 1

        return ResetExpiredStreaksResult(checked=len(users), reset=reset_count)
