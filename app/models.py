# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import authenticate

'''
Các mô hình dữ liệu dùng chung giữa các đơn vị trong hệ thống và 
các mô hình dữ liệu cấp Phòng, Sở (ngoài trường phổ thông)
'''

ORGANIZATION_LEVEL_CHOICES = (('T', u'Trường'),
                             ('P', u'Phòng'),
                             ('S', u'Sở')) 
                             
POSITION_CHOICE = (('HOC_SINH',u'Học sinh'), ('GIAO_VU', u'Giáo vụ'), ('GIAO_VIEN',u'Giáo viên'),
                   ('HIEU_PHO',u'Hiệu phó'), ('HIEU_TRUONG', u'Hiệu trưởng'), 
                   ('GIAM_DOC_SO', u'Giám đốc sở'), ('TRUONG_PHONG', u'Trưởng phòng'))

KHOI_CHOICES = (('1', u'Cấp 1'),
                ('2', u'Cấp 2'),
                ('3', u'Cấp 3'))

SCHOOL_ACTION_STATUS=((0, u'Trường mới'),
                      (1, u'Đang học kì 1'), 
                      (2, u'Đang học kì 2'), 
                      (3, u'Đang nghỉ hè'))

CONTACT_CHOICES = (('GY', u'Góp ý xây dựng'),
                   ('HT', u'Hỗ trợ'),
                   ('BL', u'Báo lỗi'),
                   ('LH', 'Liên hệ hợp tác'))
CC_CHOICES = (('True', u'Có'),
              ('False', u'Không'))
class Organization(models.Model):
    ''' Thông tin về sơ đồ tổ chức của các sở, phòng và các trường ''' 
    name = models.CharField(u'Tên tổ chức', max_length = 100) #tên đơn vị. tổ chức 
    level = models.CharField(u"cấp", max_length = 2, choices = ORGANIZATION_LEVEL_CHOICES) #Cấp
    #------- those attributes is used for School only --------------------------------------------------------
    school_level = models.CharField(u"Khối học", max_length = 6, blank = True, null = True, choices = KHOI_CHOICES)
    status = models.SmallIntegerField( max_length = 3, blank = True, null = True, choices = SCHOOL_ACTION_STATUS)
    #---------------------------------------------------------------------------------------------------------
    upper_organization = models.ForeignKey('self', blank = True, null = True, verbose_name = 'Trực thuộc')
    manager_name = models.CharField("Tên thủ trưởng", max_length = 100, null = True)
    address = models.CharField("Địa chỉ", max_length = 255, blank = True, null = True) #
    phone = models.CharField("Điện thoại", max_length = 20, blank = True, null = True)
    email = models.EmailField(max_length = 50, blank = True, null = True)
    user_admin = models.ManyToManyField (User, through = 'Membership')
    class Meta:
        verbose_name_plural = "Tổ chức"
    
    def __unicode__(self):
        return self.name

class Membership (models.Model):
    user_admin = models.ForeignKey(User)
    org = models.ForeignKey(Organization)
    
class OrganizationForm(forms.Form):
    name = forms.CharField(max_length = 100) #tên đơn vị. tổ chức 
    level = forms.CharField(max_length = 2, widget = forms.RadioSelect(choices = ORGANIZATION_LEVEL_CHOICES)) #Cấp
    upper_organization = forms.ModelChoiceField(queryset = Organization.objects.all())    
    address = forms.CharField(max_length = 255) #
    phone = forms.CharField(max_length = 20)
    email = forms.EmailField(max_length = 50)
    
class UserProfile(models.Model):
    '''
    Thông tin về người sủ dụng hệ thống, mở rộng User của Django.
    '''
    user = models.OneToOneField(User, null=True)
    organization = models.ForeignKey(Organization, verbose_name = 'Đơn vị')
    position = models.CharField( choices = POSITION_CHOICE, null = True, blank = True, max_length = 15 )
    phone = models.CharField('Điện thoại di động', max_length = 20, blank = True) #để gửi tin nhắn.
    notes = models.CharField('Ghi chú', max_length = 255, blank = True)
    #TODO permission
    
    def __unicode__(self):
        return self.user.__unicode__()
    
    # @receiver(post_save, sender=User)
    # def create_profile(sender, instance, created, **kwargs):
    #     if created: 
    #         profile, new = UserProfile.objects.get_or_create(user=instance)

class UserForm(forms.ModelForm):
    class Meta:
        model = UserProfile


# quyendt
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Mật khẩu cũ', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Mật khẩu mới', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Nhập lại mật khẩu mới', widget=forms.PasswordInput)
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Xác nhận mật khẩu mới không chính xác. Hãy nhập lại.")
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
    
    def clean_old_password(self):
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Mật khẩu cũ không đúng. Hãy nhập lại.")
        return old_password
ChangePasswordForm.base_fields.keyOrder = ['old_password', 'new_password1', 'new_password2']

# quyendt
class AuthenticationForm(forms.Form):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Please enter a correct username and password. Note that both fields are case-sensitive.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("This account is inactive.")
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                "Your Web browser doesn't appear to have cookies enabled. "
                  "Cookies are required for logging in.")

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
    
class ReportContact(models.Model):
    '''
    Thông tin về các bản báo cáo lỗi hay liên hệ từ khách hàng
    '''
    fullname = models.CharField('Họ và tên', blank=True, null=False, max_length=100)
    email = models.EmailField(max_length = 50, blank = True, null = True)
    phone = models.CharField('Điện thoại', max_length = 20, blank = True, null = True)
    address = models.CharField('Địa chỉ', blank=True, max_length = 255) #
    type = models.CharField('Mục liên hệ', max_length=20, choices=CONTACT_CHOICES)
    content = models.TextField('Nội dung', max_length=3000, blank=True, null=False)


class ContactForm(forms.Form):
    
#Hainhh    
    fullname = forms.CharField(label = 'Họ Tên',max_length=100)
    phone = forms.CharField(label = 'Điện thoại', max_length = 15)
    address = forms.CharField(label = 'Địa chỉ liên hệ', max_length = 255)
    email = forms.EmailField(label = 'Email của bạn')
    type = forms.CharField(label = 'Loại liên hệ', widget = forms.RadioSelect(choices = CONTACT_CHOICES))
    content = forms.CharField(label = 'Nội dung' , widget=forms.Textarea)    

class ResetPassword(models.Model):
#Hainhh
    username = models.CharField(max_length = 50)
    code = models.CharField(max_length = 15)
    
class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label = 'Email của bạn',max_length = 255)
        
    
    
         