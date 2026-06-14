import datetime as dt
import random
import sqlite3
from pathlib import Path


class DailyCompanion:
    def __init__(self, db_path: str = "jarvis_memory.db"):
        self.db_path = Path(db_path)
        self._create_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    is_done INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def add_task(self, content: str, category: str = "general") -> str:
        clean = content.strip()
        if not clean:
            return "Πες μου ποια εργασία να προσθέσω."

        with self._connect() as connection:
            connection.execute(
                "INSERT INTO tasks (content, category) VALUES (?, ?)",
                (clean, category),
            )
        return f"Το πρόσθεσα στη λίστα σου: {clean}"

    def list_tasks(self) -> list[str]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, content, category FROM tasks WHERE is_done = 0 ORDER BY created_at ASC"
            ).fetchall()
        return [f"{task_id}. [{category}] {content}" for task_id, content, category in rows]

    def complete_task(self, task_id_text: str) -> str:
        try:
            task_id = int(task_id_text.strip())
        except ValueError:
            return "Δώσε αριθμό εργασίας. Παράδειγμα: done 2"

        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE tasks SET is_done = 1 WHERE id = ?",
                (task_id,),
            )
        if cursor.rowcount == 0:
            return "Δεν βρήκα εργασία με αυτόν τον αριθμό."
        return "Το σημείωσα ως ολοκληρωμένο. Μπράβο για την πρόοδο."

    def encouragement(self) -> str:
        messages = [
            "Welcome back, beautiful intelligent human. Πάμε να χτίσουμε μια ήρεμη και δυνατή μέρα.",
            "Καλημέρα Παναγιώτα. Δεν χρειάζεται να τα κάνεις όλα τέλεια, μόνο να ξεκινήσεις σωστά.",
            "Welcome back. Έχεις μυαλό, δύναμη και δυνατότητες. Σήμερα πάμε βήμα βήμα.",
            "Καλημέρα. Μικρή πρόοδος σήμερα, μεγάλη διαφορά αύριο.",
            "Welcome back. Systems ready, confidence loading, discipline online.",
            "Καλημέρα. Σήμερα διάλεξε μία μικρή νίκη και ξεκίνα από εκεί.",
            "Welcome back. Your future self will thank you for one focused hour today.",
            "Καλημέρα. Μια δύσκολη μέρα δεν ακυρώνει την αξία ή την πρόοδό σου.",
            "Welcome back, brilliant human. Let us make today useful, not perfect.",
            "Καλημέρα. Είσαι πιο ικανή από όσο νιώθεις στις κουραστικές μέρες.",
        ]
        return random.choice(messages)

    def practical_tip(self) -> str:
        tips = [
            "Tip: Ξεκίνα με την πιο μικρή εργασία. Η πρώτη ολοκλήρωση δίνει ώθηση.",
            "Tip: Αν έχεις ρούχα, βάλε πλυντήριο πριν ξεκινήσεις διάβασμα. Θα δουλεύει όσο εσύ προχωράς.",
            "Tip: Βάλε χρονόμετρο 25 λεπτών και κάνε μόνο ένα πράγμα.",
            "Tip: Πριν βγεις, έλεγξε κινητό, κλειδιά, πορτοφόλι και νερό.",
            "Tip: Αν το σπίτι φαίνεται χάος, κάνε μόνο 10 λεπτά συμμάζεμα. Αρκεί για να αλλάξει η ενέργεια του χώρου.",
            "Tip: Γράψε τις τρεις βασικές δουλειές της ημέρας και άσε τα υπόλοιπα ως bonus.",
            "Tip: Πιες νερό πριν ξεκινήσεις. Η συγκέντρωση πέφτει γρήγορα όταν είσαι αφυδατωμένη.",
            "Tip: Ξεκίνα το διάβασμα με επανάληψη 5 λεπτών από χθες.",
            "Tip: Άνοιξε μόνο τα προγράμματα που χρειάζεσαι. Λιγότερο χάος στην οθόνη, περισσότερη συγκέντρωση.",
            "Tip: Αν κάτι παίρνει λιγότερο από δύο λεπτά, κάν' το τώρα.",
        ]
        return random.choice(tips)

    def daily_lesson(self) -> str:
        lessons = [
            "Daily lesson: Η επανάληψη σε αραιά χρονικά διαστήματα βοηθά τη μακροπρόθεσμη μνήμη.",
            "Daily lesson: Τα νευρωνικά δίκτυα μαθαίνουν μειώνοντας σταδιακά το σφάλμα πρόβλεψης.",
            "Daily lesson: Η ανάκληση από μνήμη είναι πιο αποτελεσματική από το απλό ξαναδιάβασμα.",
            "Daily lesson: Η τεχνική Pomodoro μειώνει το γνωστικό φορτίο και βοηθά στη συγκέντρωση.",
            "Daily lesson: Ο εγκέφαλος μαθαίνει καλύτερα όταν συνδυάζεις θεωρία, παράδειγμα και εφαρμογή.",
            "Daily lesson: Η συνέπεια νικά το κίνητρο, γιατί το κίνητρο αλλάζει ενώ η συνήθεια μένει.",
            "Daily lesson: Στον προγραμματισμό, το debugging είναι διαδικασία σκέψης, όχι αποτυχία.",
            "Daily lesson: Ένα καθαρό γραφείο μειώνει τους περισπασμούς και βοηθά την εκτελεστική λειτουργία.",
            "Daily lesson: Η τεχνητή νοημοσύνη δεν είναι μαγεία· είναι στατιστική, δεδομένα και βελτιστοποίηση.",
            "Daily lesson: Για δύσκολα μαθήματα, προσπάθησε να εξηγήσεις την έννοια σαν να τη διδάσκεις σε φίλο.",
        ]
        return random.choice(lessons)

    def evening_reflection(self) -> str:
        return (
            "Evening reflection:\n"
            "1. Τι ολοκλήρωσες σήμερα;\n"
            "2. Τι σε δυσκόλεψε;\n"
            "3. Ποιο είναι το πιο σημαντικό βήμα για αύριο;\n"
            "Μην ξεχνάς: η πρόοδος μετράει περισσότερο από την τελειότητα."
        )

    def study_mode(self) -> str:
        return (
            "Study mentor mode:\n"
            "Διάλεξε ένα θέμα και θα το σπάσουμε σε θεωρία, παράδειγμα, βασικούς όρους και πιθανές ερωτήσεις εξεταστικής."
        )

    def home_mode(self) -> str:
        return (
            "Home organizer mode:\n"
            "Πρόταση: ξεκίνα με ρούχα, σκουπίδια ή γραφείο. Διάλεξε μόνο ένα για τα επόμενα 10 λεπτά."
        )

    def briefing(self) -> str:
        now = dt.datetime.now()
        tasks = self.list_tasks()
        if tasks:
            task_text = "Σήμερα έχεις:\n" + "\n".join(f"- {task}" for task in tasks[:8])
        else:
            task_text = "Δεν έχεις ανοιχτές εργασίες αυτή τη στιγμή. Μπορούμε να προσθέσουμε μία μικρή δουλειά για αρχή."

        return (
            f"{self.encouragement()}\n\n"
            f"Ώρα: {now.strftime('%H:%M')}\n"
            f"Ημερομηνία: {now.strftime('%d/%m/%Y')}\n\n"
            f"{task_text}\n\n"
            f"{self.practical_tip()}\n\n"
            f"{self.daily_lesson()}"
        )
