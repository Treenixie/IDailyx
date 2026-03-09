import os
import sys

from core.idea_manager import IdeaManager
from core.storage import load_ideas, ensure_data_file


DATA_FILE = "data/ideas.json"
DEMO_FILE = "data/ideas_demo.json"


def configure_tk_environment():
    if "TCL_LIBRARY" in os.environ and "TK_LIBRARY" in os.environ:
        return

    tcl_root = os.path.join(sys.base_prefix, "tcl")

    if not os.path.isdir(tcl_root):
        return

    tcl_dir = None
    tk_dir = None

    for folder_name in os.listdir(tcl_root):
        full_path = os.path.join(tcl_root, folder_name)

        if not os.path.isdir(full_path):
            continue

        if folder_name.startswith("tcl8"):
            tcl_dir = full_path
        elif folder_name.startswith("tk8"):
            tk_dir = full_path

    if tcl_dir:
        os.environ["TCL_LIBRARY"] = tcl_dir

    if tk_dir:
        os.environ["TK_LIBRARY"] = tk_dir


configure_tk_environment()

from ui.main_window import MainWindow


def bootstrap_data():
    ensure_data_file(DATA_FILE)

    ideas = load_ideas(DATA_FILE)

    if not ideas and os.path.exists(DEMO_FILE):
        ideas = load_ideas(DEMO_FILE)

    return ideas


if __name__ == "__main__":
    ideas = bootstrap_data()
    manager = IdeaManager(ideas)

    app = MainWindow(manager, DATA_FILE)
    app.mainloop()