from django import forms
from django.forms.widgets import RadioFieldRenderer
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe

from cpovc_main.functions import get_list


YESNO_CHOICES = get_list('yesno_id')
activity_list = get_list('ctip_activity_id', 'Please Select')
means_list = get_list('ctip_means_id', 'Please Select')
purpose_list = get_list('ctip_purpose_id', 'Please Select')


class RadioCustomRenderer(RadioFieldRenderer):
    """Custom radio button renderer class."""

    def render(self):
        """Renderer override method."""
        return mark_safe(u'%s' % u'\n'.join(

            [u'%s' % force_unicode(w) for w in self]))


class CTIPForm(forms.Form):
    """Counter Trafficking form."""

    is_trafficking = forms.ChoiceField(
        choices=YESNO_CHOICES,
        initial='AYES',
        required=True,
        widget=forms.RadioSelect(
            renderer=RadioCustomRenderer,
            attrs={'id': 'occurence_nationality',
                   'data-parsley-required': 'true',
                   'data-parsley-errors-container': "#trafficking_error"}))

    ctip_activity = forms.ChoiceField(
        choices=activity_list,
        initial='0',
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control',
                   'id': 'ctip_activity',
                   'data-parsley-required': 'true'}))

    ctip_means = forms.ChoiceField(
        choices=means_list,
        initial='0',
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control',
                   'id': 'ctip_means',
                   'data-parsley-required': 'true'}))

    ctip_purpose = forms.ChoiceField(
        choices=purpose_list,
        initial='0',
        required=True,
        widget=forms.Select(
            attrs={'class': 'form-control',
                   'id': 'ctip_purpose',
                   'data-parsley-required': 'true'}))

