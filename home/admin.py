from django.contrib import admin
from home.models import Bus, Driver, Route, Passenger, Terminal, Tickets, Fares, Refund, AssignedBusesToDriver
from home.models import RouteAssignedToBus, Schedule, UserofTerminal, UserData, Voucher, Midpoint, Closedby, TicketsAudit
# Register your models here.
admin.site.register([Bus, Driver, Route, Passenger, Terminal, Tickets, Fares, Refund, AssignedBusesToDriver, RouteAssignedToBus,
 Schedule, UserofTerminal, UserData, Voucher, Midpoint, Closedby, TicketsAudit])