import datetime as dt
import random

from assistant.daily_companion import DailyCompanion
from assistant.focus import FocusManager
from assistant.weather import WeatherService


class CareCoach:
    def __init__(self):
        self.daily = DailyCompanion()
        self.focus = FocusManager()
        self.weather = WeatherService()

    def care_mode(self) -> str:
        return (
            "Care mode is active. I will help you choose the next small useful step.\n\n"
            f"{self.plan_now()}"
        )

    def plan_day(self) -> str:
        tasks = self.daily.list_tasks()
        weather = self.weather.summary()
        now = dt.datetime.now()

        if tasks:
            first_task = tasks[0]
            task_block = "Your open tasks:\n" + "\n".join(f"- {task}" for task in tasks[:5])
        else:
            first_task = "choose one small task and add it to your list"
            task_block = "You do not have open tasks yet. Add one small task so we can start."

        return (
            "Here is your gentle plan for today:\n\n"
            f"Time: {now.strftime('%H:%M')}\n"
            f"{weather}\n\n"
            f"{task_block}\n\n"
            "Recommended order:\n"
            "1. Drink water and reset your space for 5 minutes.\n"
            f"2. Start with: {first_task}\n"
            "3. Do one 25-minute focus session.\n"
            "4. Take a short break.\n"
            "5. Then we choose the next step together.\n\n"
            "You do not need to do everything at once. Just start with the first small action."
        )

    def plan_now(self) -> str:
        tasks = self.daily.list_tasks()
        focus_status = self.focus.status()

        if "No focus session" not in focus_status:
            return (
                f"You are already in focus mode. {focus_status}\n"
                "Stay with this task. Do not switch tabs unless you need them for the work."
            )

        if tasks:
            return (
                "Do this now:\n"
                f"1. Start with this task: {tasks[0]}\n"
                "2. Set a 25-minute focus session.\n"
                "3. Put your phone away if you can.\n"
                "4. When you finish, tell me: end focus\n\n"
                "I am here. Start small and keep going."
            )

        suggestions = [
            "Put laundry in first, then come back to study.",
            "Clear your desk for 5 minutes, then start a focus session.",
            "Open your study material and read only the first page.",
            "Write down the one thing that would make today feel successful.",
            "Start with water, fresh air, and one simple task.",
        ]
        return (
            "You do not have a task selected yet. Here is what I suggest:\n"
            f"1. {random.choice(suggestions)}\n"
            "2. Add one task with: add task task name\n"
            "3. Then say: start focus task name\n\n"
            "We are not trying to fix the whole day. We are only starting it."
        )

    def home_reset(self) -> str:
        return (
            "Home reset plan:\n"
            "1. Start laundry if needed.\n"
            "2. Throw away visible trash.\n"
            "3. Clear only your desk or bed, not the whole room.\n"
            "4. Put dishes in one place.\n"
            "5. Stop after 10 minutes unless you feel good to continue.\n\n"
            "A small reset is enough to change the feeling of the room."
        )

    def study_push(self) -> str:
        return (
            "Study push:\n"
            "1. Choose one topic only.\n"
            "2. Read for 10 minutes.\n"
            "3. Close the material and explain it out loud.\n"
            "4. Write 3 questions that could appear in an exam.\n"
            "5. Start a focus session so I can track it.\n\n"
            "The goal is not perfect studying. The goal is active studying."
        )
