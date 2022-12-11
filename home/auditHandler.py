from django.contrib import messages
from home.models import Bus, Driver, Schedule, TicketsAudit, Fares, Voucher, UserofTerminal
from datetime import datetime
from django.shortcuts import HttpResponse
import csv

class AuditHandler():
    @staticmethod
    def returnBuses(request, fromdate = datetime.now().date(), todate = datetime.now().date()):
        try:
            output = []
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            query_set = Bus.objects.filter(created__range=[fromdate, todate])
            #Header
            writer.writerow(['Bus Number', 'Seats', 'Service', 'Model'])
            for bus in query_set:
                output.append([bus.bus_number, bus.seating_capacity, bus.service_type, bus.bus_model])
                #CSV Data
            writer.writerows(output)
        except Exception as e:
            messages.warning(request, e)
        return {'request':request, 'response': response}
    
    @staticmethod
    def returnDrivers(request, fromdate = datetime.now().date(), todate = datetime.now().date()):
        try:
            output = []
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            query_set = Driver.objects.filter(created__range=[fromdate, todate])
            #Header
            writer.writerow(['Name', 'Dob', 'Cnic', 'Phone', 'Address'])
            for driver in query_set:
                output.append([driver.name, str(driver.dob), str(driver.cnic), driver.phone, driver.address])
                #CSV Data
            writer.writerows(output)
        except Exception as e:
            messages.warning(request, e)
        return {'request':request, 'response': response}

    @staticmethod
    def returnSchedules(request, fromdate = datetime.now().date(), todate = datetime.now().date()):
        try:
            output = []
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            query_set = Schedule.objects.filter(created__range=[fromdate, todate], status=True)
            #Header
            writer.writerow(['Departure', 'Arrival', 'Route', 'Bus'])
            for schedule in query_set:
                output.append([str(schedule.departure), str(schedule.arrival), schedule.route_assg_bus.route, schedule.route_assg_bus.bus])
                #CSV Data
            writer.writerows(output)
        except Exception as e:
            messages.warning(request, e)
        return {'request':request, 'response': response}

    @staticmethod
    def returnTickets(request, fromdate = datetime.now().date(), todate = datetime.now().date()):
        try:
            output = []
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            query_set = TicketsAudit.objects.filter(created__range=[fromdate, todate])
            #Header
            writer.writerow(['Ticket Id', 'Departure', 'Arrival', 'Source', 'Destination', 'Fare', 'Seat', 'Bookedby', 'Gender'])
            for ticket in query_set:
                output.append([ ticket.voucher, str(ticket.schedule.departure), str(ticket.schedule.arrival), ticket.source, ticket.destination, ticket.fare, ticket.seat_no, ticket.bookedby.cnic, ticket.gender])
                #CSV Data
            writer.writerows(output)
        except Exception as e:
            messages.warning(request, e)
        return {'request':request, 'response': response}
    
    @staticmethod
    def returnCnics(request, fromdate = datetime.now().date(), todate = datetime.now().date()):
        try:
            output = []
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            query_set = TicketsAudit.objects.filter(created__range=[fromdate, todate])
            #Header
            writer.writerow(['Name', 'Gender', 'Phone', 'Cnic'])
            for ticket in query_set:
                output.append([ ticket.bookedby.name, ticket.bookedby.gender, ticket.bookedby.phone, ticket.bookedby.cnic])
                #CSV Data
            writer.writerows(output)
        except Exception as e:
            messages.warning(request, e)
        return {'request':request, 'response': response}
    
    @staticmethod
    def returnVouchers(request, fromdate = datetime.now().date(), todate = datetime.now().date()):
        try:
            output = []
            response = HttpResponse(content_type='text/csv')
            writer = csv.writer(response)
            userterminal = UserofTerminal.objects.get(user=request.user)
            query_set = Voucher.objects.filter(created__range=[fromdate, todate], terminal=userterminal.terminal)
            #Header
            writer.writerow(['Terminal', 'Destination', 'Voucher#', 'Refreshment', 'Washing', 'Parking', 'Toll', 'IssuedBy'])
            for voucher in query_set:
                output.append([ voucher.terminal, voucher.schedule.route_assg_bus.route.destination, voucher.voucher, voucher.refreshment, voucher.washing, voucher.parking, voucher.toll, voucher.issuedby.get_full_name()])
                #CSV Data
            writer.writerows(output)
        except Exception as e:
            messages.warning(request, e)
        return {'request':request, 'response': response}