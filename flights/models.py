from django.db import models

# Create your models here.
class Airport(models.Model):
    code = models.CharField(max_length=9)
    city = models.CharField(max_length=64)
    
    def __str__(self):
        return f"{self.city} ({self.code})"
    
    
class Flight(models.Model):
    # origin = models.CharField(max_length=64)
    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departures")
    # destination = models.CharField(max_length=64)
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arrivals")
    duration = models.IntegerField()
    
    # which returns a string representation of that particular object 
    def __str__(self):
        return f"{self.id}: {self.origin} to {self.destination}"
    
    # for Django Testing
    def is_valid_flight(self):
        return self.origin != self.destination or self.duration > 0
   
   
   
class Passenger(models.Model):
    first_name = models.CharField(max_length=64)    
    last_name = models.CharField(max_length=64)      
    flights = models.ManyToManyField(Flight, blank=True, related_name="passengers")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"