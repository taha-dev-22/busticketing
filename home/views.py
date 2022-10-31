from django.shortcuts import render, redirect
from home.models import Driver, Fares, Passenger, RouteAssignedToBus, Schedule, Tickets, UserofTerminal, Voucher
from django.contrib.auth.models import User
from home.bookingHandler import BookingHandler
from home.ticketingHandler import TicketingHandler
from home.registerationHandler import RegistrationHandler
from home.userHandler import UserHandler
from django.contrib import messages
from datetime import timedelta, datetime
from django.contrib.auth import logout, authenticate, login
# Create your views here.

def importData(request):
    if request.user.is_anonymous:
        return redirect('/login')
    return render(request, 'import.html')

def createUser(request):
    if request.user.is_anonymous or not request.user.is_superuser:
        return redirect('/warning')
    result = UserHandler.create(request)
    return render(result['request'], 'createuser.html', {'terminals': result['terminals']})

def warning(request):
    return render(request, 'warning.html', {'response': "You are not authorized to access this page!"})
    
def registerSchedule(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = RegistrationHandler.registerSchedule(request)
    return render(result['request'], 'schedule.html', {'routeasgbus':result['routeasgbus']})

def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('inputUsername')
        password = request.POST.get('inputPassword')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, 'login.html')
    return render(request, 'login.html')

def logoutUser(request):
    logout(request)
    return redirect('/login')

def bookingdetail(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = BookingHandler.bookingdetail(request)
    return render(result['request'], 'bookingdetail.html', {'uid': result['uid'], 'schedules': result['schedules'], 
                'tickets': result['tickets'], 'schedule': result['schedule'], 'billdata': result['billdata']})

def schedule(request):
    if request.user.is_anonymous:
        return redirect('/login')
    schedule = None
    user = User.objects.get(id=request.user.id)
    userterminal = UserofTerminal.objects.get(user=user)
    request.session['uterminal'] = str(userterminal.terminal)
    schedule = Schedule.objects.filter(status=True)
    if request.method == "POST":
        date = request.POST['inputDate']
        time = request.POST['inputTime']
        if date:
            dt = None
            if time:
                dt = datetime.combine(datetime.strptime(date, r'%Y-%m-%d'), datetime.time(datetime.strptime(time, r'%H:%M')))
            else:
                dt = datetime.strptime(date, r'%Y-%m-%d')
            schedule = Schedule.objects.filter(departure__gte = dt, status=True)
        else:
            messages.warning(request, "Please choose a date first!")
    return render(request, 'index.html', {'schedule': schedule, 'uterminal': userterminal})

def booking(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    response = BookingHandler.returnBooking(request, schedule_id)
    return render(response['request'], 'booking.html', response['result'])

def ticketing(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    response = TicketingHandler.returnTicketing(request, schedule_id)
    return render(response['request'], 'ticketing.html', response['result'])

def printBill(request):
    if request.user.is_anonymous:
        return redirect('/login')
    return render(request, 'bill.html')

def cancelBooking(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = BookingHandler.cancelBooking(request)
    return render(result['request'], 'cancelBooking.html', {'tickets': result['tickets']})

def cancelTickets(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = TicketingHandler.cancelTickets(request)
    return render(result['request'], 'cancelTickets.html', {'tickets': result['tickets'], 'fares': result['fares'], 'ps_id': result['ps_id']})

def cancelReservation(request):
     if request.user.is_anonymous:
         return redirect('/login')
     tickets = BookingHandler.cancelReservation(request)
     return render(request, 'cancelReservation.html', {'tickets': tickets})

def returnBookingbySc(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    tickets = BookingHandler.returnBookingBySchedule(request, schedule_id)
    return render(request, 'cancelReservation.html', {'tickets': tickets})

def registerDriver(request):
    if request.user.is_anonymous:
        return redirect('/login')
    RegistrationHandler.driverRegisteration(request)
    return render(request, 'driver.html')

def registerBus(request):
    if request.user.is_anonymous:
        return redirect('/login')
    RegistrationHandler.busRegisteration(request)
    return render(request, 'bus.html')

def registerTerminal(request):
    if request.user.is_anonymous:
        return redirect('/login')
    RegistrationHandler.terminalRegisteration(request)
    return render(request, 'terminal.html')

def registerRoute(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = RegistrationHandler.routeRegisteration(request)
    return render(result['request'], 'route.html', {'terminals':result['terminals']})

def assignRoute(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = RegistrationHandler.assignBusToRoute(request)
    return render(result['request'], 'bustoroute.html', {'buses':result['buses'], 'routes':result['routes'], 'routeasgbus':result['routeasgbus']})

def assignDriver(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = RegistrationHandler.assignDriverToBus(request)
    return render(result['request'], 'drivertobus.html', {'buses':result['buses'], 'drivers':result['drivers'], 'bustodriver':result['bustodriver']})

def vouchers(request):
    if request.user.is_anonymous:
        return redirect('/login')
    uterminal = UserofTerminal.objects.get(user=request.user)
    vouchers = Voucher.objects.filter(terminal=uterminal.terminal)
    return render(request, 'voucher.html', {'vouchers': vouchers})

def fares(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = RegistrationHandler.fares(request)
    return render(result['request'], 'fares.html', {'fares': result['fares'], 'routetobus': result['routetobus']})

def close(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    schedule = Schedule.objects.get(id=schedule_id)
    tickets = Tickets.objects.filter(schedule=schedule).count()
    route_to_bus = RouteAssignedToBus.objects.get(id=schedule.route_assg_bus.id)
    fare = Fares.objects.get(route_asg_to_bus=route_to_bus).fare
    fare *= tickets
    if request.method == "POST":
        data = request.POST
        try:
            schedule = Schedule.objects.get(id=schedule_id)
            schedule.status = False
            schedule.save()
            user = request.user
            uterminal = UserofTerminal.objects.get(user=user)
            voucher = Voucher(terminal=uterminal.terminal, schedule= schedule, issuedby= user, voucher= data['inputVoucher'], 
                              refreshment=data['inputRefreshment'], washing=data['inputWashing'], parking=data['inputParking'], toll=data['inputToll'])
            voucher.save()
            messages.success(request, 'Booking Closed Successfully!')
        except Exception as e:
            messages.warning(request, e)
    return render(request, 'close.html', {'schedule':schedule, 'tickets':tickets, 'route_bus': route_to_bus, 'fare': fare})

def addtime(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    if request.method == "POST":
        time = int(request.POST["inputTime"])
        schedule = Schedule.objects.get(id=schedule_id)
        schedule.arrival += timedelta(minutes=time)
        schedule.departure += timedelta(minutes=time)
        schedule.save()
        return redirect('schedule')
    return render(request, 'addtime.html')