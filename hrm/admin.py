from django.contrib import admin
from .models import Department, Employee, LeaveRequest,Attendance,Salary
from jalali_date import datetime2jalali, date2jalali
from jalali_date.admin import ModelAdminJalaliMixin, StackedInlineJalaliMixin, TabularInlineJalaliMixin





@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_per_page = 10

@admin.register(Employee)
class EmployeeAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):

    
    list_display = ('fullname','department','join_date')

    raw_id_fields = ('user',)
    list_per_page = 10

    @admin.display(description='نام و نام خانوادگی')
    def fullname(self,obj):
         return obj.user.first_name + ' ' + str(obj.user.last_name)
    


@admin.register(LeaveRequest)
class LeaveRequestAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    list_display = ('employee','start_date','end_date','status')

    list_per_page = 10
    list_editable = ('status',)


@admin.register(Attendance)
class AttendanceAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in_datetime', 'check_out_datetime', 'status']
    list_filter = ['status', 'date']
    search_fields = ['employee__user__username']
    list_per_page = 10




@admin.register(Salary)
class SalaryAdmin(ModelAdminJalaliMixin,admin.ModelAdmin):
    # تنظیمات نمایش لیست
    list_display = ('employee', 'sum_salary')
    list_filter = ('payment_date', 'employee__department')
    search_fields = ('employee__user__first_name', 'employee__user__last_name')
  
    list_per_page = 10
    
    # تنظیمات فرم ویرایش
    fieldsets = (
        ('اطلاعات پایه', {
            'fields': ('employee', 'payment_date')
        }),
        ('محاسبات حقوق', {
            'fields': ('base_salary', 'overtime_hours', 'bonus')
        }),
    )

    @admin.display(description='جمع حقوق')
    def sum_salary(self,obj):
         return obj.total_salary


class SalaryInline(admin.TabularInline):  # یا StackedInline
    model = Salary
    extra = 0

class EmployeeAdmin(admin.ModelAdmin):
    inlines = [SalaryInline]



