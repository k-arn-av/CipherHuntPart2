from datetime import date


# Each clue comes back from the database as a tuple, in table column order:
# (id, user_id, clue_text, key, date_created, is_solved)
ID, USER_ID, CLUE_TEXT, KEY, DATE_CREATED, IS_SOLVED = range(6)


class ClueModel:
    def __init__(self, db):
        self.db = db
        self.current_clue = None

        self.GenerateClue()
        self.FetchNewClue()

    def GenerateClue(self):
        """Adds sample players and clues the first time, so the Vault isn't empty."""
        if self.db.fetchone("SELECT COUNT(*) FROM clues")[0] > 0:
            return

        samples = [
            ("eagle_coder", "eagle_coder@usm.edu", "I point at things but have no finger. Dereference me carelessly and your program falls over.", "pointer"),
            ("null_pointer", "null_pointer@usm.edu", "Last in, first out is the only rule I follow.", "stack"),
            ("eagle_coder", "eagle_coder@usm.edu", "I go round and round until a condition breaks me.", "loop"),
            ("null_pointer", "null_pointer@usm.edu", "I remember every version of your code but never write a line myself.", "git"),
            ("eagle_coder", "eagle_coder@usm.edu", "I have keys but open no locks, and a space but no room.", "keyboard"),
        ]

        for username, email, clue_text, key in samples:
            self.db.execute(
                "INSERT OR IGNORE INTO users (username, email) VALUES (?, ?)",
                (username, email),
            )
            user_id = self.db.fetchone("SELECT id FROM users WHERE username = ?", (username,))[0]
            self.AddClue(clue_text, key, user_id)

    def GetCurrentClue(self):
        """Returns the clue on screen right now, or None if there are no unsolved clues."""
        return self.current_clue

    def FetchNewClue(self):
        """Picks a random unsolved clue and makes it the current one."""
        self.current_clue = self.db.fetchone(
            "SELECT * FROM clues WHERE is_solved = 0 ORDER BY RANDOM() LIMIT 1"
        )
        return self.current_clue

    def GetClueUsername(self):
        """Returns the username of whoever wrote the current clue."""
        if self.current_clue is None:
            return None
        row = self.db.fetchone(
            "SELECT username FROM users WHERE id = ?", (self.current_clue[USER_ID],)
        )
        return row[0] if row else None

    def AddClue(self, clue_text, key, user_id):
        """Saves a new clue and returns its id."""
        return self.db.execute(
            "INSERT INTO clues (user_id, clue_text, key, date_created) VALUES (?, ?, ?, ?)",
            (user_id, clue_text, key, date.today().isoformat()),
        )

    def AttemptCurrentClueSolve(self, key):
        """Returns True and marks the clue solved if the key matches, ignoring capitals and spaces."""
        if self.current_clue is None:
            return False
        if key.strip().lower() != self.current_clue[KEY].strip().lower():
            return False

        self.db.execute("UPDATE clues SET is_solved = 1 WHERE id = ?", (self.current_clue[ID],))
        return True

    def GetUnsolvedClues(self):
        """Returns every clue that hasn't been solved yet."""
        return self.db.fetchall("SELECT * FROM clues WHERE is_solved = 0")


if __name__ == "__main__":
    from database import Database

    db = Database(":memory:")
    clues = ClueModel(db)

    print("Unsolved clues:", len(clues.GetUnsolvedClues()))
    current = clues.GetCurrentClue()
    print("Current clue:", current[CLUE_TEXT], "| by", clues.GetClueUsername())

    print("Wrong guess:", clues.AttemptCurrentClueSolve("banana"))
    print("Right guess:", clues.AttemptCurrentClueSolve("  " + current[KEY].upper() + " "))
    print("Unsolved clues:", len(clues.GetUnsolvedClues()))

    user_id = db.fetchone("SELECT id FROM users WHERE username = ?", ("eagle_coder",))[0]
    new_id = clues.AddClue("What has hands but can't clap?", "clock", user_id)
    print("Added clue", new_id, "| unsolved clues:", len(clues.GetUnsolvedClues()))

    for clue in clues.GetUnsolvedClues():
        clues.current_clue = clue
        clues.AttemptCurrentClueSolve(clue[KEY])
    print("All solved, FetchNewClue() returns:", clues.FetchNewClue())
