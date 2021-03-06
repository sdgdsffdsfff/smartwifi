from django.shortcuts import render, redirect, get_object_or_404, render_to_response, get_list_or_404
import json
from django.http import HttpResponse, HttpResponseRedirect, Http404
from datetime import datetime, date, time, timedelta
from management.models import Gateway, WifiClient, Ad, AdStat
from django.utils import timezone


def login(request):
    gw_address = request.GET.get('gw_address')
    gw_port = request.GET.get('gw_port')
    gw_id = request.GET.get('gw_id')
    mac = request.GET.get('mac')
    url = request.GET.get('url')

    if request.method == 'POST':
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        print mobile, password
        if mobile and password is None:
            #TODO send SMS to get password
            pass
        elif mobile and password:
            #TODO verify password
            import uuid
            token = uuid.uuid1()
            print token
            gateway = get_object_or_404(Gateway, pk=gw_id)
            try:
                client = get_object_or_404(WifiClient, mac=mac)
            except Http404:
                client = WifiClient(phone=mobile, mac=mac)
            client.gateway = gateway
            client.token = token
            client.last_login = datetime.today()
            client.save()

            #save url in session
            request.session['url'] = url
            request.session['token'] = token

            redirect_url = 'http://{}:{}/wifidog/auth?token={}'.format(gw_address, gw_port, token)
            return HttpResponseRedirect(redirect_url)

    return render(request, 'api/login.html')


def auth(request):
    stage = request.GET.get('stage')
    ip = request.GET.get('ip')
    mac = request.GET.get('mac')
    token = request.GET.get('token')
    incoming = request.GET.get('incoming')
    outgoing = request.GET.get('outgoing')

    if mac and token:
        if token == request.session.get('token'):
            data = {'Auth': 1}
    else:
        data = {'Auth': 1}

    return HttpResponse(json.dumps(data), content_type="application/json")


def portal(request):
    #TODO
    url = request.session.get('url')
    print url
    if url:
        return HttpResponseRedirect(url)
    else:
        #redirect to ad3
        pass

    return HttpResponse('OK', content_type="application/json")


def ping(request):
    gw_id = request.GET.get('gw_id')
    sys_uptime = request.GET.get('sys_uptime')
    sys_memfree = request.GET.get('sys_memfree')
    sys_memtotal = request.GET.get('sys_memtotal')

    gateway = get_object_or_404(Gateway, id=gw_id)

    #TODO
    data = {'ssid': 'test ssid', 'authmode': 'open', 'password': '11111111', 'channel': 'test', 'pinginterval': 10}

    return HttpResponse(json.dumps(data), content_type="application/json")


def login_ad(request):
    images = []
    result = {}
    ads = Ad.objects.all()
    for ad in ads:
        if ad.ad_img:
            images.append(ad)

    if len(images) > 0:
        import random
        ad = images[random.randint(0, len(images)-1)]
        result['content'] = ad.ad_text
        result['image'] = ad.ad_img.url

        stat = AdStat(ad=ad, showtime=timezone.now())
        stat.save()

    return HttpResponse(json.dumps(result), content_type="application/json")
