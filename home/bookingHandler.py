from home.models import Schedule, Passenger, Tickets, Fares, UserofTerminal, RouteAssignedToBus
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count

class BookingHandler():
    @staticmethod
    def returnBooking(request, schedule_id):
        schedule = Schedule.objects.filter(id=schedule_id)[0]
        if request.method == "POST":
            try:
                data = request.POST
                passenger = Passenger.objects.filter(cnic = data['inputCnic'])
                faresRoute = Fares.objects.get(id=int(data['inputRoute']))
                ps = None
                if passenger:
                    passenger.update(phone = data['inputContact'])
                    ps = passenger[0]
                else:
                    passenger = {'name' : data['inputPasName'], 'gender' : int(data['inputBookedbyGender']), 'phone' : data['inputContact'], 'cnic' : data['inputCnic']}
                    ps = Passenger(name=passenger['name'], gender=passenger['gender'], phone=passenger['phone'], cnic=passenger['cnic'])
                    ps.save()
                seats = [int(i) for i in data['inputSeats'].split(',')]
                genders = [int(i) for i in data['inputGenders'].split(',')]
                fare = Fares.objects.get(id=int(data['inputRoute']))
                for i in range(len(seats)):
                    tk = Tickets(voucher = data['inputVoucher'], schedule = schedule, discount = data['inputDiscount'], source = faresRoute.source, destination = faresRoute.destination, seat_no = seats[i], fare = fare, bookedby = ps, gender = genders[i], status = 1, type = 1, issuedby = request.user)
                    tk.save()
                messages.success(request, 'Tickets has been booked successfully!')
            except Exception as e:
                messages.warning(request, e)
        tickets = Tickets.objects.filter(schedule=schedule_id)
        uterminal = UserofTerminal.objects.get(user=request.user)
        fares = Fares.objects.filter(route_asg_to_bus=schedule.route_assg_bus, source=uterminal.terminal)
        seating = {}
        for i in tickets.values():
            fare = Fares.objects.get(id=i['fare_id'])
            if fare.destination.id == uterminal.terminal.id:
                continue
            bookedincity = fare.source.city
            destcity = fare.destination.city
            gender = i['gender']
            status = i['status']
            seating[i['seat_no']] =  {'gender':gender, 'status':status, 'bookedincity':bookedincity, 'destcity': destcity}
        result = {'schedule': schedule, 'seating': seating, 'range': range(schedule.route_assg_bus.bus.seating_capacity), 'fares': fares}
        dt = {'request': request, 'result': result}
        return dt
    
    @staticmethod
    def cancelBooking(request):
        tickets = None
        passengerfound = False
        if request.method == "POST" and 'find-cnic' in request.POST:
            try:
                cnic = request.POST['inputPasId']
                passenger = Passenger.objects.get(cnic=cnic)
                tickets = Tickets.objects.filter(bookedby=passenger, status=1).annotate(count=Count('schedule'))
                if passenger:
                    passengerfound = True
            except Exception as e:
                if not passengerfound:
                    messages.warning(request, 'Passenger not found!')
                else:
                    messages.warning(request, e.args)
        elif request.method == "POST" and 'find-tickets' in request.POST:
            try:
                tk_ids = dict(request.POST)
                cnic = None
                for i in tk_ids['ticket']:
                    tk = Tickets.objects.get(id=i)
                    cnic = tk.bookedby.cnic
                    tk.delete()
                passenger = Passenger.objects.get(cnic=cnic)
                tickets = Tickets.objects.filter(bookedby=passenger, status=1).annotate(count=Count('schedule'))
                if not tickets:
                    tickets = None
                messages.success(request, 'Booking cancelled successfully!')
            except Exception as e:
                messages.warning(request, e)
        return {'request': request, 'tickets': tickets}
    
    @staticmethod
    def cancelReservation(request):
        tickets = None 
        if request.method == "POST":
            try:
                tk_ids = dict(request.POST)
                schedule = None
                for i in tk_ids['ticket']:
                    tk = Tickets.objects.get(id=i)
                    schedule = tk.schedule
                    tk.delete()
                tickets = Tickets.objects.filter(schedule=schedule, status=1)
                if not tickets:
                    tickets = None
                messages.success(request, 'Booking has been cancelled successfully!')
            except Exception as e:
                messages.warning(request, e)
        return tickets
    
    @staticmethod
    def returnBookingBySchedule(request, schedule_id):
        tickets = Tickets.objects.filter(schedule=schedule_id, status=1)
        return tickets

    @staticmethod
    def bookingdetail(request):
        schedules = []
        billData = {}
        seat_gender = {}
        seats = []
        genders = []
        schedule = None
        vouchers = None
        tickets = None
        uid = None
        if request.method == "POST":
            if 'find-cnic' in request.POST:
                try:
                    passenger = Passenger.objects.get(cnic=request.POST['inputPasId'])
                    uid = passenger.id
                    vouchers = Tickets.objects.filter(bookedby = passenger, status= 1).distinct()
                    if not vouchers:
                        messages.warning(request, 'No Tickets found against this cnic!')
                        vouchers = None
                        uid = None
                except Exception as e:
                    messages.warning(request, 'Passenger not found!')
            elif 'find-seats' in request.POST:
                try:
                    uid = request.POST['inputUid']
                    passenger = Passenger.objects.get(id=request.POST['inputUid'])
                    tickets = Tickets.objects.get(id=request.POST['inputSchedule'])
                    fare = tickets.fare.fare
                    tickets = Tickets.objects.filter(voucher=tickets.voucher)
                    qty = len(tickets)
                    for i in tickets:
                        seat_gender[i.seat_no] = 'M' if i.gender else 'F'
                        billData['voucher'] = i.voucher
                        billData['issuedby'] = i.issuedby
                    for i in sorted(seat_gender.keys()):
                        seats.append(i)
                        genders.append(seat_gender[i])
                    seats = ','.join(map(str, seats))
                    genders = ','.join(map(str, genders))
                    billData['seats'] = seats
                    billData['genders'] = genders
                    billData['qty'] = qty
                    billData['fare'] = fare
                    billData['total'] = fare * qty
                except Exception as e:
                    messages.warning(request, e)
            elif 'Purchase-seats' in request.POST:
                try:
                    passenger = Passenger.objects.get(id=request.POST['inputUid'])
                    schedule = Schedule.objects.get(id=request.POST['inputSid'])
                    tickets = Tickets.objects.filter(bookedby=passenger, schedule= schedule, status=1)
                    for i in tickets:
                        i.status = 2
                        i.save()
                    tickets = None
                    messages.success(request, 'Seats Purchased Successfully!')
                except Exception as e:
                    messages.warning(request, e)
        return {'request': request, 'uid': uid, 'schedules': schedules, 'tickets': tickets, 'vouchers': vouchers, 'billdata': billData}