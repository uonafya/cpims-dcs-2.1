from django.db import models
from django.utils import timezone

from cpovc_registry.models import RegPerson
from cpovc_forms.models import OVCCaseRecord


class CTIPMain(models.Model):
    case = models.ForeignKey(OVCCaseRecord, on_delete=models.CASCADE)
    case_number = models.CharField(max_length=10, blank=True)
    case_date = models.DateField()
    country = models.CharField(max_length=2, blank=True)
    person = models.ForeignKey(RegPerson)
    case_status = models.NullBooleanField(null=True, default=None)
    case_stage = models.IntegerField(default=0)
    timestamp_created = models.DateTimeField(default=timezone.now)
    timestamp_updated = models.DateTimeField(default=timezone.now)
    is_void = models.BooleanField(default=False)

    class Meta:
        db_table = 'ovc_ctip_main'
        verbose_name = 'Trafficked Person'
        verbose_name_plural = 'Trafficked Persons'

    def __unicode__(self):
        """To be returned by admin actions."""
        return '%s' % (str(self.case))
