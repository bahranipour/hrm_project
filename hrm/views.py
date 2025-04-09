from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LeaveRequestForm
from .models import Employee,LeaveRequest,Attendance,Salary
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone


@login_required
def create_leave_request(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            # اختصاص کارمند به درخواست (با فرض اینکه Employee به User مرتبط است)
            employee = Employee.objects.get(user=request.user)
            leave_request.employee = employee
            leave_request.save()
            messages.success(request,'درخواست شما با موفقیت ثبت شد')
            return redirect('my_leave_requests')
    else:
        form = LeaveRequestForm()
    
    return render(request, 'hrm/create_leave_request.html', {'form': form})



@login_required
def edit_leave_request(request, pk):
    # فقط درخواست‌های کاربر جاری و با وضعیت pending قابل ویرایش هستند
    leave_request = get_object_or_404(
        LeaveRequest, 
        pk=pk, 
        employee__user=request.user,
        status='pending'  # فقط درخواست‌های در حال انتظار قابل ویرایش
    )
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'درخواست مرخصی با موفقیت ویرایش شد.')
            return redirect('my_leave_requests')
    else:
        form = LeaveRequestForm(instance=leave_request)
    
    return render(request, 'hrm/edit_leave_request.html', {'form': form})




@login_required
def my_leave_requests(request):
    employee = Employee.objects.get(user=request.user)
    leave_requests_list = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')  # جدیدترین درخواست‌ها اول
    
    # تنظیم صفحه‌بندی (مثلاً ۵ آیتم در هر صفحه)
    paginator = Paginator(leave_requests_list, 5)
    page_number = request.GET.get('page')  # دریافت شماره صفحه از URL
    
    try:
        leave_requests = paginator.page(page_number)
    except PageNotAnInteger:
        leave_requests = paginator.page(1)  # اگر صفحه عدد نباشد، صفحه اول نمایش داده شود
    except EmptyPage:
        leave_requests = paginator.page(paginator.num_pages)  # اگر صفحه خالی بود، آخرین صفحه نمایش داده شود
    
    return render(request, 'hrm/my_leave_requests.html', {'leave_requests': leave_requests})





@login_required
def check_in(request):
    try:
        employee = Employee.objects.get(user=request.user)
        today = timezone.now().date()
        
        if Attendance.objects.filter(employee=employee, date=today).exists():
            messages.warning(request, 'شما امروز قبلاً ورود خود را ثبت کرده‌اید!')
            return redirect('attendance_dashboard')
        
        # ثبت با زمان دقیق
        Attendance.objects.create(
            employee=employee,
            check_in=timezone.now().time(),
            check_in_datetime=timezone.now(),  # ذخیره زمان دقیق
            status='present'
        )
        messages.success(request, 'ورود شما با موفقیت ثبت شد.')
        return redirect('attendance_dashboard')
    
    except Employee.DoesNotExist:
        messages.error(request, 'پروفایل کارمند یافت نشد!')
        return redirect('home')

@login_required
def check_out(request):
    try:
        employee = Employee.objects.get(user=request.user)
        today = timezone.now().date()
        attendance = Attendance.objects.filter(employee=employee, date=today).first()
        
        if not attendance:
            messages.error(request, 'ابتدا باید ورود خود را ثبت کنید!')
            return redirect('check_in')
        
        if attendance.check_out:
            messages.warning(request, 'شما امروز قبلاً خروج خود را ثبت کرده‌اید!')
            return redirect('attendance_dashboard')
        
        # ثبت خروج با زمان دقیق
        now = timezone.now()
        attendance.check_out = now.time()
        attendance.check_out_datetime = now
        attendance.save()
        
        # اعتبارسنجی حداقل زمان کار
        if (attendance.check_out_datetime - attendance.check_in_datetime).total_seconds() < 60:
            messages.warning(request, 'زمان کار باید حداقل ۱ دقیقه باشد!')
            attendance.check_out = None
            attendance.check_out_datetime = None
            attendance.save()
            return redirect('attendance_dashboard')
        
        messages.success(request, 'خروج شما با موفقیت ثبت شد.')
        return redirect('attendance_dashboard')
    
    except Employee.DoesNotExist:
        messages.error(request, 'پروفایل کارمند یافت نشد!')
        return redirect('home')


@login_required
def attendance_dashboard(request):

        # 1. ابتدا employee را دریافت می‌کنیم
        employee = Employee.objects.get(user=request.user)
        today = timezone.now().date()
        last_attendance = Attendance.objects.filter(employee=employee).last()
        
        # 2. تعریف اولیه all_records با فیلتر پایه
        all_records = Attendance.objects.filter(employee=employee,date=today).order_by('-date')
        
        # 3. اعمال فیلترهای اختیاری (اگر وجود داشتند)
        
        
        
        # 4. صفحه‌بندی
        paginator = Paginator(all_records, 10)  # 10 رکورد در هر صفحه
        page_number = request.GET.get('page')
        
        try:
            records = paginator.page(page_number)
        except PageNotAnInteger:
            records = paginator.page(1)
        except EmptyPage:
            records = paginator.page(paginator.num_pages)
            
        
        return render(request, 'hrm/attendance_dashboard.html', {
            'attendance_records': records,
            'last_attendance': last_attendance,
            'current_time': timezone.now().isoformat(),  # برای JavaScript
        })

@login_required
def my_salary(request):
    employee = get_object_or_404(Employee, user=request.user)
    salaries_list = Salary.objects.filter(employee=employee).order_by('-payment_date')
    
    # تنظیمات صفحه‌بندی (۱۰ آیتم در هر صفحه)
    paginator = Paginator(salaries_list, 10)
    page_number = request.GET.get('page')
    
    try:
        salaries = paginator.page(page_number)
    except PageNotAnInteger:
        salaries = paginator.page(1)
    except EmptyPage:
        salaries = paginator.page(paginator.num_pages)
    
    return render(request, 'hrm/my_salary.html', {
        'salaries': salaries,
        'employee': employee
    })