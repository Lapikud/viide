from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
login_manager = LoginManager()
