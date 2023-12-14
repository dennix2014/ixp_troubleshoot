from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from tshoot.all_choices import locations


class Switch(models.Model):
    name = models.CharField(unique=True, max_length=255)
    ipv4addr = models.CharField(unique=True, max_length=255)
    oem = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY CASCADE'.format(cls._meta.db_table))


class MemberDetails(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)
    asn = models.IntegerField(blank=True, null=True)
    ipv4addr = models.CharField(unique=True, max_length=255, blank=True, null=True)
    connected_ports = models.CharField(max_length=255)
    switch = models.ForeignKey(Switch, on_delete=models.CASCADE)
    peering_policy = models.CharField(max_length=255)
    speed = models.IntegerField()

    def __str__(self):
        return f'{self.name}'

    @property
    def interface_description(self):
        return [item.split('_')[1] for item in self.connected_ports]


    @property
    def raw_speed(self):
        return sum(self.speed)

    @property
    def member_name_asn(self):
        return f'{self.speed}-{self.asn}'

    @property
    def total_speed(self):
        speed = sum(self.speed)
        if speed > 100:
            return f'{int(speed/1000)}G'
        else:
            return f'{speed}M'


    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY CASCADE'.format(cls._meta.db_table))


