# Nginx Authentication via auth_request

**Returns HTTP code 200 (OK) or 401 (Unauthorized) depending on the authentication result.**

This is an authentication interface for nginx using the `auth_request` directive. It uses bcrypt for password hashing and RSA-2048 for token signing. This interface can be used to protect a specific path, such as `/some`.

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

1. ```pip install -r requirements.txt```
2. First run will generate `.config.env` and signing keys
```py app.py```
3. Specify `PROTECT_PATH` and review other parameters in `.config.env`
4. ```py app.py```
5. Configure nginx (or another) authentication to use this application.
