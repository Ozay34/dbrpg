from data.db import db
from ui.root import root


if __name__ == "__main__":
    try:
        root.mainloop()
    finally:
        db.close()
