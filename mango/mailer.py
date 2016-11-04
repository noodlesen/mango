from flask.ext.emails import Message
from flask import render_template

class Mailer():

    def welcome_mail(addr):
        message = Message(html=render_template('email/welcome.html', header="Привет!", text="Добро пожаловать на КУДАБЫ.РУ"),
                  subject="Добро пожаловать!",
                  mail_from=("КУДАБЫ", "info@kudaby.ru"))
        r = message.send(to=(addr))

    def verify_mail(**kwargs):
        message = Message(html=render_template('email/verify_email.html', hash= kwargs['hash'], uid= kwargs['uid']),
                subject="Подтверждение адреса электронной почты",
                mail_from=("КУДАБЫ", "info@kudaby.ru"))
        r = message.send(to=(kwargs['email']))