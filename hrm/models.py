from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta



class Department(models.Model):
    name = models.CharField(max_length=100,verbose_name='نام دپارتمان')

    class Meta:
        verbose_name = 'واحد سازمانی'
        verbose_name_plural = 'واحدهای سازمانی'
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,verbose_name='کاربر')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True,verbose_name='واحد سازمانی')
    phone = models.CharField(max_length=15,verbose_name='شماره تماس')
    join_date = models.DateField(auto_now_add=True,verbose_name='تاریخ پیوستن')

    class Meta:
        verbose_name = 'کارمند'
        verbose_name_plural = 'کارمندان'

    def __str__(self):
        return self.user.get_full_name()
    


class LeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,verbose_name='کارمند')
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    reason = models.TextField(verbose_name='علت')
    STATUS_CHOICES = [
        ('pending', 'در حال بررسی'),
        ('approved', 'تایید'),
        ('rejected', 'عدم تایید'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending',verbose_name='وضعیت')

    class Meta:
        verbose_name = 'درخواست مرخصی'
        verbose_name_plural = 'درخواست های مرخصی'
    
    def __str__(self):
        return f"{self.employee} - {self.status}"
    




class Attendance(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE,verbose_name='کارمند')
    date = models.DateField(auto_now_add=True,verbose_name='تاریخ')  # تاریخ خودکار شمسی
    check_in = models.TimeField(null=True,blank=True,verbose_name='زمان ورود')  # فقط ساعت ورود
    check_out = models.TimeField(null=True, blank=True,verbose_name='زمان خروج')
    check_in_datetime = models.DateTimeField(auto_now_add=True,verbose_name='ساعت ورود')  # ساعت ورود
    check_out_datetime = models.DateTimeField(null=True, blank=True,verbose_name='ساعت خروج')  # ساعت خروج
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غایب'),
        ('late', 'تأخیر'),
        ('on_leave', 'مرخصی'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present',verbose_name='وضعیت')


    @property
    def working_duration(self):
        if self.check_in_datetime and self.check_out_datetime:
            duration = self.check_out_datetime - self.check_in_datetime
            total_seconds = duration.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            return f"{hours}:{minutes:02d}"
        return "-"
    


    class Meta:
        verbose_name = 'حضور و غیاب'
        verbose_name_plural = 'سوابق حضور و غیاب'

    def __str__(self):
        return f"{self.employee} - {self.date}"
    



class Salary(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="کارمند")
    base_salary = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="حقوق پایه")
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=0, default=0, verbose_name="ساعت اضافه‌کاری")
    overtime_rate = models.DecimalField(max_digits=5, decimal_places=0, default=1.5, verbose_name="نرخ اضافه‌کاری")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=0, default=10, verbose_name="درصد مالیات")
    insurance_percentage = models.DecimalField(max_digits=5, decimal_places=0, default=7, verbose_name="درصد بیمه")
    bonus = models.DecimalField(max_digits=10, decimal_places=0, default=0, verbose_name="پاداش")
    payment_date = models.DateField(verbose_name="تاریخ پرداخت")

    class Meta:
        verbose_name = 'حقوق و دستمزد'
        verbose_name_plural = 'حقوق و دستمزد'
    
    @property
    def total_salary(self):
        """محاسبه حقوق خالص با احتساب تمام کسورات و مزایا"""
        # محاسبه اضافه‌کاری
        hourly_rate = self.base_salary / 160  # فرض: 160 ساعت کار ماهانه
        overtime_pay = self.overtime_hours * self.overtime_rate * hourly_rate
        
        # محاسبه کل حقوق ناخالص
        gross_salary = self.base_salary + overtime_pay + self.bonus
        
        # محاسبه کسورات
        total_deductions = (self.tax_percentage + self.insurance_percentage) / 100 * gross_salary
        
        # حقوق خالص
        net_salary = gross_salary - total_deductions
        
        return round(net_salary, 0)
    
    @property
    def attendance_factor(self):
        """محاسبه ضریب حضور برای پاداش"""
        from django.db.models import Count
        total_days = Attendance.objects.filter(
            employee=self.employee,
            date__month=self.payment_date.month
        ).count()
        
        work_days = Attendance.objects.filter(
            employee=self.employee,
            date__month=self.payment_date.month,
            status='present'
        ).count()
        
        return work_days / total_days if total_days > 0 else 0

    @property
    def adjusted_bonus(self):
        """پاداش تعدیل شده بر اساس حضور"""
        return self.bonus * self.attendance_factor
    
    

    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.payment_date.strftime('%Y-%m')}"

