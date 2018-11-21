from flask import Flask, request
from flask import render_template

app = Flask(__name__)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print 'This is a POST request'
    else:
        print 'This is a GET request'
    return render_template('layout.html')


if __name__ =='__main__':
    app.run()

