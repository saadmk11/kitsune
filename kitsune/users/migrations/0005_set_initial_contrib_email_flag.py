# -*- coding: utf-8 -*-
"""
Set the `first_{revision,question}_email_sent` flags for existing users, to
avoid back filling welcome emails to contributors.
"""
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations
from django.db.models import F


def contrib_email_flags_forwards(apps, schema_editor):
    Profile = apps.get_model('users', 'Profile')
    Answer = apps.get_model('questions', 'Answer')
    Revision = apps.get_model('wiki', 'Revision')

    l10n_contributor_ids = set(
        Revision.objects
        .exclude(document__locale='en-US')
        .values_list('creator', flat=True))
    (Profile.objects
        .filter(user__id__in=l10n_contributor_ids)
        .update(first_l10n_email_sent=True))

    answer_contributor_ids = set(
        Answer.objects
        .exclude(question__creator=F('creator'))
        .values_list('creator', flat=True))
    (Profile.objects
        .filter(user__id__in=answer_contributor_ids)
        .update(first_answer_email_sent=True))


def contrib_email_flags_backwards(apps, schema_editor):
    Profile = apps.get_model('users', 'Profile')
    Profile.objects.all().update(first_l10n_email_sent=False, first_answer_email_sent=False)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_add_contrib_email_flags'),
        ('wiki', '0001_initial'),
        ('questions', '0001_initial'),
        ('auth', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(contrib_email_flags_forwards, contrib_email_flags_backwards),
    ]
