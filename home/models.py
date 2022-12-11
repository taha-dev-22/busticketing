from statistics import mode
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Driver(models.Model):
    name = models.CharField(max_length=100)
    dob = models.DateField()
    cnic = models.CharField(max_length=13, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    address = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    
    class Meta:
        verbose_name_plural = 'Driver'
    
    def __str__(self):
        return self.name + ' - ' + self.phone

class Bus(models.Model):
    bus_number = models.CharField(max_length=30, unique=True)
    seating_capacity = models.IntegerField()
    service_type = models.CharField(max_length=100)
    bus_model = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Bus'
    
    def __str__(self):
        return self.bus_model + ' - ' + self.bus_number

class Terminal(models.Model):
    tcode = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Terminal'

    def __str__(self):
        return self.name + ' - ' + self.city

class Route(models.Model):
    source = models.ForeignKey(Terminal, related_name='source_terminal', on_delete=models.CASCADE)
    destination = models.ForeignKey(Terminal, related_name='destination_terminal', on_delete=models.CASCADE)
    via = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Route'
    
    def __str__(self):
        return str(self.source) + ' to ' + str(self.destination) + ' via ' + self.via

class Midpoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Midpoint'
    
    def __str__(self):
        return str(self.route) + ' - ' + str(self.terminal)
    
class Passenger(models.Model):
    name = models.CharField(max_length=100)
    gender = models.BooleanField()
    phone = models.CharField(max_length=13)
    cnic = models.CharField(max_length=13)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Passenger'
    
    def __str__(self):
        return self.name + ' - ' + self.phone

class Fares(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    source = models.ForeignKey(Terminal, related_name='fare_source_terminal', on_delete=models.CASCADE)
    destination = models.ForeignKey(Terminal, related_name='fare_destination_terminal', on_delete=models.CASCADE)
    fare = models.IntegerField()
    service_type = models.CharField(max_length=100, default='economy')
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Fares'
    
    def __str__(self):
        return str(self.source) + ' - ' + str(self.destination) + ' - ' + str(self.route)

class Tickets(models.Model):
    voucher = models.CharField(max_length=100, default= None, null= True)
    schedule = models.ForeignKey("Schedule", on_delete=models.CASCADE)
    source = models.ForeignKey(Terminal, related_name='ticket_source_terminal', on_delete=models.CASCADE, default=None, null=True)
    destination = models.ForeignKey(Terminal, related_name='ticket_destination_terminal', on_delete=models.CASCADE, default=None, null=True)
    fare = models.ForeignKey(Fares, on_delete=models.CASCADE)
    discount = models.IntegerField(default=0)
    seat_no = models.IntegerField()
    bookedby = models.ForeignKey("Passenger", on_delete=models.CASCADE)
    gender = models.BooleanField()
    status = models.IntegerField()
    type = models.IntegerField()
    issuedby = models.ForeignKey(User, on_delete=models.CASCADE, default= None, null= True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Tickets'
    
    def __str__(self):
        return str(self.bookedby) + ' - ' + str(self.schedule) + ' - ' + str(self.status)

class Voucher(models.Model):
    terminal = models.ForeignKey(Terminal, on_delete=models.SET_NULL, null=True)
    schedule = models.ForeignKey("Schedule", on_delete=models.SET_NULL, null=True)
    issuedby = models.ForeignKey(User, on_delete=models.CASCADE)
    voucher = models.CharField(max_length=200, unique=True)
    refreshment = models.IntegerField()
    washing = models.IntegerField()
    parking = models.IntegerField()
    toll = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Voucher'
    
    def __str__(self):
        return str(self.voucher) + ' - ' + str(self.schedule)
    
class Refund(models.Model):
    passenger = models.ForeignKey("Passenger", on_delete=models.SET_NULL, null=True)
    schedule = models.ForeignKey("Schedule", on_delete=models.SET_NULL, null=True)
    seats = models.IntegerField()
    amount = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Refund'
    
    def __str__(self):
        return str(self.passenger) + ' - ' + str(self.schedule) + ' - Seats: ' + str(self.seats)

class TicketsAudit(models.Model):
    voucher = models.CharField(max_length=100, default= None, null= True)
    schedule = models.ForeignKey("Schedule", on_delete=models.CASCADE)
    source = models.ForeignKey(Terminal, related_name='ticket_source_audit', on_delete=models.CASCADE, default=None, null=True)
    destination = models.ForeignKey(Terminal, related_name='ticket_destination_audit', on_delete=models.CASCADE, default=None, null=True)
    fare = models.IntegerField()
    discount = models.IntegerField(default=0)
    seat_no = models.IntegerField()
    bookedby = models.ForeignKey("Passenger", on_delete=models.CASCADE)
    gender = models.BooleanField()
    status = models.IntegerField()
    type = models.IntegerField()
    issuedby = models.ForeignKey(User, on_delete=models.CASCADE, default= None, null= True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'TicketsAudit'
    
    def __str__(self):
        return str(self.bookedby) + ' - ' + str(self.schedule) + ' - ' + str(self.status)

class AssignedBusesToDriver(models.Model):
    bus = models.ForeignKey("Bus", on_delete=models.CASCADE)
    driver = models.ForeignKey("Driver", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'AssignedBusesToDriver'
    
    def __str__(self):
        return str(self.bus) + ' - ' + str(self.driver)

class RouteAssignedToBus(models.Model):
    bus = models.ForeignKey("Bus", on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey("Route", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'RouteAssignedToBus'

    def __str__(self):
        return str(self.route) + ' - ' + str(self.bus)

class Schedule(models.Model):
    departure = models.DateTimeField()
    arrival = models.DateTimeField()
    route_assg_bus = models.ForeignKey("RouteAssignedToBus", on_delete=models.CASCADE)
    mid_dept = models.CharField(max_length=500, default=None, null=True)
    status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Schedule'

    def __str__(self):
        return str(self.route_assg_bus.route) + ' - '+': ' + str(self.departure) + ' - ' + str(self.arrival)

class Closedby(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Closedby'

    def __str__(self):
        return str(self.schedule) + '- Closedby: ' + str(self.terminal.city)

class UserofTerminal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    terminal = models.ForeignKey(Terminal, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    
    class Meta:
        verbose_name_plural = 'UserofTerminal'
    
    def __str__(self):
        return self.user.get_username() + ' - ' + str(self.terminal)

class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dob = models.DateField()
    cnic = models.CharField(max_length=13, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    address = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    last_modified = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    
    class Meta:
        verbose_name_plural = 'UserData'
    
    def __str__(self):
        return self.user.get_username() + ' - ' + self.phone
