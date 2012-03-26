# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from tinymce.models import HTMLField

class Profile(models.Model):
    user = models.OneToOneField(User)
    username = models.CharField(max_length=30)
    first_name = models.CharField(u'Имя', max_length=40)
    last_name = models.CharField(u'Фамилия', max_length=40,
            help_text=u'<b>Мы не будем показывать ваше настоящее имя другим пользователям без вашего разрешения.</b>')
    #middle_name = models.CharField(u'Отчество', max_length=30, blank=True, default='')
    show_name = models.BooleanField(u'Показывать настоящее имя', default=False,
            help_text=u'<b>Поставьте эту галку, чтобы другие пользователи видели ваше настоящее имя</b>' \
                    u' (к участникам, открывающим свое имя, больше доверия на площадке)')
    about = HTMLField(u'О себе', default='', blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', [self.username])

    def __unicode__(self):
        if self.show_name and self.first_name and self.last_name:
            return u'%s %s (%s)' % (self.first_name, self.last_name, self.username)
        return self.username

def create_profile(sender, **kwargs):
    if kwargs.get('created', False):
        profile = Profile()
        profile.user = kwargs['instance']
        profile.username = profile.user.username
        profile.save()

models.signals.post_save.connect(create_profile, sender=User)
