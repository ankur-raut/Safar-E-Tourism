from django.http import HttpResponse,JsonResponse, StreamingHttpResponse
from django.shortcuts import render, redirect
from qrcode import *
import razorpay
from pyzbar.pyzbar import decode
from .models import Tickett
from django.http import StreamingHttpResponse
import cv2
from .models import Tickett
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .mail import sendMail
from django.contrib.auth.views import LoginView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from datetime import date
import cv2
import numpy as np
import cv2
from datetime import datetime, timedelta
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate,login
@csrf_exempt
def book(request):
    global Tickett
    print(request.POST)
    name=request.POST["name"]
    city=request.POST['city']
    monument=request.POST['monument']
    date=request.POST['date']
    print(date)
    email=request.POST['emailID']
    count=request.POST['count']
    price=request.POST['price']
    total_cost=int(float(price))*int(count)
    global payment
    client = razorpay.Client(auth=('rzp_test_A0pbku9Y5vKP6Z', 'V70rauYt6WIeDQi7vfMmhQD5'))        # create Razorpay client
    response_payment = client.order.create(dict(amount=total_cost*100,
                                                    currency='INR')
                                               )# create order
    order_id = response_payment['id']
    order_status = response_payment['status']
    if order_status == 'created':
        Ticket=Tickett(name=name, city=city, monument =monument, date=date, email=email, count=count, ticket_price=price, total_cost=total_cost,order_id=order_id)
        Ticket.save()
        response_payment['name'] = name
        print(response_payment)
        # return Response(response_payment)
        return render(request,'coffee_payment.html',{ 'payment': response_payment})    

    return redirect("homepage")

def payment_status(request):
    response = request.POST
    params_dict = {
        'razorpay_order_id': response['razorpay_order_id'],
        'razorpay_payment_id': response['razorpay_payment_id'],
        'razorpay_signature': response['razorpay_signature']
    }

    # client instance
    client = razorpay.Client(auth=('rzp_test_A0pbku9Y5vKP6Z', 'V70rauYt6WIeDQi7vfMmhQD5'))
    status = client.utility.verify_payment_signature(params_dict)
    cold_coffee = Tickett.objects.get(order_id=response['razorpay_order_id'])
    cold_coffee.razorpay_payment_id = response['razorpay_payment_id']
    cold_coffee.paid = True
    cold_coffee.save()
    delete_unpaid()
    img=make(response['razorpay_order_id'])
    img_path = "Frontend/build/static/Generated_QR/test.png"
    img.save(img_path)
    context_dict={
                    'name': cold_coffee.name,
                    'date':cold_coffee.date,
                    'city':cold_coffee.city,
                    'monument': cold_coffee.monument,
                    'count':cold_coffee.count,
                    'total_cost':cold_coffee.total_cost,
                    'img':img_path,
                    'status': True,
                    'id':response['razorpay_order_id']
                }
    
    
    sendMail(cold_coffee.email, response['razorpay_order_id'],cold_coffee,context_dict)
    print("hi")
    return render(request, 'payment_status.html', context_dict)
        
    # except:
    #     return render(request, 'payment_status.html', {'status': False})
from django.template.loader import get_template
from django.template import Context
from xhtml2pdf import pisa
from io import StringIO, BytesIO
import cgi
# import fitz

def write_pdf(template_src, context_dict, filename, cold_coffee):
    template = get_template(template_src)
    context = (context_dict)
    html  = template.render(context)
    result = open(filename, 'wb') # Changed from file to filename
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    result.close()
 
    doc = fitz.open(filename)
    page = doc.loadPage(0)  # number of page
    pix = page.get_pixmap()
    output = 'qrscan/Final_tickets/'+cold_coffee.order_id+'.png'
    pix.save(output)

def delete_unpaid():
    objects = Tickett.objects.filter(paid=False)
    objects.delete()



def homepage(request):
    return redirect("react_app")  
 
def pay(request,total_cost):
    global payment
    client = razorpay.Client(auth=("rzp_test_A0pbku9Y5vKP6Z", "V70rauYt6WIeDQi7vfMmhQD5"))
    data = {"amount": total_cost*100, "currency": "INR", "receipt": "order_rcptid_11"}
    payment = client.order.create(data=data)
    print(payment)
    return render(request,'pay.html',{"payment":payment,"id":payment['id']})


def Call_Scan(request):
    displaytext=""
    vid = cv2.VideoCapture(0)
    vid.set(3,640)
    vid.set(4,740)
    counter=0
    global status
    while True:
        success, img = vid.read()
        for barcode in decode(img):
            displaytext=""
            text = barcode.data.decode('utf-8')
            text=str(text)
            print(text)
            verified=Tickett.objects.get(order_id=text)
            if Tickett.objects.filter(order_id=text).exists(): 
                if verified.verified==False:
                    color=(0,255,0)
                    displaytext = "Access Granted"
                    verified.verified=True

                    now = datetime.now()
                    print("NOW: ",now)
                    expire = now + timedelta(minutes=0.5)

                    verified.timevalid = expire
                    verified.save()
                    print("VALID TILL: ",verified.timevalid)

                else:
                    if datetime.now()<verified.timevalid.replace(tzinfo=None):
                        color=(0,255,0)
                        displaytext = "Access Granted"
                        status=True
                        return render(request,"sc.html",{"displaytext":displaytext,"status":status}) 

                    else:
                        color=(0,0,255)
                        displaytext =  "Unauthorised Access"
                        status=False
                        return render(request,"sc.html",{"displaytext":displaytext,"status":status})
                
            else:
                color=(0,0,255)
                displaytext =  "Unauthorised Access"
                status=False
                return render(request,"sc.html",{"displaytext":displaytext,"status":status})
              
        



@csrf_exempt
def login_page(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        seo_specialist = authenticate(username=username, password=password)
        if seo_specialist is not None:
            login(request,seo_specialist)
            return redirect("AdminPage")
        else:
            return redirect("/react/") 




class TaskList(ListView):
    template_name='ticket.html'
    model = Tickett
    context_object_name = 'Ticket'
    def get_queryset(self):
        return Tickett.objects.filter(verified=True)


@login_required(login_url='/react/admin')
def Admin(request):
    count=0
    counter={}
    today=date.today()
    d3 = today.strftime("%Y-%m-%d")
    customers = Tickett.objects.filter(date=d3,verified=True)
    for id in customers:
        count=count+ id.count
    return render(request,"SCANNER.html",{"count":count})


@login_required(login_url='/react/admin')
def Counter(request):
    count=0
    counter={}
    today=date.today()
    d3 = today.strftime("%Y-%m-%d")

    customers = Tickett.objects.filter(date=d3,verified=True)
    monuments   = customers.values_list("monument", flat=True)
    monuments=set(monuments)
    for m in monuments:
        count=0
        mo= Tickett.objects.filter(date=d3,verified=True,monument=m)
        for id in mo:
            count=count+id.count
        counter[m]=count
    print(counter)

       
    return render(request,"counter.html",{"counter":counter})


def gen_frames():  
    camera = cv2.VideoCapture(0)

    while True:
        success, frame = camera.read()  
        try:
            if not success:
                break
            else:
                for barcode in decode(frame):
                    text = barcode.data.decode('utf-8')
                    text=str(text) # Order ID String
                    print(text) 
                    verified=Tickett.objects.get(order_id=text) #Object Returned
                    if Tickett.objects.filter(order_id=text).exists(): 
                        if verified.verified==False:
                            color=(0,255,0)
                            displaytext = "Access Granted"
                            verified.verified=True

                            now = datetime.now()
                            print("NOW: ",now)
                            expire = now + timedelta(minutes=0.5)

                            verified.timevalid = expire
                            verified.save()
                            print("VALID TILL: ",verified.timevalid)

                        else:
                            if datetime.now()<verified.timevalid.replace(tzinfo=None):
                                color=(0,255,0)
                                displaytext = "Access Granted"
                            else:
                                color=(0,0,255)
                                displaytext =  "Unauthorised Access"
                        
                    else:
                        color=(0,0,255)
                        displaytext =  "Unauthorised Access"
                    
                    polygon_Points = np.array([barcode.polygon], np.int32)
                    polygon_Points=polygon_Points.reshape(-1,1,2)
                    rect_Points= barcode.rect
                    cv2.polylines(frame,[polygon_Points],True,color, 3)
                    frame=cv2.putText(frame, displaytext, (rect_Points[0],rect_Points[1]), cv2.FONT_HERSHEY_PLAIN, 0.9, color, 2)
                    
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') # concat frame one by one and show result
        except:
            color=(0,0,255)
            displaytext =  "Unauthorised Access"

            polygon_Points = np.array([barcode.polygon], np.int32)
            polygon_Points=polygon_Points.reshape(-1,1,2)
            rect_Points= barcode.rect
            cv2.polylines(frame,[polygon_Points],True,color, 3)
            frame=cv2.putText(frame, displaytext, (rect_Points[0],rect_Points[1]), cv2.FONT_HERSHEY_PLAIN, 0.9, color, 2)
                    
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') # concat frame one by one and show result



def ScanQR(self):
    #Video streaming route. Put this in the src attribute of an img tag
    print(gen_frames())
    return StreamingHttpResponse(gen_frames(), content_type="multipart/x-mixed-replace;boundary=frame")    



class MyReactView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        return {'context_variable': 'value'}
