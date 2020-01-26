from peewee import *

database = MySQLDatabase('TRADER', thread_safe=True,
                         **{'charset': 'utf8', 'use_unicode': True, 'host': 'localhost', 'port': 3306, 'user': 'bot',
                            'password': 'change5_Everything'}, )


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Invitations(BaseModel):
    id = IntegerField(column_name='ID')
    invited = IntegerField(column_name='INVITED')

    class Meta:
        table_name = 'INVITATIONS'
        primary_key = False


class TempDetails(BaseModel):
    btc_address = CharField(column_name='BTC_ADDRESS')
    id = IntegerField(column_name='ID')
    end_time = IntegerField(null=True)

    class Meta:
        table_name = 'TEMP_DETAILS'
        primary_key = False


class Video(BaseModel):
    link = CharField(null=True)

    class Meta:
        table_name = 'VIDEO'
        primary_key = False


class Additional(BaseModel):
    val = IntegerField(null=True)
    var = CharField(primary_key=True)

    class Meta:
        table_name = 'additional'


class AwaitReceipt(BaseModel):
    amount = CharField(null=True)
    comment = CharField(null=True)
    days = IntegerField(null=True)
    uid = IntegerField(null=True)

    class Meta:
        table_name = 'awaitReceipt'
        primary_key = False


class CompletedTransactions(BaseModel):
    tx_hash = CharField(null=True)

    class Meta:
        table_name = 'completedTransactions'
        primary_key = False


class Demo(BaseModel):
    days = IntegerField(null=True)
    id = IntegerField(null=True)
    state = IntegerField(null=True)

    class Meta:
        table_name = 'demo'
        primary_key = False


class LostSubs(BaseModel):
    end_date = TextField(null=True)
    uid = IntegerField(null=True)

    class Meta:
        table_name = 'lost_subs'
        primary_key = False


class Payments(BaseModel):
    end_date = CharField(null=True)
    uid = IntegerField()

    class Meta:
        table_name = 'payments'
        primary_key = False


class Prices(BaseModel):
    days = IntegerField(null=True)
    price = FloatField(null=True)

    class Meta:
        table_name = 'prices'
        primary_key = False


class Users(BaseModel):
    alias = CharField(constraints=[SQL("DEFAULT '@None'")], null=True)
    balance = FloatField(constraints=[SQL("DEFAULT 0.00000000")], null=True)
    first_name = CharField(constraints=[SQL("DEFAULT ''")], null=True)
    last_name = CharField(null=True)
    uid = AutoField()

    class Meta:
        table_name = 'users'
