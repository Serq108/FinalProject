from django.core.mail import send_mail


def send_mail_note(email, etext):
    send_mail(
        'Django Notice', etext, 'djangodev108@gmail.com',
        email, fail_silently=False
    )
    print('etext')
    return True

def send_mail_note1(email, etext, header):
    send_mail(
        header, etext, 'djangodev108@gmail.com',
        email, fail_silently=False
    )
    print('etext1')
    return True

def test_job(smstr):
   f = open('per.txt','w')
   print(smstr)
   f.write(smstr)
   f.close()

def testjob():
   print('Shabba')


def send_mail_reg(email, url):
    send_mail(
        'Activation on Django', url, 'djangodev108@gmail.com',
        email, fail_silently=False
        )
    print('url')
    return True
