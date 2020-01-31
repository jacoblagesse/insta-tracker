from .models import User

def get_full_data(username):
    user = User.objects.get(_username=username)
    user.get_followers()
    user.get_followees()
    user.send_email()