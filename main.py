import os

from core.storage import load_ideas, ensure_data_file
from ui.main_window import MainWindow


DATA_FILE = "data/ideas.json"
DEMO_FILE = "data/ideas_demo.json"


def bootstrap_data():
    ensure_data_file(DATA_FILE)

    ideas = load_ideas(DATA_FILE)

    if not ideas and os.path.exists(DEMO_FILE):
        ideas = load_ideas(DEMO_FILE)

    return ideas


if __name__ == "__main__":
    ideas = bootstrap_data()
    app = MainWindow(ideas)
    app.mainloop()