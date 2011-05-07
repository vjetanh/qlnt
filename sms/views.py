# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from sms.models import sms, smsForm, smsFromExcelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
import urllib, urllib2
import xlrd, xlwt
import os.path

TEMP_FILE_LOCATION = os.path.join(os.path.dirname(__file__), 'uploaded')
EXPORTED_FILE_LOCATION = os.path.join(os.path.dirname(__file__), 'exported')

def index(request):
    return render_to_response("sms/index.html", context_instance=RequestContext(request))

def manual_sms(request):
    if request.method == 'POST':
        form = smsForm(request.POST)
        if form.is_valid():
            phone_list = form.cleaned_data.get('phone')
            content = form.cleaned_data.get('content')
            
            phone = []
            for p1 in phone_list.split(','):
                p1 = p1.split(';')
                for p2 in p1:
                    p2 = p2.split()
                    for p3 in p2:
                        phone.append(p3)
                    
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

def save_file(file):
    saved_file = open(os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls'), 'wb+')
    for chunk in file.chunks():
        saved_file.write(chunk)
    saved_file.close()
    return 'sms_input.xls'

def upload_excel(request):
    if request.method == 'POST':
        form = smsFromExcelForm(request.POST, request.FILES)
        if form.is_valid():
            save_file(request.FILES['file'])
            return HttpResponseRedirect('/sms/preview_sms/')
    else:
        form = smsFromExcelForm()
                
    t = loader.get_template('sms/excel_sms.html')
    c = RequestContext(request, {'form': form})
    return HttpResponse(t.render(c))
        
def preview_sms(request):
    if request.method == 'POST':
        filepath = os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')
        list = xlrd.open_workbook(filepath)
        sheet = list.sheet_by_index(0)
            
        open = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(open)
            
        para = urllib.urlencode({'u': 'VT_username', 'p': 'VT_password'})
            
#        f = open.open('http://viettelvas.vn:7777/fromcp.asmx', para)
#        f.close();            
        for r in range(1, sheet.nrows):
            '''Save to db'''
            s = sms(phone=sheet.cell_value(r,0), content=sheet.cell_value(r,1))
            s.save() 
                
            '''Send sms via Viettel system'''
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
#            f = open.open('http://viettelvas.vn:7777/fromcp.asmx', data)
            
        os.remove(filepath)
        return HttpResponseRedirect('/sms/sent_sms/')
    else:                
        filepath = os.path.join(TEMP_FILE_LOCATION, 'sms_input.xls')
        list = xlrd.open_workbook(filepath)            
        sheet = list.sheet_by_index(0)
        data = []
        for r in range(0, sheet.nrows):
            data.append({
                        'number': sheet.cell_value(r,0),
                        'content': sheet.cell_value(r,1)
                        })
        t = loader.get_template('sms/preview_sms.html')
        c = RequestContext(request, {'data' : data})
        return HttpResponse(t.render(c))

def export_excel(request):
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment; filename=Thống kê tin nhắn.xls'
    
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Thống kê tin nhắn')
    
    queryset=sms.objects.all()
    
    ws.write(0, 0, 'Số điện thoại người nhận')
    ws.write(0, 1, 'Nội dung tin nhắn')
    begin = 1;
    for q in queryset:
        ws.write(begin, 0, q.phone)
        ws.write(begin, 1, q.content)
        begin = begin+1
    
    wb.save(response)
    return response