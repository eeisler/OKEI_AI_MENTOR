import asyncio
import logging
import sys

from application.interactors.reset_expired_streaks import ResetExpiredStreaks
from infrastructure.database.connection import async_session_factory
from infrastructure.repositories.postgres_user_repository import AsyncPostgresUserRepository
from infrastructure.taskiq.broker import broker, cfg
from infrastructure.dependency_fabrics import get_container
# import infrastructure.taskiq.tasks.tasks
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger = logging.getLogger(__name__)

@broker.task(
    task_name="streaks.reset_expired_streaks",
    schedule=[{"cron": "*/1 * * * *"}],
)
async def reset_expired_streaks(user_id: int | None = None) -> dict:
    logger.info("reset_expired_streaks started, user_id=%s", user_id)

    async with async_session_factory() as session:
        repo = AsyncPostgresUserRepository(session)
        interactor = ResetExpiredStreaks(repo)
        result = await interactor.execute()
        await session.commit()  

    logger.info("done: checked=%s reset=%s", result.checked, result.reset)
    return {"checked": result.checked, "reset": result.reset}

@broker.task(
    task_name="study.generate_daily_student_tasks",
    schedule=[{
        "cron": f"{cfg.task_generation_minute} {cfg.task_generation_hour} * * *",
        "cron_offset": cfg.task_generation_timezone,
    }],
)
async def generate_daily_student_tasks(user_id: int | None = None) -> dict:
    logger.info("generate_daily_student_tasks started, user_id=%s", user_id)

    if user_id is not None:
        student_ids = [user_id]
    else:
        async with async_session_factory() as session:
            repo = AsyncPostgresUserRepository(session)
            students = await repo.find_active_students()
        student_ids = [student.id for student in students]

    container = get_container()
    ok = 0
    failed = 0

    for student_id in student_ids:
        try:
            async with async_session_factory() as session:
                use_case = await container.get_start_skill_session(db=session)
                await use_case.execute(student_id)
            ok += 1
        except Exception:
            failed += 1
            logger.exception("task generation failed for user_id=%s", student_id)

    logger.info("done: total=%s ok=%s failed=%s", len(student_ids), ok, failed)
    return {"total": len(student_ids), "ok": ok, "failed": failed}