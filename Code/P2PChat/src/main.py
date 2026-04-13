import sys
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from gui.validation import validate_port
from gui import ChatApp


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ok, port, err = validate_port(sys.argv[1])
        if not ok:
            print(f"❌ {err}")
            print("Cách dùng: python main.py [port]")
            sys.exit(1)
        if err:
            print(err)
    else:
        port = 12000

    app = ChatApp(port)
    app.mainloop()