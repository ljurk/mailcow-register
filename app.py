import random
import string
import json
from os import getenv
from flask import Flask, render_template, request, redirect
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import redis
from json2table import convert
from forms.ui import Ui, Admin


app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET303"
app.config['JSON_SORT_KEYS'] = False
auth = HTTPBasicAuth()

users = {"admin": generate_password_hash(getenv("ADMIN_PASSWORD"))}

sess = requests.Session()
sess.headers.update({'X-API-Key': getenv('API_TOKEN')})

db_invitations = redis.Redis(host=getenv('REDIS_HOST'), port=getenv('REDIS_PORT'), db=0)
db_expiredInvitations = redis.Redis(host=getenv('REDIS_HOST'), port=getenv('REDIS_PORT'), db=1)

def getRandomString(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def getArg(key):
    return request.args.get(key) if request.args.get(key) else request.form.get(key)

def getRegistrationUrl(username, token, text='registration link'):
    return  f"<a href='http://localhost:5000/?username={username}&token={token}'> {text} </a>"

def getUrl(resource):
    return getenv('MAILCOW_HOST') + getenv('MAILCOW_API_PATH') + resource

def getInvitationData(redis):
    returnData = []
    for invitation in redis.keys():
        data = json.loads(redis.get(invitation))
        data['user'] = invitation.decode()
        data['url']  = getRegistrationUrl(invitation.decode(), data['token'])
        del data['token']
        returnData.append(data)

    if len(returnData) == 1: # add empty row so json2table will convert consistent
        emptyDict = data.copy()
        for key in emptyDict.keys():
            emptyDict[key] = ''
        returnData.append(emptyDict)
    return returnData

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route('/admin', methods=['GET', 'POST'])
@auth.login_required
def getAdmin():
    form = Admin()
    form.token.data = getRandomString(int(getenv('REGISTER_DEFAULT_TOKEN_LENGTH')))

    if form.validate_on_submit():
        data = {
                 "token": form.token.data,
                 "active": "1",
                 "domain": form.domain.data,
                 "local_part": form.username.data,
                 "quota": str(form.quota.data),
                 "force_pw_update": "0",
                 "tls_enforce_in": int(form.tlsIn.data),
                 "tls_enforce_out": int(form.tlsOut.data)
               }
        db_invitations.set(form.username.data, json.dumps(data))
        # redirect to admin so you can reload the page without the warning "You will post data again"
        return redirect("/admin")

    currentUsers = sess.get(getUrl('/get/mailbox/all')).json()
    output = {'activeUsers': [x['username'] for x in currentUsers],
              'invitations': getInvitationData(db_invitations),
              'expired': getInvitationData(db_expiredInvitations)}

    return render_template('index.html', url=getenv('MAILCOW_HOST'), form=form, table=convert(output), admin=True)

@app.route('/', methods=['GET', 'POST'])
def getIndex():
    form = Ui()
    # check username
    if getArg('username') not in [x.decode() for x in db_invitations.keys()]:
        return "user invalid", 401

    userData = json.loads(db_invitations.get(getArg('username')))

    # check token
    if getArg('token') != userData['token']:
        return "token invalid", 401

    form.username.data = getArg('username')
    if form.validate_on_submit():
        data = {
                 "local_part": form.username.data,
                 "name": "Full name",
                 "password": form.password.data,
                 "password2": form.password.data,
               } | userData


        requestData=sess.post(getUrl("add/mailbox"), json=data).json()[0]
        form.message = f"[{ requestData['type'] }] { requestData['msg'][0] }"
        if requestData['type'] == 'success':
            # remove element from invitations and add it to expired Invitations
            db_expiredInvitations.set(getArg('username'), json.dumps(data))
            db_invitations.delete(getArg('username'))

    return render_template('index.html', form=form, url=getenv('MAILCOW_HOST'), user=True)


# Run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
