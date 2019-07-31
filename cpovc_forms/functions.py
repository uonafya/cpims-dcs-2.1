from django.db import connection
from cpovc_registry.functions import (
    get_client_ip, get_meta_data)

from cpovc_main.functions import get_general_list, convert_date
from cpovc_forms.models import (
    FormsAuditTrail, OVCCareF1B, OVCCareEvents, OVCCaseGeo, OVCCaseCategory,
    OVCCaseEventSummon, OVCCaseEventCourt, OVCReferral, OVCCaseEventClosure,
    OVCPlacement, OVCCaseEventServices, OVCEducationFollowUp)
from cpovc_ovc.functions import get_house_hold
from .models import OVCGokBursary


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


def get_case_period(case_date, is_date=False, dfmt='%Y-%m-%d'):
    """Method to get case period."""
    try:
        if is_date:
            a = case_date
        else:
            a = datetime.strptime(case_date, dfmt)
        mon, year = a.month, a.year

        if mon < 7:
            start = '%s-07-01' % (year - 1)
            end = '%s-06-30' % (year)
        else:
            start = '%s-07-01' % (year)
            end = '%s-06-30' % (year + 1)

        print (start, end, year)
    except Exception as e:
        print ('Error -%s' % (str(e)))
        return None, None, None
    else:
        return start, end, year


def get_cases(request):
    """Method to get cases."""
    try:
        cbo_id = request.session.get('ou_primary', 0)
        # cbo_ids = request.session.get('ou_attached', [])
        org_id = int(cbo_id)
        itm_check = True
        if request.user.is_active and request.user.is_superuser:
            org_ids, itm_check = [], False
        else:
            org_ids = get_orgs_child(org_id)
        cs = {}
        case_ids = OVCCaseGeo.objects.filter(
            is_void=False).values_list('case_id_id', flat=True)
        # Transfers
        transfers = OVCCaseEventClosure.objects.filter(
            transfer_to_id__in=org_ids, is_void=False).values_list(
            'case_event_id__case_id_id', flat=True)
        if org_ids or itm_check:
            cids = case_ids.filter(report_orgunit_id__in=org_ids)
            case_ids = []
            for csid in cids:
                case_ids.append(csid)
            for trs in transfers:
                case_ids.append(trs)
        # Case priorities
        casesets = OVCCaseCategory.objects.filter(is_void=False)
        # Other cases
        ocasesets = casesets.filter(is_void=False, case_id_id__in=case_ids)
        cases = ocasesets.order_by('-timestamp_created')[:10]
        risks = ocasesets.values(
            'case_id__risk_level').annotate(dc=Count('case_id__risk_level'))
        status = ocasesets.values(
            'case_id__case_status').annotate(dc=Count('case_id__case_status'))
        # Case load
        ncases = casesets.count()
        ocases = ocasesets.count()
        # Summons
        case_cats = ocasesets.values_list('case_id_id', flat=True)
        summons = OVCCaseEventSummon.objects.filter(
            is_void=False, case_event_id__case_id_id__in=case_cats).values(
            'case_event_id__case_id__risk_level', 'honoured').annotate(
            dc=Count('honoured'))
        smons, fsmons = {}, []
        for summon in summons:
            sname = summon['case_event_id__case_id__risk_level']
            scount = summon['dc']
            shon = summon['honoured']
            if shon not in smons:
                smons[shon] = {'RLHG': 0, 'RLMD': 0, 'RLLW': 0}
                smons[shon][sname] = scount
            else:
                smons[shon][sname] = scount
        for smon in smons:
            s_mon = smons[smon]
            s_mon['name'] = 'Honoured' if smon else 'Not Honoured'
            s_mon['status'] = 'AYES' if smon else 'ANNO'
            fsmons.append(s_mon)
        # Get Court Sessions
        courts = OVCCaseEventCourt.objects.filter(
            is_void=False, case_event_id__case_id_id__in=case_cats).values(
            'case_event_id__case_id__risk_level').annotate(
            dc=Count('court_order'))
        fcourts = create_lists(courts, 'case_event_id__case_id__risk_level',
                               'court_order')
        # Referrals
        referrals = OVCReferral.objects.filter(
            is_void=False, case_id_id__in=case_cats).values(
            'case_id__risk_level').annotate(dc=Count('refferal_to'))
        freferrals = create_lists(referrals, 'case_id__risk_level',
                                  'refferal_to')
        # Transfers
        transfers = OVCCaseEventClosure.objects.filter(
            is_void=False, case_event_id__case_id_id__in=case_cats).values(
            'case_event_id__case_id__risk_level').annotate(
            dc=Count('transfer_to__org_unit_name'))
        ftransfers = create_lists(
            transfers, 'case_event_id__case_id__risk_level',
            'transfer_to__org_unit_name')
        # Institution Placement
        placements = OVCPlacement.objects.filter(
            is_void=False).values(
            'admission_type').annotate(
            dc=Count('admission_type'))
        # Case Interventions
        interventions = OVCCaseEventServices.objects.filter(
            is_void=False, service_provider='EXIT',
            case_event_id__case_id_id__in=case_cats).values(
            'case_event_id__case_id__risk_level').annotate(
            dc=Count('service_provided'))
        finterventions = create_lists(
            interventions, 'case_event_id__case_id__risk_level',
            'service_provided')
        smons, fpls = {}, []
        for summon in placements:
            sname = summon['admission_type']
            scount = summon['dc']
            if sname not in smons:
                smons[sname] = {'RLHG': 0, 'RLMD': 0, 'RLLW': 0}
                smons[sname]['RLHG'] = scount
            else:
                smons[sname]['RLHG'] = scount
        for smon in smons:
            s_mon = smons[smon]
            s_mon['name'] = smon if smon else 'Not Honoured'
            s_mon['status'] = 'AYES' if smon else 'ANNO'
            fpls.append(s_mon)
        print ('intvs', finterventions)
        cs['cases'] = cases
        cs['risks'] = risks
        cs['status'] = status
        cs['ncases'] = ncases
        cs['ocases'] = ocases
        cs['summons'] = fsmons
        cs['courts'] = fcourts
        cs['referrals'] = freferrals
        cs['transfers'] = ftransfers
        cs['placements'] = fpls
        cs['interventions'] = finterventions
        # print (summons)
    except Exception as e:
        print ('Error - %s' % str(e))
        return {'cases': None, 'risks': None, 'status': status,
                'ncases': ncases, 'ocases': ocases}
    else:
        return cs


def create_lists(csets, ctxt, cname):
    try:
        smons, fsmons = {}, []
        for summon in csets:
            sname = str(summon[ctxt])
            scount = summon['dc']
            # shon = 'BLANK' if not s_hon else s_hon
            if sname not in smons:
                smons = {'RLHG': 0, 'RLMD': 0, 'RLLW': 0, 'name': 'Summary'}
            smons[sname] = scount
        if smons:
            fsmons.append(smons)
    except Exception as e:
        print ('Error - %s' % (str(e)))
        return fsmons
    else:
        return fsmons


def save_bursary(request, person_id):
    """Method to save bursary details."""
    try:
        adm_school = request.POST.get('in_school')
        school_id = request.POST.get('school_id')
        county_id = request.POST.get('child_county')
        constituency_id = request.POST.get('child_constituency')
        sub_county = request.POST.get('child_sub_county')
        location = request.POST.get('child_location')
        sub_location = request.POST.get('child_sub_location')
        village = request.POST.get('child_village')
        nearest_school = request.POST.get('nearest_school')
        nearest_worship = request.POST.get('nearest_worship')
        val_in_school = request.POST.get('in_school')
        in_school = True if val_in_school == 'AYES' else False
        school_class = request.POST.get('school_class')
        primary_school = request.POST.get('pri_school_name')
        school_marks = request.POST.get('kcpe_marks')
        father_names = request.POST.get('father_name')
        val_father_alive = request.POST.get('father_alive')
        father_alive = True if val_father_alive == 'AYES' else False
        father_telephone = request.POST.get('father_contact')
        mother_names = request.POST.get('mother_name')
        val_mother_alive = request.POST.get('mother_alive')
        mother_alive = True if val_mother_alive == 'AYES' else False
        mother_telephone = request.POST.get('mother_contact')
        guardian_names = request.POST.get('guardian_name')
        guardian_telephone = request.POST.get('guardian_contact')
        guardian_relation = request.POST.get('guardian_relation')
        val_same_household = request.POST.get('living_with')
        same_household = True if val_same_household == 'AYES' else False
        val_father_chronic_ill = request.POST.get('father_ill')
        father_chronic_ill = True if val_father_chronic_ill == 'AYES' else False
        father_chronic_illness = request.POST.get('father_illness')
        val_father_disabled = request.POST.get('father_disabled')
        father_disabled = True if val_father_disabled == 'AYES' else False
        father_disability = request.POST.get('father_disability')
        val_father_pension = request.POST.get('father_pension')
        father_pension = True if val_father_pension == 'AYES' else False
        father_occupation = request.POST.get('father_occupation')
        val_mother_chronic_ill = request.POST.get('mother_ill')
        mother_chronic_ill = True if val_mother_chronic_ill == 'AYES' else False
        mother_chronic_illness = request.POST.get('mother_illness')
        val_mother_disabled = request.POST.get('mother_disabled')
        mother_disabled = True if val_mother_disabled == 'AYES' else False
        mother_disability = request.POST.get('mother_disability')
        val_mother_pension = request.POST.get('mother_pension')
        mother_pension = True if val_mother_pension == 'AYES' else False
        mother_occupation = request.POST.get('mother_occupation')

        fees_amount = request.POST.get('fees_amount')
        fees_balance = request.POST.get('balance_amount')
        school_secondary = request.POST.get('school_name')
        school_county_id = request.POST.get('school_county')
        school_constituency_id = request.POST.get('school_constituency')
        school_sub_county = request.POST.get('school_sub_county')
        school_location = request.POST.get('school_location')
        school_sub_location = request.POST.get('school_sub_location')
        school_village = request.POST.get('school_village')
        school_email = request.POST.get('school_email')
        school_telephone = request.POST.get('school_telephone')
        school_type = request.POST.get('school_type')
        school_category = request.POST.get('school_category')
        school_enrolled = request.POST.get('school_enrolled')

        school_bank_id = request.POST.get('bank')
        school_bank_branch = request.POST.get('bank_branch')
        school_bank_account = request.POST.get('bank_account')
        school_recommend_by = request.POST.get('recommend_principal')
        school_recommend_date = convert_date(
            request.POST.get('recommend_principal_date'))
        chief_recommend_by = request.POST.get('recommend_chief')
        chief_recommend_date = convert_date(
            request.POST.get('recommend_chief_date'))
        chief_telephone = request.POST.get('chief_telephone')
        csac_approved = request.POST.get('approved_csac')
        approved_amount = request.POST.get('approved_amount')
        scco_name = request.POST.get('scco_name')
        val_scco_signed = request.POST.get('signed_scco')
        scco_signed = True if val_scco_signed == 'AYES' else False
        scco_sign_date = convert_date(request.POST.get('date_signed_scco'))
        csac_chair_name = request.POST.get('csac_chair_name')
        val_csac_signed = request.POST.get('signed_csac')
        csac_signed = True if val_csac_signed == 'AYES' else False
        csac_sign_date = convert_date(request.POST.get('date_signed_csac'))
        application_date = convert_date(request.POST.get('application_date'))
        app_user_id = request.user.id
        ## add missing fields

        nemis = request.POST.get('nemis_no')
        father_idno = request.POST.get('father_id')
        mother_idno = request.POST.get('mother_id')
        year_of_bursary_award = request.POST.get('year_of_bursary_award')
        eligibility_score = request.POST.get('eligibility_scores')
        date_of_issue = request.POST.get('date_of_issue')
        status_of_student = request.POST.get('status_of_student')


        obj, created = OVCEducationFollowUp.objects.get_or_create(
            school_id=school_id, person_id=person_id,
            defaults={'admitted_to_school': adm_school},
        )
        # Save all details from the Bursary form
        gok_bursary = OVCGokBursary(
            person_id=person_id, county_id=county_id,
            constituency_id=constituency_id,
            sub_county=sub_county, location=location,
            sub_location=sub_location, village=village,
            nearest_school=nearest_school,
            nearest_worship=nearest_worship, in_school=in_school,
            school_class=school_class, primary_school=primary_school,
            school_marks=school_marks, father_names=father_names,
            father_alive=father_alive, father_telephone=father_telephone,
            mother_names=mother_names, mother_alive=mother_alive,
            mother_telephone=mother_telephone, guardian_names=guardian_names,
            guardian_telephone=guardian_telephone,
            guardian_relation=guardian_relation, same_household=same_household,
            father_chronic_ill=father_chronic_ill,
            father_chronic_illness=father_chronic_illness,
            father_disabled=father_disabled,
            father_disability=father_disability,
            father_pension=father_pension,
            father_occupation=father_occupation,
            mother_chronic_ill=mother_chronic_ill,
            mother_chronic_illness=mother_chronic_illness,
            mother_disabled=mother_disabled,
            mother_disability=mother_disability,
            mother_pension=mother_pension,
            mother_occupation=mother_occupation,
            fees_amount=fees_amount, fees_balance=fees_balance,
            school_secondary=school_secondary,
            school_county_id=school_county_id,
            school_constituency_id=school_constituency_id,
            school_sub_county=school_sub_county,
            school_location=school_location,
            school_sub_location=school_sub_location,
            school_village=school_village, school_telephone=school_telephone,
            school_email=school_email, school_type=school_type,
            school_category=school_category, school_enrolled=school_enrolled,
            school_bank_id=school_bank_id,
            school_bank_branch=school_bank_branch,
            school_bank_account=school_bank_account,
            school_recommend_by=school_recommend_by,
            school_recommend_date=school_recommend_date,
            chief_recommend_by=chief_recommend_by,
            chief_recommend_date=chief_recommend_date,
            chief_telephone=chief_telephone,
            csac_approved=csac_approved, approved_amount=approved_amount,
            ssco_name=scco_name, scco_signed=scco_signed,
            scco_sign_date=scco_sign_date, csac_chair_name=csac_chair_name,
            csac_signed=csac_signed, csac_sign_date=csac_sign_date,
            app_user_id=app_user_id, application_date=application_date,
            nemis = nemis,
            father_idno = father_idno,
            mother_idno = mother_idno,
            year_of_bursary_award = year_of_bursary_award,
            eligibility_score = eligibility_score,
            date_of_issue = date_of_issue,
            status_of_student = status_of_student)

        gok_bursary.save()
    except Exception as e:
        print 'Error saving bursary - %s' % (str(e))
    else:
        return True
