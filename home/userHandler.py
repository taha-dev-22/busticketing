from django.contrib import messages
from django.contrib.auth.models import User
from home.models import UserData, Terminal, UserofTerminal
from django.db.models import Q
from django.contrib.auth.hashers import make_password
class UserHandler():

    @staticmethod
    def create(request):
        terminals = Terminal.objects.all()
        user = None
        udata = None
        if request.method == "POST":
            data = request.POST
            try:
                user = User.objects.filter(Q(email=data['inputEmail']) | Q(username=data['inputUsername'])).exists()
                udata = UserData.objects.filter(Q(cnic=data['inputCnic']) | Q(phone=data['inputPhone'])).exists()
            except Exception as e:
                messages.warning(request, e)
            if user or udata:
                print(data)
                messages.warning(request, 'User Already Exists!')
            else:
                try:
                    user = User(username = data['inputUsername'], first_name = data['inputFname'], last_name = data['inputLname'], email = data['inputEmail'], password = make_password(data['inputPass']))
                    user.save()
                    udata = UserData(user = user, dob = data['inputDob'], cnic = data['inputCnic'], phone = data['inputPhone'], address = data['inputAddress'])
                    udata.save()
                    terminal = Terminal.objects.get(id = data['inputTerminal'])
                    uterminal = UserofTerminal(user = user, terminal = terminal)
                    uterminal.save()
                    messages.success(request, 'User registered successfully!')
                except Exception as e:
                    messages.warning(request, e)
        return {'request':request, 'terminals':terminals}