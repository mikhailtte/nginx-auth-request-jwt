![Stars](https://img.shields.io/github/stars/mikhailtte/nginx-auth-request-jwt?style=social&color=blue)
![alt text](https://img.shields.io/github/forks/mikhailtte/nginx-auth-request-jwt)
![alt text](https://img.shields.io/github/license/mikhailtte/nginx-auth-request-jwt)
[![Language](https://img.shields.io/badge/Language-Python%203.13-blue)](https://www.python.org/)

# Nginx Authentication via auth_request

### **Returns OK 200 or 401 Unauthorized depending on the authentication result.**

This is an authentication interface, great to use with nginx `auth_request` directive or anything else to protect a specific path, such as `'/'` or `/some`.


## How it works

1. When attempting to access the protected path, the user is prompted to enter their login and password.
2. Upon providing valid credentials, a JWT token is written to the user's cookie and access to the requested path is granted.
3. Each user request undergoes token validation before being redirected to the requested path.
4. If the token has expired, the user is prompted for a refresh token (which has a longer lifespan). After successful signature verification, both tokens are reissued.
5. If both tokens expire (due to prolonged inactivity on the site), the user will need to re-enter their login and password.

## Important Notes

1. **Must be used exclusively with HTTPS**
2. Uses the `pyjwt` library (not `jwt`!)
3. Use in conjunction with IPBan (Windows) or Fail2ban (Linux)

## Features

- bcrypt hashing
- RSA-2048 keys for token signing - generated automatically upon first run.
- Generation and renewal of JWT tokens upon expiration using a refresh token
- Use of HttpOnly Secured Cookies (prevents XSS attacks)


# Installation

* Windows or Linux
* Python 3.13 or Docker
* _nginx (or whatever) + SSL_


## Python
```bash
pip install -r requirements.txt
py add_user.py -n name password
py app.py
```
The first run will generate .config.env and signing keys;
be sure to specify PROTECT_PATH and review other parameters within .config.env.


## Docker
```bash
docker build -t auth:latest .
docker run -d -p 8000:8000 --name auth auth
```
Create users
```bash
docker exec -it auth bash
python add_user.py -n name password
exit
``` 

---
_Give it a star bro ⭐_

[Discussion](https://github.com/mikhailtte/nginx-auth-request-jwt/discussions)
[Repository](https://github.com/mikhailtte/nginx-auth-request-jwt/)
