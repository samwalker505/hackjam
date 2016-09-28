import logging
import md5
import time

import jwt

import common.micro_webapp2 as micro_webapp2
from handlers import BaseHanler
from common.constants import Error
from models.user import User
from models.email import Email
import secret
app = micro_webapp2.WSGIApplication()

def gen_token(user):
    payload = {
        'id': user.key.id(),
        'ts': time.time()
    }
    return jwt.encode(payload, secret.secret, algorithm='HS256')

@app.api('/tokens')
class TokensHandler(BaseHanler):
    def post(self):
        email = self.json_body.get('email')
        password = self.json_body.get('password')
        if not email or not password:
            return self.res_error(Error.NO_EMAIL_PASSWORD)

        email_log = Email.get_by_id(email)
        if email_log.owner:
            user = email_log.owner.get()
            if md5.new(password).hexdigest() != user.password:
                return self.res_error(Error.INVALID_PASSWORD, status=403)
            token = gen_token(user)
            d = user.to_dict()
            d['access_token'] = token
            return self.res_json(d)
        else:
            return self.res_error(Error.NO_USER)