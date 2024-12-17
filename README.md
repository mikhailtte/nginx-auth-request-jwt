![Stars](https://img.shields.io/github/stars/mikhailtte/nginx-auth-request-jwt?style=social&color=blue)
![alt text](https://img.shields.io/github/forks/mikhailtte/nginx-auth-request-jwt)
![alt text](https://img.shields.io/github/license/mikhailtte/nginx-auth-request-jwt)
[![Language](https://img.shields.io/badge/Language-Python%203.13-blue)](https://www.python.org/)

# Nginx Authentication via auth_request

### **Returns OK 200 or 401 Unauthorized depending on the authentication result.**

This is an authentication interface, great to use with nginx `auth_request` directive or anything else to protect a specific path, such as `'/'` or `/some`.


## How it works

- When attempting to access the protected path, the user is prompted to enter their login and password.
- Upon providing valid credentials, a JWT token is written to the user's cookie and access to the requested path is granted.
- Each user request undergoes token validation before being redirected to the requested path.
- If the token has expired, the user is prompted for a refresh token (which has a longer lifespan). After successful signature verification, both tokens are reissued.
- If both tokens expire (due to prolonged inactivity on the site), the user will need to re-enter their login and password.

## Important Notes

- **Must be used exclusively with HTTPS!**
- Uses the `pyjwt` library (not `jwt`!)
- Use in conjunction with IPBan (Windows) or Fail2ban (Linux)

## Features

- bcrypt hashing
- RSA-2048 keys for token signing - generated automatically upon first run.
- Generation and renewal of JWT tokens upon expiration using a refresh token
- Use of HttpOnly Secured Cookies (prevents XSS attacks)

## Installation

Requirements: Python 3.13, nginx + SSL


```
pip install -r requirements.txt
py add_user.py yourname yourpass
py app.py
```
The first run will generate .config.env and signing keys;
be sure to specify PROTECT_PATH and review other parameters within .config.env.

---
If you find this project useful, please give it a star! ⭐

Join the [Discussion](https://github.com/mikhailtte/nginx-auth-request-jwt/discussions)!
