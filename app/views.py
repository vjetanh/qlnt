from django.http import HttpResponse, HttpResponseRedirect
from app.models import TimeTableForm, SchoolForm, Organization
from app.models import SystemDataTypeForm
from app.models import MarkByPeriodForm
from app.models import UserForm
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.template import Context
from django.template.loader import get_template

def index(request): 
    #template = get_template('index.html')
    #output = template.render(Context({"a":"b",}))
    #return HttpResponse(output)
    return render_to_response("index.html", context_instance=RequestContext(request))

def help(request):
    #template = get_template('index.html')
    #output = template.render(Context({"a":"b",}))
    #return HttpResponse(output)
    return render_to_response("help.html", context_instance=RequestContext(request))

def school_add(request):
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        if form.is_valid():
            org_name = form.cleaned_data['name']
            org_address = form.cleaned_data['address']
            org_phone = form.cleaned_data['phone_number']
            upper_org_id = form.cleaned_data['upper_organization']
            org_upper = None if upper_org_id == '-1' \
                                else Organization.objects.get(pk=upper_org_id)
            org = Organization.objects.create(name=org_name, address=org_address, \
                                    phone_number=org_phone, organization_type='T', \
                                    upper_organization=org_upper)
            org.save()
            return HttpResponseRedirect('/admin/app/organization/')
    else:
        form = SchoolForm()
    t = loader.get_template('app/school/add.html')
    c = RequestContext(request, {'form' : form})
    return HttpResponse(t.render(c))

def school_edit(request):
    pass

def timetable(request):
    template = get_template('app/timetable.html')
    variables = Context({
        'head_title': 'Quan Ly Nha Truong',
        'page_title': 'This is title of timetable page',
        'page_body': 'This is body of timetable page',
    })
    output = template.render(variables)
    return HttpResponse(output)

def time_table_add(request):
    if request.method == 'POST':
        form = TimeTableForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/app/timetable/')
    else:
        form = TimeTableForm()
    t = loader.get_template('app/timetable/add.html')
    c = RequestContext(request, {'form' : form})
    return HttpResponse(t.render(c))

def system_datatype_add(request):
    if request.method == 'POST':
        form = SystemDataTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/app/systemdatatype/')
    else:
        form = SystemDataTypeForm()
    t = loader.get_template('app/systemdatatype/add.html')
    c = RequestContext(request, {'form' : form})
    return HttpResponse(t.render(c))

def mark_by_period_add(request):
    if request.method == 'POST':
        form = MarkByPeriodForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/app/markbyperoid/')
    else:
        form = MarkByPeriodForm()
    t = loader.get_template('app/markbyperiod/add.html')
    c = RequestContext(request, {'form' : form})
    return HttpResponse(t.render(c))

def user_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/app/schoolstaff/')
    else:
        form = UserForm()
    t = loader.get_template('app/schoolstaff/add.html')
    c = RequestContext(request, {'form' : form})
    return HttpResponse(t.render(c))

#------------------------------------------------------------------------------ 
#-------------------------------------------- def sys_value_mark_type(request):
    #---------------------------------------------- if request.method == 'POST':
        #----------------------------- form = SysValueMarkTypeForm(request.POST)
        #--------------------------------------------------- if form.is_valid():
            #------------------------------------------------------- form.save()
            #-------------- return HttpResponseRedirect('app/sysvaluemarktype/')
        #----------------------------------------------------------------- else:
            #------------------------------------- form = SysValueMarkTypeForm()
        #-------------- t = loader.get_template('app/sysvaluemarktype/add.html')
        #-------------------------- c = RequestContext(request, {'form' : form})
        #-------------------------------------- return HttpResponse(t.render(c))
