from django.contrib import messages
from django.contrib.auth.models import User
from home.models import UserData, Terminal, UserofTerminal, Terminal
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

    @staticmethod
    def viewUsers(request):
        users = None
        try:
            users = User.objects.all().order_by('-is_active').values()
        except Exception as e:
            messages.warning(request, e)
        return {'request': request, 'Users': users}
    
    @staticmethod
    def editUsers(request, user_id):
        user = None
        udata = None
        uterminal = None
        terminals = None
        if request.method == "POST":
            data = request.POST
            try:
                user = User.objects.get(id=int(user_id))
                udata = UserData.objects.filter(user=user)
                uterminal = UserofTerminal.objects.filter(user=user)
                if data['inputPass']:
                    user.set_password(data['inputPass'])
                user.first_name = data['inputFname']
                user.last_name = data['inputLname']
                user.save()
                if data['inputDob']:
                    udata.update(dob = data['inputDob'], cnic = data['inputCnic'], phone = data['inputPhone'], address = data['inputAddress'])
                else:
                    udata.update(cnic = data['inputCnic'], phone = data['inputPhone'], address = data['inputAddress'])
                terminal = Terminal.objects.get(id = data['inputTerminal'])
                uterminal.update(terminal = terminal)
                messages.success(request, 'User modified successfully!')
            except Exception as e:
                messages.warning(request, e)

        try:
            user = User.objects.get(id=int(user_id))
            udata = UserData.objects.get(user=user)
            uterminal = UserofTerminal.objects.get(user=user)
            terminals = Terminal.objects.all().exclude(id=uterminal.terminal.id)
        except Exception as e:
            messages.warning(request, e)

        return {'request': request, 'User': user, 'udata': udata, 'uterminal': uterminal, 'terminals': terminals}
