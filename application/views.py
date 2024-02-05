from django.shortcuts import render,redirect
from application.models import UserData,LoanData,NotificationData,TransactionData,RoomData,MessageData
import random
import smtplib
from email.message import EmailMessage
import datetime
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment
from django.http import HttpResponse,JsonResponse

def homepage(request):
    return render(request,"homepage.html")

def username(s):
    userName = ""
    for char in s:
        if char=='@':
            return userName
        userName += char

def time(s):
    time=str(s)
    time=time[10:16]
    return time
    
def signup(request):
    if request.method=="POST":
        name=request.POST['name']
        email=request.POST['email']
        number=request.POST['number']
        password=request.POST['password']
        confirmpassword=request.POST['confirmpassword']
        pan=request.POST['pan']

        if UserData.objects.filter(Email=email).exists():
            return render(request,"signup.html",{'error':'Mail ID exists already'})
        if password==confirmpassword:
            object=UserData.objects.create(Email=email,
                                           Name=name,
                                           Number=number,
                                           Password=password,
                                           PAN=pan)
            object.save()
            return redirect('signin')
        else:
            return render(request,"signup.html",{'error':'Passwords do not match'})
    return render(request,"signup.html",{'error':None})

def signin(request):
    if request.method=="POST":
        email=request.POST["mail"]
        password=request.POST["password"]
        if UserData.objects.filter(Email=email,Password=password).exists():
            currentsession = UserData.objects.get(Email=email)
            request.session['name'],request.session['email']=currentsession.Name,currentsession.Email
            request.session['balance']=currentsession.Balance
            request.session['sentotp']=str(random.randint(100000,999999))
            print(request.session['sentotp'])
            sendMail("OTP for SignIn ",request.session['sentotp'],email)
            return redirect('otplogin')
        else:
            return render(request,"signin.html",{'error':'Wrong Credentials'})
    return render(request,"signin.html",{'error':None})

def sendMail(subject,body,to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    mail_id = "kj.personalised.mailclient@gmail.com"
    msg['from'] = mail_id
    password = "ibcaxrdnhnwueagg"
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(mail_id, password)
    server.send_message(msg)
    server.quit()

def otplogin(request):
    if request.method=='POST':
        receivedotp=""
        receivedotp+=str(request.POST['d1'])
        receivedotp+=str(request.POST['d2'])
        receivedotp+=str(request.POST['d3'])
        receivedotp+=str(request.POST['d4'])
        receivedotp+=str(request.POST['d5'])
        receivedotp+=str(request.POST['d6'])
        print(receivedotp)
        if receivedotp==request.session['sentotp']:
            return redirect('dashboard')
        else:
            print("Otp authentication failed.. Try Again")
            return render(request,"signin.html",{'error':'Otp authentication failed.. Try Again'})
    return render(request,'otplogin.html')

def dashboard(request):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    notifications=NotificationData.objects.all()
    return render(request,"dashboard.html",{'name':request.session['name'],'uppercase':request.session['name'].upper(),'balance':request.session['balance'],'error':None,'report':None,'notifications':notifications,'currentusermail':currentuser.Email})

def applyloan(request):
    loans = LoanData.objects.all()
    c=0
    for loan in loans:
        if loan.Borrower==request.session['name'] and loan.Status==1:
            c+=1
            if c>=2:
                break
    if c>=2:
        print("Loan applying limit reached")
        return render(request,"dashboard.html",{'name':request.session['name'],'balance':request.session['balance'],'error':'Loan applying limit reached'})
    if request.method=='POST':
        #receive input 
        loanamount=int(request.POST['loanamount'])
        interestpercentage=int(request.POST['interestpercentage'])
        termmonths=int(request.POST['termmonths'])
        applicationdatetime=datetime.datetime.now()
        #calculations based on input
        r=(interestpercentage / 100) / 12
        emi = loanamount * r * (1 + r) ** termmonths
        emi /= ((1 + r) ** termmonths - 1)
        netearnings=((termmonths*emi)-loanamount)
        #create new object
        application=LoanData()
        application.Borrower=request.session['name']
        application.BorrowerMail=request.session['email']
        application.ApplicationTime=applicationdatetime
        application.ApplicationDate=applicationdatetime
        application.LoanAmount=loanamount
        application.InterestPercentage=interestpercentage
        application.Status='0'
        application.TermMonths=termmonths
        application.Monthly=emi
        application.NetEarnings=netearnings
        application.save()
        #
        print("Loan Applied Successfully")
        #
        #update in Notifications table
        notify=NotificationData()
        notify.Date=application.ApplicationDate
        notify.Time=application.ApplicationTime
        notify.BorrowerMail=request.session['email']
        msg="Loan Applied for "+str(application.LoanAmount)+" @ "+str(application.InterestPercentage)+"%"+" Interest"
        notify.Message=msg
        notify.save()
        return redirect('dashboard')
    return render(request,"applyloan.html",{'name':request.session['name']})

def viewapplications(request):
    loans=LoanData.objects.all()
    return render(request,"viewapplications.html",{'loans':loans,'currentuser':request.session['name'],'currentusermail':request.session['email']})

def sanctionloan(request,id):
    #transfer balance
    selectedapplication=LoanData.objects.get(id=id)
    currentuser=UserData.objects.get(Email=request.session['email']) 
    if currentuser.Balance>=selectedapplication.LoanAmount:
        objects=UserData.objects.all()
        for ob in objects:
            if ob.Email==selectedapplication.BorrowerMail:
                ob.Balance=ob.Balance+selectedapplication.LoanAmount
                currentuser.Balance=currentuser.Balance-selectedapplication.LoanAmount
                email=ob.Email
                ob.save()
                currentuser.save()
                break
        #Update Sanction in LoanData Table
        selectedapplication.Status='1'
        selectedapplication.Lender=currentuser.Name
        selectedapplication.LenderMail=currentuser.Email
        selectedapplication.SanctionDate=datetime.datetime.now()
        selectedapplication.SanctionTime=datetime.datetime.now()
        #Next Repayment calculation
        nextrepayment=datetime.datetime.now()
        m=nextrepayment.month+1
        mod_date=nextrepayment.replace(month=m)
        selectedapplication.NextRepayment=mod_date
        selectedapplication.save()
        #NotificationData table
        notify=NotificationData()
        notify.Date=datetime.datetime.now()
        notify.Time=datetime.datetime.now()
        notify.BorrowerMail=email
        notify.LenderMail=currentuser.Email
        msg="Loan Sanctioned to "+str(selectedapplication.Borrower)+" by "+str(selectedapplication.Lender)+" for ₹ "+str(selectedapplication.LoanAmount)
        notify.Message=msg
        notify.save()
        #Mail Notification
        date=str(selectedapplication.SanctionDate)
        date=date[:10]
        time=str(selectedapplication.SanctionTime)
        time=time[10:16]
        body="Your loan application for " +str(selectedapplication.LoanAmount)+" was sanctioned by "+str(selectedapplication.Lender)+" on "+str(date)+" by "+str(time)+"."+" Current Balance : "+str(currentuser.Balance)
        sendMail("Loan Sanction",body,email)
        #TransactionData Table
        transactiondata=TransactionData()
        transactiondata.TransactionID=username(selectedapplication.BorrowerMail)+":"+date+":"+username(selectedapplication.LenderMail)
        transactiondata.Purpose="Loan Sanction"
        transactiondata.TransactionDate=datetime.datetime.now()
        transactiondata.TransactionTime=datetime.datetime.now()
        transactiondata.BorrowerUsername=selectedapplication.Borrower
        transactiondata.LenderUsername=currentuser.Name
        transactiondata.LenderMail=currentuser.Name
        transactiondata.BorrowerMail=selectedapplication.BorrowerMail
        transactiondata.Amount=selectedapplication.LoanAmount
        transactiondata.BorrowerBalance=ob.Balance
        transactiondata.LenderBalance=currentuser.Balance
        transactiondata.save()
        return redirect('viewapplications')
    else :
        #
        print("Insufficient Balance")
        #
        return redirect('viewapplications')

def myloans(request):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    loanapplications = LoanData.objects.all()
    return render(request,"myloans.html",{'loanapplications':loanapplications,'currentuser':currentuser})

def updateterms(request,id):
    selectedloan=LoanData.objects.get(id=id)
    if request.method=="POST":
        interest=int(request.POST['interestpercentage'])
        if interest>=15:
            loanamount=int(selectedloan.LoanAmount)
            interestpercentage=int(request.POST['interestpercentage'])
            termmonths=int(request.POST['termmonths'])
            r=interestpercentage/1200
            emi=(loanamount*r*(1+r)**termmonths)/(((1+r)**termmonths)-1)
            netearnings=((termmonths*emi)-loanamount)
            selectedloan.TermMonths=termmonths
            selectedloan.InterestPercentage=interestpercentage
            selectedloan.Monthly=emi
            selectedloan.NetEarnings=netearnings
            selectedloan.ApplicationDate=datetime.datetime.now()
            selectedloan.ApplicationTime=datetime.datetime.now()
            selectedloan.save()
            #
            print("Loan Terms updated successfully")
            return redirect('myloans')
    return render(request,"updateterms.html",{'selectedloan':selectedloan})

def trackrepayments(request):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    loanapplications = LoanData.objects.all()
    return render(request,"trackrepayments.html",{'username':currentuser.Name,'loanapplications':loanapplications})

def deposit(request):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    if request.method=="POST":
        global deposit_amount,orderid
        deposit_amount=int(request.POST["amount"])*100
        orderid=""
        orderid+=currentuser.Name
        orderid+=str(datetime.datetime.now())
        return render(request,"payment.html",{'amount':deposit_amount})
    return render(request, "deposit.html")

def success(request,amount):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    #Updated Balance in UserData
    existing=int(currentuser.Balance)
    deposit_amount=amount/100
    currentuser.Balance=existing+deposit_amount
    currentuser.save()
    #Update TransactionData
    transactiondata=TransactionData()
    transactiondata.TransactionID=orderid
    transactiondata.Purpose="Deposit"
    transactiondata.TransactionDate=datetime.datetime.now()
    transactiondata.TransactionTime=datetime.datetime.now()
    transactiondata.BorrowerUsername=currentuser.Name
    transactiondata.LenderUsername=currentuser.Name
    transactiondata.Amount=deposit_amount
    transactiondata.LenderMail=currentuser.Email
    transactiondata.LenderBalance=currentuser.Balance
    transactiondata.BorrowerBalance=currentuser.Balance
    transactiondata.save()
    #Update NotificationData
    notify=NotificationData()
    notify.Date=datetime.datetime.now()
    notify.Time=datetime.datetime.now()
    notify.LenderMail=currentuser.Email
    msg="Deposit of ₹ "+str(deposit_amount)+" is successful "
    notify.Message=msg
    notify.save()
    return redirect('dashboard')

def report(request):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    workbook = Workbook()
    worksheet = workbook.active
    worksheet['A1']='Transaction ID'
    worksheet['B1']='Purpose'
    worksheet['C1']='Date'
    worksheet['D1']='Time'
    worksheet['E1']='Borrower Name'
    worksheet['F1']='Transaction Amount'
    worksheet['G1']='Lender Name'
    worksheet['H1']='Balance'
    worksheet.row_dimensions.height = 70
    worksheet.column_dimensions['A'].width = 40
    worksheet.column_dimensions['B'].width = 12
    worksheet.column_dimensions['C'].width = 10
    worksheet.column_dimensions['D'].width = 9
    worksheet.column_dimensions['E'].width = 25
    worksheet.column_dimensions['F'].width = 17
    worksheet.column_dimensions['G'].width = 25
    worksheet.column_dimensions['H'].width = 12

    header_row = worksheet[1]
    for cell in header_row:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    #heading row created
    transactions=TransactionData.objects.all()
    for obj in transactions:
        if obj.LenderMail==currentuser.Email: 
            t = [obj.TransactionID,obj.Purpose,str(obj.TransactionDate),str(obj.TransactionTime),obj.BorrowerUsername,obj.Amount,obj.LenderUsername,obj.LenderBalance]#changes needed as per Transactions Database
            worksheet.append(t)
            continue
        if obj.BorrowerMail==currentuser.Email: 
            t = [obj.TransactionID,obj.Purpose,str(obj.TransactionDate),str(obj.TransactionTime),obj.BorrowerUsername,obj.Amount,obj.LenderUsername,obj.BorrowerBalance]#changes needed as per Transactions Database
            worksheet.append(t)
    filename=currentuser.Name+"_"+str(obj.TransactionDate)+".xlsx"
    workbook.save(filename)
    print("REPORT GENERATED")
    return redirect('dashboard')

def notification(request):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    notifications=NotificationData.objects.all()
    return render(request,"notification.html",{'notifications':notifications,'currentusermail':currentuser.Email})

def killsession(request):
    del request.session['name']
    del request.session['email']
    del request.session['balance']
    del request.session['sentotp']
    return redirect('homepage')

def chat(request):
    userdata=UserData.objects.all()
    return render(request,'chat.html',{'userdata':userdata,'currentusermail':request.session['email']})

def manageroom(request,email):
    currentuser=UserData.objects.get(Email=request.session['email']) 
    selecteduser=UserData.objects.get(Email=email)
    request.session['selectedname']=selecteduser.Name
    request.session['selectedmail']=selecteduser.Email
    #Create Room ID
    s = username(currentuser.Email)+username(selecteduser.Email)
    request.session['room_id']=s
    print(s)
    #Check if Room exists already
    roomdata=RoomData.objects.all()
    for x in roomdata:
        if username(currentuser.Email) in x.Room_ID and username(selecteduser.Email) in x.Room_ID:
            print("Room exists")
            request.session['room_id']=x.Room_ID 
            return redirect('message') 
    #Create new room if needed
    room=RoomData.objects.create(Room_ID=request.session['room_id'])
    print("Room created")
    room.save()
    return redirect('message')

def message(request):
    return render(request,"message.html",{'username':request.session['name'],'selectedname':request.session['selectedname']})

def sendmessage(request):
    message=request.POST['message']
    dt=str(datetime.datetime.now())
    #create an object for new_message
    new_message=MessageData.objects.create(Room_ID=request.session['room_id'],
                                        SenderMail=request.session['email'],
                                        SenderName=request.session['name'],
                                        Message=message,
                                        DateTime=dt[10:16],
                                        ReceiverName=request.session['selectedname'],
                                        ReceiverMail=request.session['selectedmail'])
    new_message.save()
    print("Msg sent successfully")
    return HttpResponse('Message sent successfully')


def getmessages(request):
    #get message from MESSAGEDATA table using Room_ID using FILTER
    messages = MessageData.objects.filter(Room_ID=request.session['room_id'])
    #return message_details of this room_id as JSONRESPONSE
    return JsonResponse({"messages":list(messages.values())})

def getbalance(request):
    currentuser=UserData.objects.get(Email=request.session['email'])
    balance=currentuser.Balance
    return HttpResponse(balance,content_type='text/plain')
