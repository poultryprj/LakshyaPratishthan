from django.db import models
from django.contrib.auth.models import User

class Areas(models.Model):
    AreaId = models.AutoField(primary_key=True)
    AreaName = models.CharField(max_length=150, null=True, blank=True)
    AreaStatus = models.CharField(default=1, db_comment="0 = Inactive, 1 = Active", null=True, blank=True)  

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Area_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Area_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Area_deleted_by')

    class Meta:
        db_table = "Areas"

class BloodGroup(models.Model):
    bloodGroupId = models.AutoField(primary_key=True)
    bloodGroupName = models.CharField(max_length=50, null=True, blank=True)
    bloodGroupOrder = models.IntegerField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BloodGroup_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BloodGroup_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BloodGroup_deleted_by')

    class Meta:
        db_table = "BloodGroup"

class Gender(models.Model):
    GenderId = models.AutoField(primary_key=True)
    GenderName = models.CharField(max_length=50, null=True, blank=True)
    GenderOrder = models.IntegerField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Gender_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Gender_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Gender_deleted_by')

    class Meta:
        db_table = "gender"

class Registrations(models.Model):
    registrationId = models.AutoField(primary_key=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    middlename = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    mobileNo = models.IntegerField(max_length=10, null=True, blank=True)
    alternateMobileNo = models.IntegerField(max_length=10, null=True, blank=True)
    bloodGroup = models.ForeignKey(BloodGroup, on_delete=models.SET_NULL, null=True, related_name='Registrations_BloodGroup')
    dateOfBirth = models.DateField(null=True, blank=True)
    zonePreference = models.IntegerField(default=0, db_comment="0 = No preferance, 1 = Front, 2 = Middle, 3 = Back", null=True, blank=True)
    gender = models.IntegerField(default=1, db_comment="1 = Female, 2 = Male",null=True, blank=True)
    aadharNumber = models.IntegerField(max_length=12, null=True, blank=True)
    areaId = models.ForeignKey(Areas, on_delete=models.SET_NULL, null=True, related_name='Registrations_Area')
    address = models.TextField(null=True, blank=True)
    photoFileName = models.CharField(max_length=255, null=True, blank=True)
    idProofFileName = models.CharField(max_length=255, null=True, blank=True)
    voterIdProof = models.CharField(max_length=255, null=True, blank=True)
    dateOfRegistration = models.DateField(null=True, blank=True)
    permanentId = models.IntegerField(null=True, blank=True)
    userId = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Registrations_UserId')

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Registrations_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Registrations_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Registrations_deleted_by')

    class Meta:
        db_table = "Registrations"
     

class YatraStatus(models.Model):
    statusId = models.AutoField(primary_key=True)
    statusName = models.CharField(max_length=255, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraStatus_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraStatus_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraStatus_deleted_by')

    class Meta:
        db_table = "yatra_status"

class YatraRoutes(models.Model):
    yatraRouteId = models.AutoField(primary_key=True)
    yatraRoutename = models.CharField(null=True, blank=True)
    yatraDetails = models.TextField(null=True, blank=True)
    yatraStatus = models.IntegerField(default=1, null=True, blank=True, db_comment="0 = Inactive, 1 = Active")

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraRoute_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraRoute_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraRoute_deleted_by')

    class Meta:
        db_table = "YatraRoutes"

class BusNames(models.Model):
    busNameId = models.AutoField(primary_key=True)
    busName = models.CharField(max_length=150, null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BusNames_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BusNames_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BusNames_deleted_by')

    class Meta:
        db_table = "BusNames"      

class BusSeats(models.Model):
    seatId = models.AutoField(primary_key=True)
    seatName = models.CharField(max_length=100, null=True, blank=True)
    seatStatus = models.CharField(max_length=10,default="1",db_comment="0 = Inactive, 1 = Active",null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BusSeats_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BusSeats_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='BusSeats_deleted_by')

    class Meta:
        db_table = "BusSeats"

class Yatras(models.Model):
    yatraId = models.AutoField(primary_key=True)
    yatraDateTime = models.DateTimeField(null=True, blank=True)
    yatraRouteId = models.ForeignKey(YatraRoutes, on_delete=models.SET_NULL, null=True, related_name='Yatras_yatraRouteId')
    yatraFees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    yatraStartDateTime = models.DateTimeField(null=True, blank=True)
    yatraStatus = models.ForeignKey(YatraStatus, on_delete=models.SET_NULL, null=True, related_name='Yatras_yatrastatus')
    # yatraBusId = models.ForeignKey(YatraBuses, on_delete=models.SET_NULL, null=True, related_name='Yatras_yatraBusId')
    seatNo = models.IntegerField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Yatras_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Yatras_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Yatras_deleted_by')

    class Meta:
        db_table = "Yatras"                    

class YatraBuses(models.Model):
    yatraBusId = models.AutoField(primary_key=True)
    busName = models.CharField(max_length=50, null=True, blank=True)
    busDateTimeStart = models.DateTimeField(null=True, blank=True)
    seatFees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    yatraId = models.ForeignKey(Yatras, on_delete=models.SET_NULL, null=True, related_name='Yatrabuses_yatraId')
    yatraRouteId = models.ForeignKey(YatraRoutes, on_delete=models.SET_NULL, null=True, related_name='Yatrabuses_yatraRouteId')
    busStatus = models.IntegerField(default=1, null=True, blank=True, db_comment="0 = Inactive, 1 = Active")
    busCapacity = models.IntegerField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraBus_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraBus_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='YatraBus_deleted_by')

    class Meta:
        db_table = "YatraBuses"  
             

class Payments(models.Model):
    paymentId = models.AutoField(primary_key=True)
    paymentDateTime = models.IntegerField(null=True, blank=True)  
    registrationId = models.ForeignKey(Registrations, on_delete=models.SET_NULL, null=True, related_name='Payments_registrationId')
    paidAmount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    paymentMode = models.IntegerField(default=1, null=True, blank=True, db_comment="1 = Cash, 2 = UPI,")
    paymentTransactionId = models.CharField(max_length=255, null=True, blank=True)
    paymentPhotoFileName = models.CharField(max_length=255, null=True, blank=True)
    paymentUserId = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Payment_PaymentUserid')

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Payment_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Payment_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Payment_deleted_by')

    class Meta:
        db_table = "Payments"        


class TicketsNew(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    ticket_year = models.IntegerField(null=True, blank=True)
    yatra_id = models.ForeignKey(Yatras, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_yatraId')
    yatra_route_id = models.ForeignKey(YatraRoutes, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_yatraRouteId')
    yatra_bus_id = models.ForeignKey(YatraBuses, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_yatraBusId')
    seat_no = models.IntegerField(null=True, blank=True)
    seat_fees = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    seat_ticket_type = models.IntegerField(null=True, blank=True)
    discount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discount_reason = models.TextField(null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2,null=True, blank=True)
    payment_mode = models.IntegerField(default=1, null=True, blank=True, db_comment="1 = Cash, 2 = UPI,")
    payment_id = models.ForeignKey(Payments, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_payment_Id')
    payment_details = models.TextField(null=True, blank=True)
    payment_proof = models.CharField(max_length=50,null=True, blank=True)
    registration_id = models.ForeignKey(Registrations, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_RegistrationId')
    permanant_id = models.IntegerField(null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_Userid')
    ticket_status_id = models.IntegerField(null=True, blank=True )
    cancel_reason = models.TextField(null=True, blank=True)
    booking_date = models.DateField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TicketsNew_deleted_by')

    class Meta:
        db_table = 'tickets_new'  


class Feedback(models.Model):
    feedbackId = models.AutoField(primary_key=True)
    firstName = models.CharField(max_length=100, null=True, blank=True)
    lastName = models.CharField(max_length=100, null=True, blank=True)
    mobileNo = models.IntegerField(max_length=100, null=True, blank=True)
    areaId = models.ForeignKey(Areas, on_delete=models.SET_NULL, null=True, related_name='Feedback_Area')
    feedbackCategory = models.IntegerField(default=1, null=True, blank=True)
    feedbackText = models.TextField(null=True, blank=True)
    feedbackPhotoURL = models.CharField(max_length=400, null=True, blank=True)
    feedbackDateTime = models.DateTimeField(null=True, blank=True)
    userId = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Feedback_PaymentUserid')

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Feedback_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Feedback_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='Feedback_deleted_by')

    class Meta:
        db_table = "tblFeedbacks"    
        
        
class SMSMaster(models.Model):
    templateId = models.AutoField(primary_key=True)
    templateTitle = models.CharField(max_length=50, null=True, blank=True)
    templateMessageBody = models.TextField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='SMSMaster_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='SMSMaster_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='SMSMaster_deleted_by')

    class Meta:
        db_table = "tblSMSMaster"            
        
        
class SMSTransaction(models.Model):
    smsTransId = models.AutoField(primary_key=True)
    smsTemplateId = models.ForeignKey(SMSMaster, on_delete=models.SET_NULL, null=True, related_name='SMSTransaction_smsTemplateId')
    smsBody = models.TextField(null=True, blank=True)
    registrationId = models.ForeignKey(Registrations, on_delete=models.SET_NULL, null=True, related_name='SMSTransaction_registrationId')
    smsTo = models.CharField(max_length=10, null=True, blank=True)
    smsFrom = models.CharField(max_length=10, null=True, blank=True)
    smsCategory = models.IntegerField(null=True, blank=True)
    smsStatus = models.IntegerField(null=True, blank=True)
    smsSendOn = models.IntegerField(null=True, blank=True)
    smsDeliveredOn = models.IntegerField(null=True, blank=True)
    smsMethod = models.IntegerField(null=True, blank=True)
    smsRequestByUserId = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='SMSTransaction_smsRequestByUserId')

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='SMSTransaction_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='SMSTransaction_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='SMSTransaction_deleted_by')

    class Meta:
        db_table = "tblSMSTransactions"


class TourExpenses(models.Model):
    expenseId = models.AutoField(primary_key=True)
    expenseDateTime = models.DateTimeField(null=True, blank=True)
    expenseTime = models.TimeField(null=True, blank=True)
    expenseAmount = models.DecimalField(max_digits=12, decimal_places=2,null=True, blank=True)
    expenseRemark = models.TextField(null=True, blank=True)
    expenseUserId = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TourExpenses_expenseUserId')

    created_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TourExpenses_created_by')
    last_modified_on = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TourExpenses_modified_by')
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='TourExpenses_deleted_by')

    class Meta:
        db_table = "TourExpenses"        
        

