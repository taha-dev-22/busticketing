from django import template

register = template.Library()

def Range(mx, mn=1):
    return range(mn,mx+1)

register.filter('range', Range)

def returnrem(num,dv):
    return num%dv

register.filter('returnrem', returnrem)

def get_gender(dictionary, key):
    return dictionary[key]['gender']

register.filter('get_gender', get_gender)

def get_status(dictionary, key):
    return dictionary[key]['status']

register.filter('get_status', get_status)

def get_bookedcity(dictionary, key):
    return dictionary[key]['bookedincity']

register.filter('get_bookedcity', get_bookedcity)

def get_destcity(dictionary, key):
    return dictionary[key]['destcity']

register.filter('get_destcity', get_destcity)

def get_item(dictionary, key):
    return dictionary.get(key)

register.filter('get_item', get_item)

def get_fare(fares):
    result = ''
    for fare in range(len(fares)):
        result += str(fares[fare].id) + ':' + str(fares[fare].fare)
        if fare != len(fares):
            result += ';'
    print(result)
    return result[:len(result)-1]

register.filter('get_fare', get_fare)