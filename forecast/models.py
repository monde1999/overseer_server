from django.db import models

class FloodProneArea(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField(default=100)
    is_monitored = models.BooleanField(default=False)

    class Meta:
        db_table = 'flood_prone_area'

class FloodLevel(models.Model):
    fpa = models.ForeignKey(FloodProneArea, on_delete=models.CASCADE)
    rain_level = models.IntegerField() # weather
    level = models.IntegerField(default=1)
    flood_level = models.IntegerField()
    flood_start = models.IntegerField()
    flood_n = models.IntegerField(default=0)
    level_n = models.IntegerField(default=0)
