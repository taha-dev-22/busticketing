from home.models import Refund, Schedule, Passenger, Tickets, Fares, UserofTerminal
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count

class TicketingHandler():
    @staticmethod
    def returnTicketing(request, schedule_id):
        schedule = Schedule.objects.filter(id=schedule_id)[0]
        if request.method == "POST":
            try:
                data = request.POST
                passenger = Passenger.objects.filter(cnic = data['inputCnic'])
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
                for i in range(len(seats)):
                    tk = Tickets(voucher = data['inputVoucher'], schedule = schedule, seat_no = seats[i], bookedby = ps, gender = genders[i], status = 2, type = 1, issuedby = request.user)
                    tk.save()
                messages.success(request, 'Tickets has been purchased successfully!')
            except Exception as e:
                messages.warning(request, e)
        tickets = Tickets.objects.filter(schedule=schedule_id)
        fare = Fares.objects.filter(route_asg_to_bus=schedule.route_assg_bus).values('fare')[0]['fare']
        seating = {}
        for i in tickets.values():
            user = User.objects.get(id=i['issuedby_id'])
            uterminal = UserofTerminal.objects.get(user=user)
            bookedincity = uterminal.terminal.city
            gender = i['gender']
            status = i['status']
            seating[i['seat_no']] =  {'gender':gender, 'status':status, 'bookedincity':bookedincity}
        result = {'schedule': schedule, 'seating': seating, 'range': range(schedule.route_assg_bus.bus.seating_capacity), 'fare': fare}
        dt = {'request': request, 'result': result}
        return dt
    
    @staticmethod
    def cancelTickets(request):
        tickets = None
        passengerfound = False
        ps_id = None
        fares = {}
        if request.method == "POST" and 'find-cnic' in request.POST:
            try:
                cnic = request.POST['inputPasId']
                passenger = Passenger.objects.get(cnic=cnic)
                ps_id = passenger.id
                tickets = Tickets.objects.filter(bookedby=passenger, status=2).annotate(count=Count('schedule'))
                for i in tickets:
                    fare = Fares.objects.get(route_asg_to_bus=i.schedule.route_assg_bus).fare
                    fares[i.id] = fare
                if passenger:
                    passengerfound = True
            except Exception as e:
                if not passengerfound:
                    messages.warning(request, 'Passenger not found!')
                else:
                    messages.warning(request, e.args)
        elif request.method == "POST" and 'find-tickets' in request.POST:
            print(dict(request.POST))
            try:
                tk_ids = dict(request.POST)
                passenger = Passenger.objects.get(id=int(tk_ids['inputPSid'][0]))
                ps_id = passenger.id
                refund = {'bookedby': passenger, 'seats': len(tk_ids['ticket']), 'amount': tk_ids['inputTotal'][0]}
                for i in tk_ids['ticket']:
                    tk = Tickets.objects.get(id=i)
                    refund['schedule'] = tk.schedule
                    tk.delete()
                refund_query = Refund(passenger=refund['bookedby'], schedule=refund['schedule'], seats = refund['seats'], amount = refund['amount'])
                refund_query.save()
                tickets = Tickets.objects.filter(bookedby=passenger, status=2).annotate(count=Count('schedule'))
                if not tickets:
                    tickets = None
                messages.success(request, 'Tickets cancelled successfully!')
            except Exception as e:
                messages.warning(request, e)
        return {'request': request, 'tickets':tickets, 'fares':fares, 'ps_id': ps_id}
    