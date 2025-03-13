import logging
from urllib.parse import unquote

from django.db.models.signals import post_save
from django.dispatch import receiver

from starlink.models import Publication
from starlink.tasks import send_publication

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Publication)
def after_publication_create(sender, instance, created, **kwargs):
    if created:
        logger.info(f'Publication id={instance.pk} was created')
        send_publication.delay(
            instance.text,
            unquote(instance.media.url.lstrip('/'))
            if instance.media else None,
        )
