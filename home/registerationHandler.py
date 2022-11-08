from asyncio.windows_events import NULL
from home.models import AssignedBusesToDriver, Driver, Bus, Fares, Midpoint, Route, Terminal, RouteAssignedToBus, Schedule
from django.contrib import messages
from datetime import datetime, timedelta

class RegistrationHandler():
    @staticmethod
    def registerSchedule(request):
        routeasgbus = None
        try:
            routeasgbus = RouteAssignedToBus.objects.all()
        except Exception as e:
            messages.warning(request, 'Route assignment not found!')
        if request.method == "POST":
            data = request.POST
            schedule = None
            departure = None
            arrival = None
            routebus = None
            fromdate = datetime.strptime(data['inputFromDate'], r'%Y-%m-%d')
            todate = datetime.strptime(data['inputToDate'], r'%Y-%m-%d')
            if fromdate <= todate:
                try:
                    while fromdate <= todate:
                        departure = datetime.combine(datetime.date(fromdate), datetime.time(datetime.strptime(data['inputDeptTime'], r'%H:%M')))
                        arrival = datetime.combine(datetime.date(fromdate), datetime.time(datetime.strptime(data['inputArrTime'], r'%H:%M')))
                        routebus = RouteAssignedToBus.objects.get(id = data['inputRouteBus'])
                        schedule = Schedule.objects.filter(route_assg_bus = routebus, departure = departure, arrival = arrival).exists()
                        fromdate += timedelta(days=1)
                        if schedule:
                            messages.warning(request, 'Schedule already exists!')
                            return {'request': request, 'routeasgbus': routeasgbus}
                except Exception as e:
                    messages.warning(request, e)
                if not schedule:
                    try:
                        fromdate = datetime.strptime(data['inputFromDate'], r'%Y-%m-%d')
                        todate = datetime.strptime(data['inputToDate'], r'%Y-%m-%d')
                        while fromdate <= todate:
                            departure = datetime.combine(datetime.date(fromdate), datetime.time(datetime.strptime(data['inputDeptTime'], r'%H:%M')))
                            arrival = datetime.combine(datetime.date(fromdate), datetime.time(datetime.strptime(data['inputArrTime'], r'%H:%M')))
                            schedule = Schedule(route_assg_bus = routebus, departure = departure, arrival = arrival)
                            schedule.save()
                            fromdate += timedelta(days=1)
                        messages.success(request, 'Schedules Registered Successfully!')
                    except Exception as e:
                        messages.warning(request, e)
                else:
                    messages.warning(request, 'Schedule already exists!')
            else:
                messages.warning(request, 'Final Date must be greater than initial date!')
        return {'request': request, 'routeasgbus': routeasgbus}

    @staticmethod
    def driverRegisteration(request):
        if request.method == "POST":
            driver = Driver.objects.filter(cnic=request.POST['inputCnic']).exists()
            if not driver:
                data = request.POST
                try:
                    driver = Driver(name=data['inputName'], dob = datetime.strptime(data['inputDob'], r'%Y-%m-%d'), cnic = data['inputCnic'], phone = data['inputPhone'], address = data['inputAddress'])
                    driver.save()
                    messages.success(request, 'Driver Registered Successfully!')
                except Exception as e:
                    messages.warning(request, e)
            else:
                messages.warning(request, 'Driver already exists!')
        return request
    
    @staticmethod
    def busRegisteration(request):
        if request.method == "POST":
            bus = Bus.objects.filter(bus_number=request.POST['inputNumber']).exists()
            if not bus:
                data = request.POST
                try:
                    bus = Bus(bus_number=data['inputNumber'], seating_capacity = data['inputSeating'], service_type = data['inputService'], bus_model = data['inputModel'])
                    bus.save()
                    messages.success(request, 'Bus Registered Successfully!')
                except Exception as e:
                    messages.warning(request, e)
            else:
                messages.warning(request, 'Bus already exists!')
        return request
    
    @staticmethod
    def terminalRegisteration(request):
        if request.method == "POST":
            terminal = Terminal.objects.filter(name=request.POST['inputName'], city=request.POST['inputCity']).exists()
            if not terminal:
                data = request.POST
                try:
                    terminal = Terminal(name=data['inputName'], city = data['inputCity'], address = data['inputAddress'])
                    terminal.save()
                    messages.success(request, 'Terminal Registered Successfully!')
                except Exception as e:
                    messages.warning(request, e)
            else:
                messages.warning(request, 'Terminal already exists!')
        return request
    
    @staticmethod
    def routeRegisteration(request):
        terminals = None
        routes = None
        try:
            terminals = Terminal.objects.all()
            routes = Route.objects.all()
        except Exception as e:
            messages.warning(request, e)
        if request.method == "POST" and 'route' in request.POST:
            try:
                data = request.POST
                t1 = Terminal.objects.get(id=data['inputSource'])
                t2 = Terminal.objects.get(id=data['inputDestination'])
                route = Route.objects.filter(source=t1, destination=t2, via=data['inputVia']).exists()
                if data['inputSource'] == data['inputDestination']:
                    messages.warning(request, 'Source and Destinations must be different!')
                elif not route:
                    route = Route(source=t1, destination=t2, via=data['inputVia'])
                    route.save()
                    messages.success(request, 'Route Registered Successfully!')
                else:
                    messages.warning(request, 'Route Already exists!')
            except Exception as e:
                messages.warning(request, e)
        elif request.method == "POST" and 'midpoint' in request.POST:
            try:
                data = request.POST
                terminal = Terminal.objects.get(id=data['inputTerminal'])
                route = Route.objects.get(id=data['inputRoute'])
                midpoint = Midpoint.objects.filter(terminal=terminal, route=route).exists()
                if terminal == route.source:
                    messages.warning(request, 'Source cannot be Midpoint!')
                elif terminal == route.destination:
                    messages.warning(request, 'Destination cannot be Midpoint!')
                elif not midpoint:
                    midpoint = Midpoint(route=route, terminal=terminal)
                    midpoint.save()
                    messages.success(request, 'MidPoint Registered Successfully!')
                else:
                    messages.warning(request, 'MidPoint Already exists!')
            except Exception as e:
                messages.warning(request, e)
        return {'request': request, 'terminals': terminals, 'routes': routes}
    
    @staticmethod
    def assignBusToRoute(request):
        buses = None
        routes = None
        routeasgbus = None
        if request.method == "POST":
            try:
                data = request.POST
                bus = Bus.objects.get(id=data['inputBus'])
                route = Route.objects.get(id=data['inputRoute'])
                routeasgbus = RouteAssignedToBus.objects.filter(bus=bus, route=route).exists()
                if not routeasgbus:
                    routeasgbus = RouteAssignedToBus(bus=bus, route=route)
                    routeasgbus.save()
                    messages.success(request, 'Route Assigned Successfully!')
                else:
                    messages.warning(request, 'Bus Already Assigned to Route!')
            except Exception as e:
                messages.warning(request, e)
        try:
            buses = Bus.objects.all()
            routes = Route.objects.all()
            routeasgbus = RouteAssignedToBus.objects.all()
        except Exception as e:
            messages.warning(request, e)
        return {'request': request, 'buses': buses, 'routes': routes, 'routeasgbus': routeasgbus}
    
    @staticmethod
    def assignDriverToBus(request):
        buses = None
        drivers = None
        bustodriver = None
        if request.method == "POST":
            try:
                data = request.POST
                bus = Bus.objects.get(id=data['inputBus'])
                driver = Driver.objects.get(id=data['inputDriver'])
                driverasgbus= AssignedBusesToDriver.objects.filter(bus=bus, driver=driver).exists()
                if not driverasgbus:
                    if AssignedBusesToDriver.objects.filter(driver=driver).exists():
                        driverasgbus = AssignedBusesToDriver.objects.get(driver=driver)
                        driverasgbus.driver = None
                        driverasgbus.save()
                    if AssignedBusesToDriver.objects.filter(bus=bus).exists():
                        driverasgbus = AssignedBusesToDriver.objects.get(bus=bus)
                        driverasgbus.driver = driver
                        driverasgbus.save()
                    else:
                        driverasgbus = AssignedBusesToDriver(bus=bus, driver=driver)
                        driverasgbus.save()
                    messages.success(request, 'Driver Assigned Successfully!')
                else:
                    messages.warning(request, 'Driver Already Assigned to this Bus!')
            except Exception as e:
                messages.warning(request, e)
        try:
            buses = Bus.objects.all()
            drivers = Driver.objects.all()
            bustodriver = AssignedBusesToDriver.objects.all()
        except Exception as e:
            messages.warning(request, e)
        return {'request': request, 'buses': buses, 'drivers': drivers, 'bustodriver': bustodriver}

    @staticmethod
    def fares(request):
        fares = None
        routetobus = None
        midpoints = None
        if request.method == "POST":
            try:
                data = request.POST
                src = data['inputSrc']
                dst = data['inputDest']
                mp1 = True
                mp2 = True
                if src and dst and src == dst:
                    messages.warning(request, 'Source and Destination cannot be same!')
                else:
                    routetobus = RouteAssignedToBus.objects.get(id=data['inputRoute'])
                    if src and dst:
                        src = Terminal.objects.get(id=int(src))
                        dst = Terminal.objects.get(id=int(dst))
                        mp1 = Midpoint.objects.filter(route=routetobus.route, terminal=src).exists()
                        mp2 = Midpoint.objects.filter(route=routetobus.route, terminal=dst).exists()
                        if not mp1:
                            messages.warning(request, 'Source does not belong to route!')
                        if not mp2:
                            messages.warning(request, 'Destination does not belong to route!')
                    elif src:
                        src = Terminal.objects.get(id=int(src))
                        dst = routetobus.route.destination
                        mp1 = Midpoint.objects.filter(route=routetobus.route, terminal=src).exists()
                        if not mp1:
                            messages.warning(request, 'Terminal does not belong to route!')
                    elif dst:
                        src = routetobus.route.source
                        dst = Terminal.objects.get(id=int(dst))
                        mp2 = Midpoint.objects.filter(route=routetobus.route, terminal=dst).exists()
                        if not mp2:
                            messages.warning(request, 'Terminal does not belong to route!')
                    else:
                        src = routetobus.route.source
                        dst = routetobus.route.destination
                    fare = Fares.objects.filter(route_asg_to_bus=routetobus, source=src, destination=dst).exists()
                    print(mp1, mp2)
                    if not fare and mp1 and mp2:
                        fare = Fares(route_asg_to_bus=routetobus, source=src, destination=dst, fare=data['inputFare'])
                        fare.save()
                        messages.success(request, 'Fare assigned successfully!')
                    elif mp1 and mp2:
                        fare = Fares.objects.get(route_asg_to_bus=routetobus, source=src, destination=dst)
                        fare.fare = data['inputFare']
                        fare.save()
                        messages.success(request, 'Fare updated successfully!')
            except Exception as e:
                messages.warning(request, e)
        try:
            fares = Fares.objects.all()
            routetobus = RouteAssignedToBus.objects.all()
            midpoints = Midpoint.objects.all()
        except Exception as e:
            messages.warning(request, e)
        return {'request': request, 'fares': fares, 'routetobus': routetobus, 'midpoints': midpoints}
                