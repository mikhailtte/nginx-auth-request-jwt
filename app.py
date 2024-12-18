from flask import Flask, redirect, request, render_template, make_response, Response
from time import sleep, time
from storage import db, settings as s, CredentialsModel
import jwt
from crypt import Crypt
import logging

app = Flask(__name__)
_ = Crypt.get_public_key()
logging.basicConfig(
    filename='auth.log', level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)
protected_path = f'/{s.PROTECT_PATH}'

@app.errorhandler(Exception)
def internal_server_error(error):
    return render_template(
        'error.html',
        error_code=error.code,
        message=error.name
    )

@app.route('/validation', methods=['GET'])
def validate_token():
    _401 = make_response(redirect('/authpage')), 401
    token = request.cookies.get('token')
    if not token:
        return _401
    try:
        _ = jwt.decode(
            token,
            Crypt.get_public_key(),
            algorithms=s.ALGORITHM,
            options={"verify_signature": True}
        )
        return make_response(), 200
    except jwt.ExpiredSignatureError as _:
        refresh = request.cookies.get('refresh')
        if not refresh:
            return _401
        try:
            payload = jwt.decode(
                refresh,
                Crypt.get_public_key(),
                algorithms=s.ALGORITHM,
                options={"verify_signature": True}
            )
            response = make_token_response(payload)
            return response
        except Exception as _:
            return _401

@app.route('/validation', methods=['POST'])
def authentication():
    ip = request.headers.get('X-Forwarded-For')
    try:
        validated = CredentialsModel(
            username=request.form.get('username'),
            password=request.form.get('password')
        )
    except ValueError:
        # Для fail2ban/IPban
        logging.warning(
            f'Failed login attempt from {ip} for user invalid_form'
        )
        return make_response(redirect('/authpage')), 401

    username = validated.username
    password = validated.password

    if username and password:
        if db.check_credentials(username, password):
            response = make_token_response({'username': username})
            logging.info(
                f'Successful login from {ip} for user {username}'
            )
            return response
        else:
            logging.warning(
                f'Failed login attempt from {ip} for user {username}'
            )
            sleep(1)
    return make_response(redirect('/authpage')), 401

def make_token_response(payload: dict) -> Response:
    """
    Generates and sets JWT tokens in response cookies
    Return Response object with JWT tokens set in cookies.
    """
    now = int(time())
    try:
        # Generate access token
        payload['exp'] = now + s.TOKEN_EXPIRATION_SECS
        token = jwt.encode(
            payload,
            Crypt.get_private_key(),
            algorithm=s.ALGORITHM
        )

        # рефреш токен
        payload['exp'] = now + s.REFRESH_TOKEN_EXP
        refresh = jwt.encode(
            payload,
            Crypt.get_private_key(),
            algorithm=s.ALGORITHM
        )
    
        # записываем их в куки
        response = make_response()
        response.set_cookie('refresh', refresh, httponly=True, secure=s.SECURE)
        response.set_cookie('token', token, httponly=True, secure=s.SECURE)
        response.status_code = 200
        return response
    except Exception as _:
        print(f'Ошибка генерации ключей: {_}')
        return make_response(redirect('/authpage')), 500


@app.route('/authpage', methods=['GET'])
def authpage():
    return render_template(
        ('login.html'),
        redirect_url=protected_path
    )

@app.route('/', methods=['GET'])
def root():
    return make_response(redirect(protected_path)), 301

if __name__ == '__main__':
    app.run(host=s.HOST, port=s.PORT, debug=False)
