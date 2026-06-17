from django.db import models # pyright: ignore[reportMissingModuleSource]
class IMSVoiceRecord(models.Model):

    # --- Identification fields ---
    cdfId               = models.CharField(max_length=20,  null=True, blank=True)
    cdrseqnum           = models.IntegerField(null=True, blank=True)
    lclrcdseqnum        = models.IntegerField(null=True, blank=True)
    rcdseqnum           = models.IntegerField(null=True, blank=True)
    cdrtype             = models.IntegerField(null=True, blank=True)

    # --- Call party numbers ---
    callerno            = models.CharField(max_length=32,  null=True, blank=True)
    calledno            = models.CharField(max_length=32,  null=True, blank=True)
    fullcalledno        = models.CharField(max_length=128, null=True, blank=True)
    associatedpartyaddress = models.CharField(max_length=64, null=True, blank=True)
    mediainitiatorparty = models.CharField(max_length=64, null=True, blank=True)

    # --- Call type and service ---
    calltype            = models.IntegerField(null=True, blank=True)
    imschargingid       = models.CharField(max_length=164, null=True, blank=True)
    lrn                 = models.CharField(max_length=10,  null=True, blank=True)
    servicereasonreturncode = models.IntegerField(null=True, blank=True)
    serviceinvoke       = models.IntegerField(null=True, blank=True)
    mmtelservicetype    = models.IntegerField(null=True, blank=True)
    servicekey          = models.IntegerField(null=True, blank=True)
    imsemergencyindicator = models.IntegerField(null=True, blank=True)

    # --- Timestamps ---
    callarrivaltimestamp  = models.CharField(max_length=25, null=True, blank=True)
    callanswertimestamp   = models.CharField(max_length=25, null=True, blank=True)
    callendtimestamp      = models.CharField(max_length=25, null=True, blank=True)
    ringingtimestamp      = models.CharField(max_length=25, null=True, blank=True)
    recordOpeningTime     = models.CharField(max_length=25, null=True, blank=True)
    recordClosingTime     = models.CharField(max_length=25, null=True, blank=True)
    confchangetime        = models.CharField(max_length=25, null=True, blank=True)

    # --- Duration ---
    duration            = models.IntegerField(null=True, blank=True)
    audioduration       = models.IntegerField(null=True, blank=True)
    videoduration       = models.IntegerField(null=True, blank=True)

    # --- Session IDs ---
    initialicid         = models.CharField(max_length=164, null=True, blank=True)
    origincsessionid    = models.CharField(max_length=164, null=True, blank=True)
    termincsessionid    = models.CharField(max_length=164, null=True, blank=True)
    origogsessionid     = models.CharField(max_length=164, null=True, blank=True)
    termogsessionid     = models.CharField(max_length=164, null=True, blank=True)

    # --- Network info ---
    origioi             = models.CharField(max_length=128, null=True, blank=True)
    termioi             = models.CharField(max_length=128, null=True, blank=True)
    origaccessnetworkinfo = models.CharField(max_length=164, null=True, blank=True)
    termaccessnetworkinfo = models.CharField(max_length=164, null=True, blank=True)
    imsvisitednetworkid = models.CharField(max_length=164, null=True, blank=True)
    scscfinformation    = models.CharField(max_length=128, null=True, blank=True)
    asinformation       = models.CharField(max_length=128, null=True, blank=True)
    termscscfinformation = models.CharField(max_length=164, null=True, blank=True)
    termasinformation   = models.CharField(max_length=164, null=True, blank=True)
    termnetworkid       = models.CharField(max_length=164, null=True, blank=True)

    # --- Device and subscriber info ---
    privateuserid       = models.CharField(max_length=128, null=True, blank=True)
    origdeviceip        = models.CharField(max_length=32,  null=True, blank=True)
    termdeviceip        = models.CharField(max_length=32,  null=True, blank=True)
    servedIMEI          = models.CharField(max_length=16,  null=True, blank=True)
    termservedIMEI      = models.CharField(max_length=164, null=True, blank=True)
    subsPLMN            = models.CharField(max_length=6,   null=True, blank=True)
    subsIMSI            = models.CharField(max_length=16,  null=True, blank=True)
    substype            = models.IntegerField(null=True, blank=True)
    termsubsPLMN        = models.CharField(max_length=164, null=True, blank=True)
    termsubsIMSI        = models.CharField(max_length=164, null=True, blank=True)
    termsubstype        = models.IntegerField(null=True, blank=True)

    # --- Cell tower IDs ---
    firstcellIdorig     = models.CharField(max_length=30,  null=True, blank=True)
    lastcellIdorig      = models.CharField(max_length=30,  null=True, blank=True)
    firstcellIdterm     = models.CharField(max_length=30,  null=True, blank=True)
    lastcellIdterm      = models.CharField(max_length=30,  null=True, blank=True)

    # --- Media and codec ---
    codecs              = models.CharField(max_length=64,  null=True, blank=True)
    mediainitiatorflag  = models.IntegerField(null=True, blank=True)
    termcodec           = models.CharField(max_length=164, null=True, blank=True)
    rattype             = models.IntegerField(null=True, blank=True)
    srvcctype           = models.IntegerField(null=True, blank=True)
    accesstransfertype  = models.IntegerField(null=True, blank=True)

    # --- Conference fields ---
    conferenceid        = models.CharField(max_length=36,  null=True, blank=True)
    confnumparticipants = models.IntegerField(null=True, blank=True)
    confparticipationacttype = models.IntegerField(null=True, blank=True)
    confcalledstr       = models.CharField(max_length=164, null=True, blank=True)

    # --- CUG and misc ---
    origcugid           = models.CharField(max_length=20,  null=True, blank=True)
    termcugid           = models.CharField(max_length=20,  null=True, blank=True)
    resourcepri         = models.IntegerField(null=True, blank=True)
    numofdiversions     = models.IntegerField(null=True, blank=True)
    callinggt           = models.CharField(max_length=164, null=True, blank=True)
    callrefernum        = models.CharField(max_length=164, null=True, blank=True)

    # --- Dummy/reserved fields ---
    dummy7              = models.CharField(max_length=164, null=True, blank=True)
    dummy13             = models.IntegerField(null=True, blank=True)
    dummy14             = models.IntegerField(null=True, blank=True)
    dummy15             = models.CharField(max_length=164, null=True, blank=True)
    dummy16             = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'imsvoicerecord'   # exact table name in MySQL

    def __str__(self):
        return f"CDR {self.cdrseqnum} | {self.callerno} → {self.calledno}"
    
    #######
    # cdr_app/models.py
class CDRRule(models.Model):

    OPERATOR_CHOICES = [
        ('equals',      'Equals'),
        ('not_equals',  'Not equals'),
        ('greater',     'Greater than'),
        ('less',        'Less than'),
        ('contains',    'Contains'),
        ('starts_with', 'Starts with'),
        ('ends_with',   'Ends with'),
    ]

    ACTION_CHOICES = [
        ('flag',   'Flag the record'),
        ('alert',  'Raise an alert'),
        ('ignore', 'Ignore the record'),
        ('tag',    'Tag with a label'),
    ]

    name         = models.CharField(max_length=100)
    field_name   = models.CharField(max_length=100)
    operator     = models.CharField(max_length=20, choices=OPERATOR_CHOICES)
    value        = models.CharField(max_length=200)
    action       = models.CharField(max_length=20, choices=ACTION_CHOICES)
    action_label = models.CharField(max_length=100)
    is_active    = models.BooleanField(default=True)

    class Meta:
        db_table = 'cdr_rules'

    def __str__(self):
        return f"{self.name} → if {self.field_name} {self.operator} {self.value}"