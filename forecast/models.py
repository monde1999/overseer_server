from django.db import models

class FloodProneArea(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    radius = models.FloatField(default=100)

    class Meta:
        db_table = 'flood_prone_area'

class FloodLevel(models.Model):
    fpa = models.ForeignKey(FloodProneArea, on_delete=models.CASCADE)
    rain_level = models.IntegerField()
    flood_level = models.IntegerField()
    flood_start = models.IntegerField()