import os
from sqlalchemy import *
from flask import Flask, request, render_template, g, redirect, Response, flash, url_for, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from Database import engine
from User import User

conn = engine.connect()

key = 'database'
query = '''
   select j.name as name, v.aname as agency,v.uname as unit, v.sal_from as sfrom, 
           v.sal_to as sto, v.sal_freq as sfreq
   from vacancy as v inner join job as j on v.jid = j.jid
   where j.pre_skl like \'%''' + key + '%\''
print query
cursor = conn.execute(text(query))
print 'hh'
job = []
for row in cursor:
    job.append(row)
print job