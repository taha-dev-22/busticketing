from django.shortcuts import render, redirect
from home.models import Driver, Fares, Passenger, RouteAssignedToBus, Schedule, Tickets, UserofTerminal, Voucher, Route, Closedby, Midpoint, TicketsAudit, Bus
from home.auditHandler import AuditHandler
from django.contrib.auth.models import User
from home.bookingHandler import BookingHandler
from home.ticketingHandler import TicketingHandler
from home.registerationHandler import RegistrationHandler
from home.userHandler import UserHandler
from django.contrib import messages
from datetime import timedelta, datetime
from django.db.models import Q
from django.contrib.auth import logout, authenticate, login
import json
# Create your views here.

def importData(request):
    if request.user.is_anonymous:
        return redirect('/login')
    if request.method == "POST":
        fromdate = request.POST['inputFromDate']
        fromdate = datetime.strptime(fromdate, r'%Y-%m-%d')
        todate = request.POST['inputToDate']
        todate = datetime.strptime(todate, r'%Y-%m-%d')
        if request.POST['inputOption'] == '1':
            result = AuditHandler.returnBuses(request, fromdate=fromdate, todate=todate)
            return result['response']
        elif request.POST['inputOption'] == '2':
            result = AuditHandler.returnDrivers(request, fromdate=fromdate, todate=todate)
            return result['response']
        elif request.POST['inputOption'] == '3':
            result = AuditHandler.returnSchedules(request, fromdate=fromdate, todate=todate)
            return result['response']
        elif request.POST['inputOption'] == '4':
            result = AuditHandler.returnTickets(request, fromdate=fromdate, todate=todate)
            return result['response']
        elif request.POST['inputOption'] == '5':
            result = AuditHandler.returnCnics(request, fromdate=fromdate, todate=todate)
            return result['response']
        elif request.POST['inputOption'] == '6':
            result = AuditHandler.returnVouchers(request, fromdate=fromdate, todate=todate)
            return result['response']
    return render(request, 'import.html')

def createUser(request):
    if request.user.is_anonymous:
        return redirect('/login')
    if not request.user.is_superuser:
        return redirect('/warning')
    result = UserHandler.create(request)
    return render(result['request'], 'createuser.html', {'terminals': result['terminals']})

def edituser(request, user_id):
    if request.user.is_anonymous:
        return redirect('/login')
    if not request.user.is_superuser:
        return redirect('/warning')
    result = UserHandler.editUsers(request, user_id)
    return render(result['request'], 'edituser.html', {'User': result['User'], 'udata': result['udata'], 'uterminal': result['uterminal'], 'terminals': result['terminals']})

def removeuser(request, user_id):
    if request.user.is_anonymous:
        return redirect('/login')
    if not request.user.is_superuser:
        return redirect('/warning')
    if user_id == request.user.id:
        messages.warning(request, 'You cannot remove yourself from users!')
    else:
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()
            messages.success(request, 'User removed successfully!')
        except Exception as e:
            messages.warning(request, e)
    return viewUsers(request)

def viewUsers(request):
    if request.user.is_anonymous:
        return redirect('/login')
    if not request.user.is_superuser:
        return redirect('/warning')
    result = UserHandler.viewUsers(request)
    return render(result['request'], 'users.html', {'Users': result['Users']})

def warning(request):
    return render(request, 'warning.html', {'response': "You are not authorized to access this page!"})
    
def registerSchedule(request):
    if request.user.is_anonymous:
        return redirect('/login')
    result = RegistrationHandler.registerSchedule(request)
    return render(result['request'], 'schedule.html', {'routeasgbus':result['routeasgbus']})

def midtimes(request):
    if request.user.is_anonymous:
        return redirect('/login')
    schedule = None
    try:
        schedule = Schedule.objects.all().distinct()
    except Exception as e:
        messages.warning(request, e)
    return render(request, 'midtimes.html', {'schedule': schedule})

def addtimetosc(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    midpoints = None
    schedule = None
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        route = schedule.route_assg_bus.route
        midpoints = Midpoint.objects.filter(route=route)
    except Exception as e:
        messages.warning(request, e)
    if request.method == "POST":
        try:
            midtimes = {}
            data = dict(request.POST)
            for i in range(len(data['inputTerminalId'])):
                midtimes[str(data['inputTerminalId'][i])] = data['inputTime'][i]
            schedule.mid_dept = json.dumps(midtimes)
            schedule.save()
            if 'inputCheck' in data:
                schedules = Schedule.objects.filter(route_assg_bus = schedule.route_assg_bus)
                for i in schedules:
                    if i.departure.time() == schedule.departure.time():
                        i.mid_dept = json.dumps(midtimes)
                        i.save()
            messages.success(request, 'Timings added successfully!')
        except Exception as e:
            messages.warning(request, e)
    return render(request, 'addtimetosc.html', {'midpoints': midpoints, 'schedule': schedule})

def loginUser(request):
    if request.method == "POST":
        username = request.POST.get('inputUsername')
        password = request.POST.get('inputPassword')
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            messages.warning(request, 'User is not available!')
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
                'tickets': result['tickets'], 'vouchers': result['vouchers'], 'billdata': result['billdata']})

def schedule(request):
    if request.user.is_anonymous:
        return redirect('/login')
    schedule, user, userterminal, inner_qs, routes = None, None, None, None, None
    try:
        user = User.objects.get(id=request.user.id)
        userterminal = UserofTerminal.objects.get(user=user)
        request.session['uterminal'] = str(userterminal.terminal)
    except Exception as e:
        messages.warning(request, e)
    try:
        inner_qs = Closedby.objects.filter(terminal=userterminal.terminal)
        route = Route.objects.filter(source=userterminal.terminal)
        schedule = Schedule.objects.filter(status=True).exclude(id__in=inner_qs).order_by('departure')
        routes = Route.objects.all()
    except Exception as e:
        messages.warning(request, e)
    if request.method == "POST":
        try:
            date = request.POST['inputDate']
            time = request.POST['inputTime']
            if date:
                dt = None
                if time:
                    dt = datetime.combine(datetime.strptime(date, r'%Y-%m-%d'), datetime.time(datetime.strptime(time, r'%H:%M')))
                else:
                    dt = datetime.strptime(date, r'%Y-%m-%d')
                if request.POST['inputRoute']:
                    route = Route.objects.get(id=request.POST['inputRoute'])
                    rtb = RouteAssignedToBus.objects.get(route=route)
                    schedule = Schedule.objects.filter(route_assg_bus = rtb, departure__gte = dt, status=True).exclude(id__in=inner_qs).order_by('departure')
                else:
                    schedule = Schedule.objects.filter(departure__gte = dt, status=True).exclude(id__in=inner_qs).order_by('departure')
            else:
                messages.warning(request, "Please choose a date first!")
        except Exception as e:
            messages.warning(request, e)
    return render(request, 'index.html', {'schedule': schedule, 'uterminal': userterminal, 'routes': routes})

def booking(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    response = BookingHandler.returnBooking(request, schedule_id)
    if not response['result']:
        return schedule(response['request'])
    return render(response['request'], 'booking.html', response['result'])

def ticketing(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    response = TicketingHandler.returnTicketing(request, schedule_id)
    if not response['result']:
        return schedule(response['request'])
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
    return render(result['request'], 'cancelTickets.html', {'tickets': result['tickets'], 'ps_id': result['ps_id']})

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
    return render(result['request'], 'route.html', {'terminals':result['terminals'], 'routes': result['routes']})

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
    return render(result['request'], 'fares.html', {'fares': result['fares'], 'routetobus': result['routetobus'], 'midpoints': result['midpoints']})

def close(request, schedule_id):
    if request.user.is_anonymous:
        return redirect('/login')
    sc = Schedule.objects.get(id=schedule_id)
    user = request.user
    deptime = None
    uterminal = UserofTerminal.objects.get(user=user)
    tickets = Tickets.objects.filter(schedule=sc, source=uterminal.terminal)
    route_to_bus = RouteAssignedToBus.objects.get(id=sc.route_assg_bus.id)
    route = route_to_bus.route
    mdpts = Midpoint.objects.filter(route=route)
    validuser = False
    if route.source.id == uterminal.terminal.id:
        validuser = True
    else:
        deptime = str(datetime.now().date()) + ' , ' + str(datetime.now().time().strftime('%I:%M:%S %p'))
    for i in mdpts:
        if uterminal.terminal.id == i.terminal:
            validuser = True
    fare = 0
    if request.method == "POST" and validuser and 'close-sc' in request.POST:
        data = request.POST
        try:
            user = request.user
            uterminal = UserofTerminal.objects.get(user=user)
            sc = Schedule.objects.get(id=schedule_id)
            closedby = Closedby(schedule= sc, terminal=uterminal.terminal)
            closedby.save()
            tickets = Tickets.objects.filter(schedule= sc, source=uterminal.terminal)
            for i in tickets:
                tk_audit = TicketsAudit(voucher=i.voucher, schedule = sc, source = i.source, destination = i.destination, fare = i.fare.fare, seat_no = i.seat_no, bookedby = i.bookedby, gender = i.gender,
                                        status = i.status, type = i.type, issuedby = i.issuedby, discount = i.discount)
                tk_audit.save()
            voucher = Voucher(terminal=uterminal.terminal, schedule= sc, issuedby= user, voucher= data['inputVoucher'], 
                              refreshment=data['inputRefreshment'], washing=data['inputWashing'], parking=data['inputParking'], toll=data['inputToll'])
            voucher.save()
            messages.success(request, 'Booking Closed Successfully!')
        except Exception as e:
            messages.warning(request, e)
    elif not validuser and 'close-sc' in request.POST:
        messages.warning(request, 'You cannot close this schedule!')
        return schedule(request)
    elif 'quit-schedule' in request.POST:
        print(True)
        try:
            sc.status = False
            sc.save()
            messages.success(request, "Schedule removed successfully!")
            return redirect('schedule')
        except Exception as e:
            messages.warning(request, e)
    seats = []
    for i in tickets:
        fare += i.fare.fare
        seats.append(i.seat_no)
    tickets = tickets.count()
    seats = ','.join(str(seat) for seat in seats)
    print(seats, type(seats))
    return render(request, 'close.html', {'schedule':sc, 'tickets':tickets, 'route_bus': route_to_bus, 'deptime': deptime, 'fare': fare, 'seats': seats})

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

def modifybus(request, bus_id):
    if request.user.is_anonymous:
        return redirect('/login')
    bus = None
    try:
        bus = Bus.objects.get(id=bus_id)
    except Exception as e:
        messages.warning(request, e)
    if request.method == "POST":
        try:
            data = request.POST
            bus.bus_model=data['inputModel']
            bus.bus_number=data['inputNumber']
            bus.seating_capacity=data['inputSeating']
            bus.service_type=data['inputService']
            bus.save()
            bus = Bus.objects.get(id=bus_id)
            messages.success(request, 'Bus updated successfully!')
        except Exception as e:
            messages.warning(request, e)
    return render(request, 'modifybus.html', {'bus': bus})

def viewbuses(request, bus_id = None):
    if request.user.is_anonymous:
        return redirect('/login')
    Buses = None
    try:
        Buses = Bus.objects.all()
    except Exception as e:
        messages.warning(request, e)
    if bus_id is not None:
        bus = None
        try:
            bus = Bus.objects.get(id=bus_id)
            bus.delete()
            messages.success(request, 'Bus deleted successfully!')
        except Exception as e:
            messages.warning(request, e)
    return render(request, 'buses.html', {'Buses': Buses})

def modifydriver(request, driver_id):
    if request.user.is_anonymous:
        return redirect('/login')
    driver = None
    try:
        driver = Driver.objects.get(id=driver_id)
    except Exception as e:
        messages.warning(request, e)
    if request.method == "POST":
        try:
            data = request.POST
            driver.name=data['inputName']
            driver.cnic=data['inputCnic']
            driver.phone=data['inputPhone']
            driver.address=data['inputAddress']
            driver.save()
            driver = Driver.objects.get(id=driver_id)
            messages.success(request, 'Driver updated successfully!')
        except Exception as e:
            messages.warning(request, e)
    return render(request, 'modifydriver.html', {'driver': driver})

def viewdrivers(request, driver_id=None):
    if request.user.is_anonymous:
        return redirect('/login')
    Drivers = None
    try:
        Drivers = Driver.objects.all()
    except Exception as e:
        messages.warning(request, e)
    if driver_id is not None:
        driver = None
        try:
            driver = Driver.objects.get(id=driver_id)
            driver.delete()
            messages.success(request, 'Driver deleted successfully!')
        except Exception as e:
            messages.warning(request, e)
    return render(request, 'drivers.html', {'Drivers': Drivers})