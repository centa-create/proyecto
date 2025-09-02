
from flask_login import UserMixin
from app import db
import enum

class UserRole(enum.Enum):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'

class Users(db.Model, UserMixin):
    """
    Modelo de usuario para la autenticación y gestión de cuentas.
    Las contraseñas deben almacenarse siempre hasheadas.
    """
    __tablename__ = 'user'
    idUser = db.Column(db.Integer, primary_key=True)
    nameUser = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwordUser = db.Column(db.String(128), nullable=False)  # hash
    birthdate = db.Column(db.Date, nullable=False)
    is_active_db = db.Column(db.Boolean, default=False)  # Solo tras verificación
    verification_token = db.Column(db.String(128), nullable=True)
    token_expiry = db.Column(db.DateTime, nullable=True)  # Expiración para recuperación de contraseña
    accepted_terms = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    profile_pic = db.Column(db.String(255), nullable=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    wishlist_token = db.Column(db.String(32), unique=True, nullable=True)

    is_blocked = db.Column(db.Boolean, default=False)  # Nuevo campo: usuario bloqueado

    def get_id(self):
        """Obtener el ID del usuario para Flask-Login."""
        return str(self.idUser)

    def is_authenticated(self):
        """Siempre retorna True, requerido por Flask-Login."""
        return True

    @property
    def is_active(self):
        """Retorna True si el usuario está activo y no está bloqueado."""
        return not self.is_blocked and self.is_active_db

    def set_password(self, password):
        """Hashea y almacena la contraseña del usuario."""
        import bcrypt
        self.passwordUser = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verifica si la contraseña coincide con el hash almacenado."""
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), self.passwordUser.encode('utf-8'))