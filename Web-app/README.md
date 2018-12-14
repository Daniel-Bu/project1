# NYC Job Search Web-app
Designed by Chenyu Xi(cx2219) and Zhihan Bu(zb2244)

Current URL: http://35.196.200.113:8111 (already dead)

**No security features have been enabled**
## Environment:
- Python 2.7
- Packages:  
```
pip install flask psycopg2 sqlalchemy click flask-login
```
## Files:
- Server.py: Run to start the Server (please add --threaded)
- Database.py: Create Database engine
- User.py: Define user class, used for Flask-login (No ORM)
- happy: virtualenv happy for server
- templates: html files
- static: css theme

## Functions:
- User / Admin login system
- User:
  - Search vacancies with keywords
  - Apply for vacancies
  - See website statistics
- Admin:
  - Insert a job or vacancy
  - Delete a job or vacancy
## Reference:
- css file based on https://github.com/payoung/flask-sqlalchemy-login-manager-template/tree/master/static
- We rewrite login function
