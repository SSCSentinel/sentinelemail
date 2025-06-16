import sys
import os
import json
import hmac
import uuid
from datetime import date, datetime
from PyQt5.QtWidgets import QApplication
from gui import LoginWindow, MainWindow
from trial import load_trial, check_trial
from license import load_license, verify_license
from config import load_config, save_config


def run():
    # Ensure config dir
    home = os.path.expanduser('~/.sentinel')
    os.makedirs(home, exist_ok=True)

    # Trial/license check
    trial = load_trial(home)
    expired = check_trial(trial)
    licensed = False
    if expired:
        licensed = load_license(home) and verify_license(home)
        if not licensed:
            # Prompt license entry
            from ui import LicenseDialog
            dlg = LicenseDialog()
            if not dlg.exec_():
                sys.exit(0)

    # Load user config
    config = load_config(home)
    if not config or not config.get('setup_complete'):
        app = QApplication(sys.argv)
        login = LoginWindow()
        if login.exec_() != LoginWindow.Accepted:
            sys.exit(0)
        save_config(home, login.get_settings())
        config = login.get_settings()

    # Start main UI
    app = QApplication(sys.argv)
    main_win = MainWindow(config)
    main_win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run()