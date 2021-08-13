from .models import CTIPMain


def handle_ctip(request, action, params={}):
    """Method to handle CTiP"""
    try:
        if action == 0:
            save_case(request, params)
    except Exception as e:
        print('Error saving TIP Action %s' % (str(e)))
    else:
        return True


def save_case(request, params):
    """Method to save Main case data."""
    try:
        case_id = params['case_id']
        person_id = params['person_id']
        case_date = params['case_date']
        obj, created = CTIPMain.objects.update_or_create(
            case_id=case_id,
            defaults={'case_date': case_date, 'person_id': person_id},
        )
    except Exception as e:
        print('Error saving TIP %s' % (str(e)))
    else:
        return True
