from functools import wraps
from flask import session, redirect, url_for, abort
from models import Usuario

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        usuario_id = session.get('usuario_id')
        if not usuario_id:
            return redirect(url_for('login'))

        usuario = Usuario.query.get(usuario_id)
        if not usuario or not usuario.is_admin:
            abort(403)  # Proibido
        return f(*args, **kwargs)
    return decorated_function