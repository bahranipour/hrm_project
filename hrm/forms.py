from django import forms 
from .models import LeaveRequest,Attendance
from jalali_date.fields import JalaliDateField
from jalali_date.widgets import AdminJalaliDateWidget



class LeaveRequestForm(forms.ModelForm):
    start_date = JalaliDateField(
        label='تاریخ شروع (شمسی)',
        widget=AdminJalaliDateWidget(attrs={'placeholder': 'yyyy-mm-dd'})
    )
    end_date = JalaliDateField(
        label='تاریخ پایان (شمسی)',
        widget=AdminJalaliDateWidget(attrs={'placeholder': 'yyyy-mm-dd'})
    )

    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']


    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد!")
        return cleaned_data
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.status != 'pending':
            raise forms.ValidationError("فقط درخواست‌های در حال انتظار قابل ویرایش هستند!")




class CheckInForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['status']  # امکان انتخاب وضعیت (مثلاً مرخصی است یا حاضر)

class CheckOutForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = []  # فقط برای ثبت ساعت خروج
           

       
   

     
