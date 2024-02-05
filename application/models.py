from django.db import models
import datetime

class UserData(models.Model):
    Name=models.CharField(max_length=30,default="")
    Email=models.CharField(max_length=30,default="")
    Number=models.IntegerField(default="")
    Password=models.CharField(max_length=30,default="")
    PAN=models.CharField(max_length=30,default="")
    Balance=models.IntegerField(default="0")

class LoanData(models.Model):
    #receiving while applying
    Borrower=models.CharField(max_length=30,default="")
    BorrowerMail=models.CharField(max_length=30,default="")
    ApplicationDate=models.DateField(default=datetime.datetime.now)
    ApplicationTime=models.TimeField(default=datetime.datetime.now)
    LoanAmount=models.IntegerField(default="")
    InterestPercentage=models.IntegerField(default="")
    TermMonths=models.IntegerField(default="")
    #calculating based on input
    Monthly=models.IntegerField(default="")
    NetEarnings=models.IntegerField(default="")
    NextRepayment=models.DateField(default=datetime.datetime.now)
    #receiving while sanctioning
    Status=models.IntegerField(default="")
    Lender=models.CharField(max_length=30,default="")
    LenderMail=models.CharField(max_length=30,default="")
    SanctionDate=models.DateField(default=datetime.datetime.now)
    SanctionTime=models.TimeField(default=datetime.datetime.now)

class TransactionData(models.Model):
    TransactionID=models.CharField(max_length=30,default="")
    Purpose=models.CharField(max_length=30,default="")
    TransactionDate=models.DateField(default=datetime.datetime.now)
    TransactionTime=models.TimeField(default=datetime.datetime.now)
    BorrowerUsername=models.CharField(max_length=30,default="")
    LenderUsername=models.CharField(max_length=30,default="")
    Amount=models.IntegerField(default="")
    LenderMail=models.CharField(max_length=30,default="")
    BorrowerMail=models.CharField(max_length=30,default="")
    LenderBalance=models.IntegerField(default="0")
    BorrowerBalance=models.IntegerField(default="0")
    

class NotificationData(models.Model):
    LenderMail=models.CharField(max_length=100,default="")
    BorrowerMail=models.CharField(max_length=100,default="")
    Message=models.CharField(max_length=100,default="")
    Time=models.TimeField(default=datetime.datetime.now)
    Date=models.DateField(default=datetime.datetime.now)

class RoomData(models.Model):
    Room_ID=models.CharField(max_length=100,default="")

class MessageData(models.Model):
    Room_ID=models.CharField(max_length=100,default="")
    SenderName=models.CharField(max_length=30,default="")
    SenderMail=models.CharField(max_length=100,default="")
    ReceiverName=models.CharField(max_length=30,default="")
    ReceiverMail=models.CharField(max_length=100,default="")
    Message=models.CharField(max_length=100000,default="")
    DateTime=models.CharField(max_length=100000,default="")
