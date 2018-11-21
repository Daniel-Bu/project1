from sqlalchemy import *
from flask_login import  UserMixin
#
DB_USER = "zb2244"
DB_PASSWORD = "hx2jsr9w"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_SERVER + "/w4111"
engine = create_engine(DATABASEURI)
conn = engine.connect()

# user implementation:
# Set secret Key


class User(UserMixin):

    # set database
    def __init__(self, email='', password='', name=''):
        UserMixin.__init__(self)
        self.email = email
        self.name = name
        self.password = password
        self.valid = False
        self.id = ''

    def user_verify(self):
        eid = self.email
        code = self.password
        query = '''select * from usr where email like\''''+eid+'\''
        cursor = conn.execute(query)
        for row in cursor:
            key = str(row.password)
            if key.strip() == code.strip():
                self.name = str(row.name)
                self.email = eid
                self.id = eid
                self.valid = True
            break

    def insert_new_user(self):
        try:
            query= '''
            insert into usr (email,name,password)
            values (%s,%s,%s)'''
            conn.execute(query, (self.email, self.name, self.password))
            self.valid = True
        except:
            print 'invalid user'

    def is_authenticated(self):
        if self.valid:
            return True
        return False

    def is_active(self):
        return True

    def get_id(self):
        return self.id
