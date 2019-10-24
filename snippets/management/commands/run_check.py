from django.core.management.base import  BaseCommand
from django.core.mail import send_mail
from snippets.models import ReMessage
from datetime import datetime, timedelta
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler


def send_mail_note(email, etext):
    send_mail(
        'Django Notice', etext, 'djangodev108@gmail.com',
        email, fail_silently=False
    )
    print('etext')
    return True

def get_message():
    queue = Queue(connection = Redis())
    queryset = ReMessage.objects.all().values_list('dtm', flat=True)
    udtm = []
    for dtm in queryset:
        udtm.append(dtm.timestamp())
    dtm_cur = datetime.now()
    sec = dtm_cur.timestamp() + 3600*7
    job_udtm = []
    for jobs in udtm:
        if (jobs -sec) < 86400 and (jobs -sec)>0:
            job_udtm.append(datetime.utcfromtimestamp(jobs))
    print(job_udtm)
    mail_list = []
    for job in job_udtm:
        queryset = ReMessage.objects.filter(dtm=job)  #.values_list('email', flat=True)
        for item in queryset:
            mail_list.append(item.email)
    notice = queue.enqueue(send_mail_note, mail_list, 'У вас завтра урок')

class Command(BaseCommand):
    sheduler = Scheduler(connection=Redis())

    def check_notice(self):
        dtm = datetime.now()
        self.sheduler.schedule(dtm, get_message, interval=60, repeat=2)

    def handle(self, *args, **kwargs):
        self.check_notice()
        #get_message()
