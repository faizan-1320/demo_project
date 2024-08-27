from django.db import models
from project.utils import base_model

# Create your models here.
class Coupon(base_model.BaseModel):
    code = models.CharField(max_length=150,unique=True,help_text='Unique coupon code')
    discount_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.0,help_text='Fixed discount amount')
    start_date = models.DateField(help_text='Start date of the coupon validity')
    end_date = models.DateField(help_text='End date of the coupon validity')
    is_active = models.BooleanField(default=True,help_text='Whether the coupon is active or not')
    is_delete = models.BooleanField(default=False,help_text='Whether the coupon is delete or not')
    
    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    def __str__(self):
        return self.code
    
    def is_valid(self):
        from datetime import date
        return self.is_active and self.start_date <= date.today() <= self.end_date
    
    def get_discount(self,total_amount):
        if not self.is_valid():
            return 0
        
        discount = 0 
        if self.discount_amount > 0:
            discount = self.discount_amount
        elif self.discount_percentage > 0:
            discount = total_amount * (self.discount_percentage/100)
        return discount