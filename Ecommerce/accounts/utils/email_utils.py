
from django.core.mail import send_mail
from django.conf import settings


def send_verification_email(user):
    code = user.verification_code
    subject = "verifing Account"
    message = f"""
    Hello {user.username}
    Thanks for registering.
    Your verification code is: {code}

    Please enter this code in the app to activate your account.

    Regards,
    Your Team
    """ 
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, email_from, recipient_list)
    
def send_reset_password_code(user):
    code = user.reset_password_code
    
    subject = 'Reset Password Code'
    message = f"""
    hello {user.username}
    reset password code is {code}
    regards
    """
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject,message,email_from,recipient_list)