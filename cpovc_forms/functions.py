from django.db import connection
from cpovc_registry.functions import (
    get_client_ip, get_meta_data)

from cpovc_main.functions import get_general_list, convert_date
from cpovc_forms.models import (
    FormsAuditTrail, OVCCareF1B, OVCCareEvents, OVCCaseGeo)
from cpovc_ovc.functions import get_house_hold


def get_case_geo(request, case_id):
    """Get case details."""
    try:
        case_geo = OVCCaseGeo.objects.get(case_id=case_id, is_void=False)
    except Exception as e:
        print 'error getting case geo - %s' % (str(e))
        return None
    else:
        return case_geo


def save_audit_trail(request, params, audit_type):
    """Method to save audit trail depending on transaction."""
    try:
        user_id = request.user.id
        ip_address = get_client_ip(request)
        form_id = params['form_id']
        form_type_id = audit_type
        transaction_type_id = params['transaction_type_id']
        interface_id = params['interface_id']
        meta_data = get_meta_data(request)

        print 'Audit Trail', params

        FormsAuditTrail(
            transaction_type_id=transaction_type_id,
            interface_id=interface_id,
            # timestamp_modified=None,
            form_id=form_id,
            form_type_id=form_type_id,
            ip_address=ip_address,
            meta_data=meta_data,
            app_user_id=user_id).save()

    except Exception, e:
        print 'Error saving audit - %s' % (str(e))
        pass
    else:
        pass


def create_fields(field_name=[], default_txt=False):
    """Method to create fields from tools."""
    dict_val = {}
    try:
        my_list = get_general_list(field_names=field_name)
        all_list = my_list.values(
            'item_id', 'item_description_short', 'item_description',
            'item_sub_category')
        for value in all_list:
            item_id = value['item_description_short']
            item_cat = value['item_sub_category']
            item_details = value['item_description']
            items = {'id': item_id, 'name': item_details}
            if item_cat not in dict_val:
                dict_val[item_cat] = [items]
            else:
                dict_val[item_cat].append(items)
    except Exception, e:
        error = 'Error getting list - %s' % (str(e))
        print error
        return {}
    else:
        return dict_val


def create_form_fields(data):
    """Method to create fields."""
    try:
        print data
        dms = {'HG': ['1a', '1s'], 'SC': ['2a', '2s'], 'PG': ['3a', '3s'],
               'PSG': ['4a', '4s'], 'EG': ['5a', '5s'], 'HE': ['6a', '6s']}
        domains = {'HG': {}, 'SC': {}, 'PG': {}, 'PSG': {}, 'EG': {}, 'HE': {}}
        for domain in domains:
            itds = dms[domain]
            for itm in itds:
                itd = itm[-1:]
                if itm in data:
                    domains[domain][itd] = data[itm]
                else:
                    domains[domain][itd] = []
    except Exception as e:
        print 'error with domains - %s' % (str(e))
        return {}
    else:
        return domains


def save_form1b(request, person_id, edit=0):
    """Method to save form 1B."""
    try:
        user_id = request.user.id
        domains = {'SC': 'DSHC', 'PS': 'DPSS', 'PG': 'DPRO',
                   'HE': 'DHES', 'HG': 'DHNU', 'EG': 'DEDU'}
        if edit:
            print 'F1B edit'
        else:
            f1b_date = request.POST.get('olmis_service_date')
            caretaker_id = request.POST.get('caretaker_id')
            f1bs = request.POST.getlist('f1b[]')
            print 'save', f1b_date, f1bs
            hh = get_house_hold(caretaker_id)
            hhid = hh.id if hh else None
            event_date = convert_date(f1b_date)
            newev = OVCCareEvents(
                event_type_id='FM1B', created_by=user_id,
                person_id=caretaker_id, house_hold_id=hhid,
                date_of_event=event_date)
            newev.save()
            # Attach services
            for f1bitm in f1bs:
                f1b = str(f1bitm)
                did = f1b[:2]
                domain = domains[did]
                OVCCareF1B(event_id=newev.pk, domain=domain,
                           entity=f1b).save()

    except Exception as e:
        print 'error saving form 1B - %s' % (str(e))
        return None
    else:
        return True


def get_person_ids(request, name):
    """Method to get persons."""
    try:
        pids = []
        names = name.split()
        query = ("SELECT id FROM reg_person WHERE to_tsvector"
                 "(first_name || ' ' || surname || ' '"
                 " || COALESCE(other_names,''))"
                 " @@ to_tsquery('english', '%s') AND is_void=False"
                 " ORDER BY date_of_birth DESC")
        # " OFFSET 10 LIMIT 10")
        vals = ' & '.join(names)
        sql = query % (vals)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchall()
            pids = [r[0] for r in row]
    except Exception as e:
        print ('Error getting results - %s' % (str(e)))
        return []
    else:
        return pids
