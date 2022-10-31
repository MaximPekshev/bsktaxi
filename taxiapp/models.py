from django.db import models
from simple_history.models import HistoricalRecords
from datetime import datetime
from datetime import date
from django.utils import timezone

import uuid

def calculate_debt(driver_slug):

	try:
		driver = Driver.objects.get(slug=driver_slug)
	except Driver.DoesNotExist:
		driver = None	

	if driver:	
		working_days = Working_day.objects.filter(driver = driver)
		debt = 0
		for day in working_days:
			debt += day.debt_of_day
		driver.debt = debt	
		driver.save_without_historical_record()

def update_cashbox(working_day):

	try:
		cashbox = Cashbox.objects.get(working_day=working_day)
		cashbox.cash = working_day.cash
		cashbox.cash_card = working_day.cash_card
		
		cashbox.save()

	except Cashbox.DoesNotExist:

		if working_day.cash != 0 or working_day.cash_card != 0:
			
			cashbox = Cashbox(
				date=datetime.now(),
				working_day=working_day,
				cash=working_day.cash,
				cash_card=working_day.cash_card,
				)

			cashbox.save_without_historical_record()
	

def get_uuid():
	return str(uuid.uuid4().fields[0])

class Driver(models.Model):
	id 				= models.AutoField(primary_key=True)
	first_name		= models.CharField(max_length = 30, verbose_name = 'Имя')
	second_name		= models.CharField(max_length = 30, verbose_name = 'Фамилия')
	third_name		= models.CharField(max_length = 30, verbose_name = 'Отчество', blank=True, null=True)

	driver_license	= models.CharField(max_length = 15, verbose_name = 'Номер В/У', blank=True, null=True, default='')
	car_number		= models.CharField(max_length = 15, verbose_name = 'Номер А/М', blank=True, null=True, default='')
	car_model		= models.CharField(max_length = 30, verbose_name = 'Марка А/М', blank=True, null=True, default='')
	fuel_card		= models.CharField(max_length = 30, verbose_name = 'Топливная карта', blank=True, null=True, default='')
	fuel_card_2		= models.CharField(max_length = 30, verbose_name = 'Топливная карта 2', blank=True, null=True, default='')

	email 			= models.CharField(max_length = 30, verbose_name='Email', blank=True)

	rate			= models.DecimalField(verbose_name = 'Ставка', max_digits=15, decimal_places=2, blank=True, null=True, default=0)

	active			= models.BooleanField(verbose_name='Активный', default=True)

	slug 			= models.SlugField(max_length=10, verbose_name='Url', blank=True, db_index=True)
	
	debt			= models.DecimalField(verbose_name = 'Долг', max_digits=15, decimal_places=2)

	monday			= models.BooleanField(verbose_name='Понедельник', default=True)
	tuesday			= models.BooleanField(verbose_name='Вторник', default=True)
	wednesday		= models.BooleanField(verbose_name='Среда', default=True)
	thursday		= models.BooleanField(verbose_name='Четверг', default=True)
	friday			= models.BooleanField(verbose_name='Пятница', default=True)
	saturday		= models.BooleanField(verbose_name='Суббота', default=True)
	sunday			= models.BooleanField(verbose_name='Воскресенье', default=True)
	car 			= models.ForeignKey('Car', verbose_name='Автомобиль', on_delete=models.SET_DEFAULT,null=True, blank=True, default=None)

	history = HistoricalRecords()

	def __str__(self):

		return self.second_name

	def save(self, *args, **kwargs):

		if self.slug == "":
			self.slug = get_uuid()


		super(Driver, self).save(*args, **kwargs)
			

	def save_without_historical_record(self, *args, **kwargs):
		self.skip_history_when_saving=True
		try:
			ret = self.save(*args, **kwargs)
		finally:
			del self.skip_history_when_saving
		return ret


	class Meta:
		verbose_name = 'Водитель'
		verbose_name_plural = 'Водители'



class  Working_day(models.Model):

	id 			= models.AutoField(primary_key=True)
	driver 		= models.ForeignKey(Driver, on_delete=models.PROTECT)

	date 		= models.DateField('Дата рабочего дня', auto_now_add = False)

	rate		= models.DecimalField(verbose_name = 'Ставка', max_digits=15, decimal_places=2)
	fuel		= models.DecimalField(verbose_name = 'ГСМ', max_digits=15, decimal_places=2)
	penalties	= models.DecimalField(verbose_name = 'Штрафы', max_digits=15, decimal_places=2)

	cash		= models.DecimalField(verbose_name = 'Наличные', max_digits=15, decimal_places=2)
	cash_card	= models.DecimalField(verbose_name = 'Карта', max_digits=15, decimal_places=2, default=0)

	cashless	= models.DecimalField(verbose_name = 'Безналичные', max_digits=15, decimal_places=2)

	debt_of_day	= models.DecimalField(verbose_name = 'Долг дня', max_digits=15, decimal_places=2)

	slug 		= models.SlugField(max_length=10, verbose_name='Url', blank=True, db_index=True)

	history = HistoricalRecords()

	def save(self, *args, **kwargs):

		if self.slug == "":
			self.slug = get_uuid()

		self.debt_of_day = self.cash + self.cash_card + self.cashless - self.rate - self.fuel - self.penalties
		
		super(Working_day, self).save(*args, **kwargs)
		calculate_debt(self.driver.slug)
		update_cashbox(self)

	def save_without_historical_record(self, *args, **kwargs):
		self.skip_history_when_saving=True
		try:
			ret = self.save(*args, **kwargs)
		finally:
			del self.skip_history_when_saving
		return ret

	class Meta:
		
		verbose_name = 'Рабочий день'
		verbose_name_plural = 'Рабочие дни'


class Cashbox(models.Model):
	id 				= models.AutoField(primary_key=True)
	date 			= models.DateTimeField('Дата операции', auto_now_add = False)

	slug 			= models.SlugField(max_length=15, verbose_name='Url', blank=True, db_index=True)
	working_day 	= models.ForeignKey(Working_day, on_delete=models.PROTECT, blank=True, null=True, default=None)

	cash 			= models.DecimalField(verbose_name = 'Наличные', max_digits=15, decimal_places=2, default=0)
	cash_card 		= models.DecimalField(verbose_name = 'Карта', max_digits=15, decimal_places=2, default=0)

	history = HistoricalRecords()

	def __str__(self):

		return self.slug

	def save(self, *args, **kwargs):

		if self.slug == "":
			self.slug = get_uuid()

		super(Cashbox, self).save(*args, **kwargs)
	
	def save_without_historical_record(self, *args, **kwargs):
		self.skip_history_when_saving=True
		try:
			ret = self.save(*args, **kwargs)
		finally:
			del self.skip_history_when_saving
		return ret

	class Meta:

		verbose_name = 'Движение по кассе'
		verbose_name_plural = 'Движения по кассе'



class Car(models.Model):
	id 			= models.AutoField(primary_key=True)
	slug		= models.SlugField(max_length=10, verbose_name='Url', blank=True, db_index=True)

	car_number 	= models.CharField(max_length = 15, verbose_name = 'Номер', blank=True, null=True, default='')
	car_brand	= models.CharField(max_length = 30, verbose_name = 'Марка', blank=True, null=True, default='')
	car_model 	= models.CharField(max_length = 30, verbose_name = 'Модель', blank=True, null=True, default='')
		
	def __str__(self):

		return self.car_number

	def save(self, *args, **kwargs):

		if self.slug == "":
			self.slug = get_uuid()

		super(Car, self).save(*args, **kwargs)


	class Meta:
		verbose_name = 'Автомобиль'
		verbose_name_plural = 'Автомобили'


class Cost_item(models.Model):
	id 			= models.AutoField(primary_key=True)
	slug		= models.SlugField(max_length=10, verbose_name='Url', blank=True, db_index=True)
	title 		= models.CharField(max_length = 50, verbose_name = 'Наименование')
	parent_item = models.ForeignKey('Cost_item', verbose_name='Родитель', on_delete=models.SET_DEFAULT,null=True, blank=True, default=None)
	is_category = models.BooleanField(verbose_name='Это категория', default=False)
		
	def __str__(self):

		return self.title

	def save(self, *args, **kwargs):

		if self.slug == "":
			self.slug = get_uuid()

		super(Cost_item, self).save(*args, **kwargs)

	# def get_items_without_parent(self):

	# 	return Cost_item.objects.filter(parent_item=None).order_by('title')

	# def get_items_with_parent(self):

	# 	items = []

	# 	for item in Cost_item.objects.all().order_by('title'):
	# 		if item.parent_item:
	# 			items.append(item)

	# 	return items

	def get_childs(self):

		return Cost_item.objects.filter(parent_item=self).order_by('title')	


	class Meta:
		verbose_name = 'Статья затрат'
		verbose_name_plural = 'Статьи затрат'


class Car_cost(models.Model):
	id 			= models.AutoField(primary_key=True)
	car 		= models.ForeignKey('Car', verbose_name='Автомобиль', on_delete=models.PROTECT)
	cost_item	= models.ForeignKey('Cost_item', verbose_name='Статья затрат', on_delete=models.PROTECT)
	cost_date	= models.DateField('Дата документа', auto_now_add = False)
	cost_num	= models.CharField(max_length = 10, verbose_name = 'Номер документа', blank=True, null=True, default='')
	date_of_ex  = models.DateField(auto_now_add = True)
	summ		= models.DecimalField(verbose_name = 'Сумма', max_digits=15, decimal_places=2, default=0)
	comment 	= models.CharField(max_length = 200, verbose_name = 'Комментарий', blank=True, null=True, default='')
	slug		= models.SlugField(max_length=10, verbose_name='Url', blank=True, db_index=True)

	history = HistoricalRecords()
		
	def __str__(self):

		return self.slug

	def save(self, *args, **kwargs):

		if self.slug == "":
			self.slug = get_uuid()

		super(Car_cost, self).save(*args, **kwargs)

	def save_without_historical_record(self, *args, **kwargs):
		self.skip_history_when_saving=True
		try:
			ret = self.save(*args, **kwargs)
		finally:
			del self.skip_history_when_saving
		return ret	

	class Meta:
		verbose_name = 'Расход'
		verbose_name_plural = 'Расходы'
