# NYC Job Search Web-app
Designed by Chenyu Xi(cx2219) and Zhihan Bu(zb2244)
## Environment
- Python 2.7
- Packages:  
```
pip install flask psycopg2 sqlalchemy click flask-login
```
## Files
- Server.py: Run to start the Server (please add --threaded)
- Database.py: Create Database engine
- User.py: Define user class, used for Flask-login (No ORM)
- happy: virtualenv happy for server
- templates: html files
- static: css theme

## Reference:
- css file based on https://github.com/payoung/flask-sqlalchemy-login-manager-template
- We rewrite login function
