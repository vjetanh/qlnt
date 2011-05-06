from django.views.generic.list import ListView
from sms.models import sms, smsForm, smsFromExcelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.test.client import Client
import urllib, urllib2
import xlrd

def index(request):
    return render_to_response("sms/index.html", context_instance=RequestContext(request))

def manual_sms(request):
    if request.method == 'POST':
        form = smsForm(request.POST)
        if form.is_valid():
            phone_list = form.cleaned_data.get('phone')
            content = form.cleaned_data.get('content')
            
            phone = phone_list.split(',')
            
            open = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            urllib2.install_opener(open)
            
            para = urllib.urlencode({'u': 'VT_username', 'p': 'VT_password'})
            
#            f = open.open('http://viettelvas.vn:7777/fromcp.asmx', para)
#            f.close();
            
            for p in phone:    
                '''Save to db'''
                s = sms(phone=p, content=content)
                s.save()
                
                '''Send sms via Viettel system'''
                '''Implement Me'''
                data = urllib.urlencode({
                            'RequestID'     : '4',
                            'CPCode'        : '',
                            'UserID'        : '',
                            'ReceiverID'    : p,
                            'ServiceID'     : '',
                            'CommandCode'   : '',
                            'Content'       : content,
                            'ContentType'   : '',
                            })
#                f = open.open('http://viettelvas.vn:7777/fromcp.asmx', data)
            
            return HttpResponseRedirect('/sms/sent_sms/')
    else:
        form = smsForm()    
    t = loader.get_template('sms/manual_sms.html')
    c = RequestContext(request, {'form': form})
    return HttpResponse(t.render(c))

def excel_sms(request):
    if request.method == 'POST':
        form = smsFromExcelForm(request.POST, request.FILES)
        if form.is_valid():
            input_excel = request.FILES['file']
            list = xlrd.open_workbook(file_contents = input_excel.read())            
            sheet = list.sheet_by_index(0)
            
            open = urllib2.build_opener(urllib2.HTTPCookieProcessor())
            urllib2.install_opener(open)
            
            para = urllib.urlencode({'u': 'VT_username', 'p': 'VT_password'})
            
#            f = open.open('http://viettelvas.vn:7777/fromcp.asmx', para)
#            f.close();            
            
            for r in range(1, sheet.nrows):
                '''Save to db'''
                s = sms(phone=sheet.cell_value(r,0), content=sheet.cell_value(r,1))
                s.save() 
                
                '''Send sms via Viettel system'''
                '''Implement Me'''
                data = urllib.urlencode({
                            'RequestID'     : '4',
                            'CPCode'        : '',
                            'UserID'        : '',
                            'ReceiverID'    : sheet.cell_value(r,0),
                            'ServiceID'     : '',
                            'CommandCode'   : '',
                            'Content'       : sheet.cell_value(r,1),
                            'ContentType'   : '',
                            })
#                f = open.open('http://viettelvas.vn:7777/fromcp.asmx', data)
            
        return HttpResponseRedirect('/sms/sent_sms/')
    else:
        form = smsFromExcelForm()
                
    t = loader.get_template('sms/excel_sms.html')
    c = RequestContext(request, {'form': form})
    return HttpResponse(t.render(c))

def handle_uploaded_file(f):
    destination = open()