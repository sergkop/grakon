# -*- coding:utf-8 -*-
from time import sleep

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Send emails to all activated users."

    def handle(self, *args, **options):
        from services.email import send_email

        with open('/home/serg/gn1.txt') as f:
            emails = [line.strip() for line in f]

        for email in emails:
            print email
            send_email(None, u'Приглашение к участнию в новой площадке Гракон',
                    'letters/gn_invitation.html', {}, 'gn_invitation', 'noreply', to_email=email)
            sleep(0.2)
