# -*- coding: utf-8 -*-
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from ConfigParser import SafeConfigParser
import os
import codecs
from django.conf import settings
from datetime import date
SCHOOL_SETTING_FOLDER = settings.SCHOOL_SETTING_FOLDER

ORGANIZATION_LEVEL_CHOICES = (('T', u'Trường'),
                              ('P', u'Phòng'),
                              ('S', u'Sở'))

POSITION_CHOICE = (('HOC_SINH', u'Học sinh'), ('GIAO_VU', u'Giáo vụ'), ('GIAO_VIEN', u'Giáo viên'),
                   ('HIEU_PHO', u'Hiệu phó'), ('HIEU_TRUONG', u'Hiệu trưởng'),
                   ('GIAM_DOC_SO', u'Giám đốc sở'), ('TRUONG_PHONG', u'Trưởng phòng'))

KHOI_CHOICES = (('2', u'Cấp 2'),
                ('3', u'Cấp 3'))

SCHOOL_ACTION_STATUS = ((0, u'Trường mới'),
                        (1, u'Đang học kì 1'),
                        (2, u'Đang học kì 2'),
                        (3, u'Đang nghỉ hè'))
TINH_CHOICES = (('1',u'An Giang'),('2',u'Bà Rịa-Vũng Tàu'),('3',u'Bạc Liêu'),('4',u'Bắc Cạn'),('5',u'Bắc Giang'),
    ('6',u'Bắc Ninh'),('7',u'Bến Tre'),('8',u'Bình Dương'),('9',u'Bình Định'),('10',u'Bình Phước'),('11',u'Bình Thuận'),
    ('12',u'Cà Mau'),('13',u'Cao Bằng'),('14',u'Cần Thơ'),('15',u'Đà Nẵng'),('16',u'Đắk Lắk'),('17',u'Đắk Nông'),
    ('18',u'Điện Biên'),('19',u'Đồng Nai'),('20',u'Đồng Tháp'),('21',u'Gia Lai'),('22',u'Hà Giang'),('23',u'Hà Nam'),
    ('24',u'Hà Nội'),('25',u'Hà Tĩnh'),('26',u'Hải Dương'),('27',u'Hải Phòng'),('28',u'Hòa Bình'),('29',u'Hồ Chí Minh'),
    ('30',u'Hậu Giang'),('31',u'Hưng Yên'),('32',u'Khánh Hòa'),('33',u'Kiên Giang'),('34',u'Kom Tum'),('35',u'Lai Châu'),
    ('36',u'Lào Cai'),('37',u'Lạng Sơn'),('38',u'Lâm Đồng'),('39',u'Long An'),('40',u'Nam Định'),('41',u'Nghệ An'),
    ('42',u'Ninh Bình'),('43',u'Ninh Thuận'),('44',u'Phú Thọ'),('45',u'Phú Yên'),('46',u'Quảng Bình'),('47',u'Quảng Nam'),
    ('48',u'Quảng Ngãi'),('49',u'Quảng Ninh'),('50',u'Quảng Trị'),('51',u'Sóc Trăng'),('52',u'Sơn La'),('53',u'Tây Ninh'),
    ('54',u'Thái Bình'),('55',u'Thái Nguyên'),('56',u'Thanh Hóa'),('57',u'Thừa Thiên-Huế'),('58',u'Tiền Giang'),
    ('59',u'Trà Vinh'),('60',u'Tuyên Quang'),('61',u'Vĩnh Long'),('62',u'Vĩnh Phúc'),('63',u'Yên Bái'))

REGISTER_STATUS_CHOICES = (('DA_CAP', u"Đã cấp"), ('CHUA_CAP', u"Chưa cấp"))

SEMESTER_STATUS = [u'Chưa thiết lập', u'Học kì I', u'Học kì II', u'Học kì hè']


class MyConfigParser(SafeConfigParser):
    def write(self, fp):
        for section in self._sections:
            print section
            fp.write("[%s]\n" % section)
            for (key, value) in self._sections[section].items():
                print '..', key, value
                if key == "__name__":
                    continue
                if (value is not None) or (self._optcre == self.OPTCRE):
                    key = " = ".join((key, unicode(value).replace('\n', '\n\t')))
                fp.write("%s\n" % key)
            fp.write("\n")


class Organization(models.Model):
    """ Thông tin về sơ đồ tổ chức của các sở, phòng và các trường """
    name = models.CharField(u'Tên tổ chức', max_length=100) #tên đơn vị. tổ chức
    level = models.CharField(u"cấp", max_length=2, choices=ORGANIZATION_LEVEL_CHOICES) #Cấp
    #------- those attributes is used for School only --------------------------------------------------------
    school_level = models.CharField(u"Khối học", max_length=6, blank=True, null=True, choices=KHOI_CHOICES)
    status = models.SmallIntegerField(max_length=3, blank=True, null=True, choices=SCHOOL_ACTION_STATUS)
    #---------------------------------------------------------------------------------------------------------
    upper_organization = models.ForeignKey('self', blank=True, null=True, verbose_name='Trực thuộc')
    manager_name = models.CharField("Tên thủ trưởng", max_length=100, null=True)
    address = models.CharField("Địa chỉ", max_length=255, blank=True, null=True) #
    phone = models.CharField("Điện thoại", max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    class Meta:
        verbose_name_plural = "Tổ chức"

    def get_status(self):
        if self.level == 'T':
            try:
                year = self.year_set.latest('time')
#                return STATUS[self.status] + ' - ' + u'Năm học ' + year.__unicode__()
                return SEMESTER_STATUS[self.status] + u', ' + year.__unicode__()
            except Exception:
                return SEMESTER_STATUS[0]
        else:
            return ''

    def save_settings(self, attribute, value):
        if type(attribute) != str or (type(value) != str and type(value) != unicode and type(value) != int):
            raise Exception('InvalidArgumentType')
        try:
            setting_file_name = str(self.id)
            setting_file_name = os.path.join(SCHOOL_SETTING_FOLDER, setting_file_name)
        except Exception as e:
            print e
            raise Exception('OrganizationNotSaved')

        setting = MyConfigParser()
        try:
            file = codecs.open(setting_file_name, 'r', 'utf-8')
        except IOError as e:
            file = codecs.open(setting_file_name, 'wb', 'utf-8')
            file.close()
            file = codecs.open(setting_file_name, 'r', 'utf-8')
        setting.readfp(file)
        file.close()
        if not setting.has_section('school'):
            setting.add_section('school')
        setting.set('school', attribute, unicode(value))
        file = codecs.open(setting_file_name, 'wb', 'utf-8')
        setting.write(file)
        file.close()
        
    def get_setting(self, attribute):
        if type(attribute) != str:
            raise Exception('InvalidArgumentType')

        if self.id:
            setting_file_name = str(self.id)
            setting_file_name = os.path.join(SCHOOL_SETTING_FOLDER, setting_file_name)
        else:
            raise Exception('OrganizationNotSaved')

        setting = MyConfigParser()
        try:
            file = codecs.open(setting_file_name, 'r', 'utf-8')
            setting.readfp(file)
            result = setting.get('school', attribute)
        except  Exception as e:
            print e
            if attribute == 'lock_time':
                self.save_settings(attribute, 24)
                return 24
            else:
                self.save_settings(attribute, '')
                return ''
        try:
            if len(result) > 1 and result[0] == '[' and result[-1] == ']':
                return eval(result)
            else:
                if attribute == 'lock_time' and not result:
                    self.save_settings('lock_time', 24)
                    result = 24
                return result
        except Exception as e:
            print e
            return ''


    def __unicode__(self):
        return self.name

class OrganizationForm(forms.Form):
    name = forms.CharField(max_length=100) #tên đơn vị. tổ chức
    level = forms.CharField(max_length=2, widget=forms.RadioSelect(choices=ORGANIZATION_LEVEL_CHOICES)) #Cấp
    upper_organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    address = forms.CharField(max_length=255) #
    phone = forms.CharField(max_length=20)
    email = forms.EmailField(max_length=50)


class UserProfile(models.Model):
    """
    Thông tin về người sủ dụng hệ thống, mở rộng User của Django.
    """
    user = models.OneToOneField(User, null=True)
    organization = models.ForeignKey(Organization, verbose_name='Đơn vị')
    position = models.CharField(choices=POSITION_CHOICE, null=True, blank=True, max_length=15)
    phone = models.CharField('Điện thoại di động', max_length=20, blank=True) #để gửi tin nhắn.
    notes = models.CharField('Ghi chú', max_length=255, blank=True)
    username_change = models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.__unicode__()



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
                raise forms.ValidationError("Hãy nhập đúng tên và mật khẩu và phân biệt chữ hoa, chũ thường.")
            elif not self.user_cache.is_active:
                raise forms.ValidationError("Tài khoản này đang bị khóa. Hãy liên hệ quản trị hệ thống.")
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                "Cookies của trình duyệt chưa được bật. Cần phải bật cookies thì mới sử dụng được.")

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class Feedback(models.Model):
    """
    Thông tin về các bản báo cáo lỗi hay liên hệ từ khách hàng
    """
    fullname = models.CharField('Họ tên', blank=True, null=True, max_length=100)
    phone = models.CharField('Điện thoại', max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    title = models.CharField('Tiêu đề', blank=True, null=True, max_length=250)
    content = models.TextField('Nội dung', max_length=3000, blank=True)

    class Meta:
        verbose_name_plural = "Phản hồi"

    def __unicode__(self):
        return self.fullname


class FeedbackForm(forms.Form):
    #Hainhh    
    title = forms.CharField(label='Tiêu đề', max_length=250, required=True)
    content = forms.CharField(label='Nội dung', widget=forms.Textarea, required=False)
    fullname = forms.CharField(label='Họ tên', max_length=100, required=False)
    phone = forms.CharField(label='Điện thoại', max_length=15, required=False)
    email = forms.EmailField(label='Email', min_length=0, required=False)
    #    type = forms.CharField(label = 'Phân loại', widget = forms.RadioSelect(choices = CONTACT_CHOICES))

class Register(models.Model):
    register_name = models.CharField("Họ và tên", max_length=250, blank=False)
    register_phone= models.CharField("Số điện thoại", max_length=15, blank=True)
    register_email= models.CharField("Email", max_length=250, blank=False)
    school_name = models.CharField("Tên trường", max_length=250, blank=False)
    school_level = models.CharField(u"Khối học", max_length=6, blank=False, choices=KHOI_CHOICES)
    school_address = models.CharField(u"Địa chỉ", max_length=250, blank=True)
    school_province = models.CharField(u"Tỉnh/Thành phố", max_length=150, choices=TINH_CHOICES)
    status = models.CharField(u"Trạng thái", max_length=150, default='CHUA_CAP', choices=REGISTER_STATUS_CHOICES)
    register_date = models.DateField(u"Ngày đăng ký", default=date.today() )
    default_user_name = models.CharField(u'Tài khoản mặc định', max_length=250, blank=True)
    default_password = models.CharField(u'Mật khẩu mặc định', max_length=250, blank=True)
    def __unicode__(self):
        return '-'.join([unicode(self.register_name), unicode(self.school_name)])
    
class RegisterForm(forms.ModelForm):
    class Meta:
        model = Register

class ResetPassword(models.Model):
#Hainhh
    username = models.CharField(max_length=50)
    code = models.CharField(max_length=15)


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label='Email của bạn', max_length=255)
        
    
    
         
