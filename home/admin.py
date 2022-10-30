from django.contrib import admin
from home.models import Bus, Driver, Route, Passenger, Terminal, Tickets, Fares, Refund, AssignedBusesToDriver, RouteAssignedToBus, Schedule, UserofTerminal, UserData

# Register your models here.
admin.site.register([Bus, Driver, Route, Passenger, Terminal, Tickets, Fares, Refund, AssignedBusesToDriver, RouteAssignedToBus, Schedule, UserofTerminal, UserData])