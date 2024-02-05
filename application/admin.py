from django.contrib import admin
from application.models import UserData,LoanData,NotificationData,TransactionData,MessageData,RoomData

admin.site.register(UserData)
admin.site.register(LoanData)
admin.site.register(NotificationData)
admin.site.register(TransactionData)
admin.site.register(MessageData)
admin.site.register(RoomData)
