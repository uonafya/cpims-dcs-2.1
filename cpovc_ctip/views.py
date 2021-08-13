from django.shortcuts import render
from .models import CTIPMain


def ctip_home(request):
    '''
    Some default page for forms home page
    '''
    try:
        # form = OVCSearchForm(initial={'person_type': 'TBVC'})
        cases = CTIPMain.objects.filter(is_void=False)
        return render(request, 'ctip/home.html',
                      {'status': 200, 'cases': cases})
    except Exception as e:
        raise e


def view_ctip_case(request, id):
    '''
    Some default page for forms home page
    '''
    try:
        # form = OVCSearchForm(initial={'person_type': 'TBVC'})
        cases = CTIPMain.objects.filter(is_void=False)
        return render(request, 'ctip/home.html',
                      {'status': 200, 'cases': cases})
    except Exception as e:
        raise e
