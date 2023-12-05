import datetime 
import time
import requests
import json
from decimal import Decimal
from decouple import config
import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .models import Driver, Working_day
from bsktaxi.settings import BASE_DIR
log_file_path = os.path.join(BASE_DIR, 'log/log.txt')

# создание рабочих дней активных водителей
def creating_working_days():
    drivers = Driver.objects.filter(active=True)
    for driver in drivers:
        today = datetime.datetime.weekday(datetime.datetime.today())
        if today == 0:
            if driver.monday == True:
                dr_rate = driver.rate
            else:
                dr_rate = 0
        elif today == 1:
            if driver.tuesday == True:
                dr_rate = driver.rate
            else:
                dr_rate = 0
        elif today == 2:
            if driver.wednesday == True:
                dr_rate = driver.rate
            else:
                dr_rate = 0
        elif today == 3:
            if driver.thursday == True:
                dr_rate = driver.rate
            else:
                dr_rate = 0
        elif today == 4:
            if driver.friday == True:
                dr_rate = driver.rate
            else:
                dr_rate = 0
        elif today == 5:
            if driver.saturday == True:
                dr_rate = driver.rate
            else:
                dr_rate = 0
        elif today == 6:
            if driver.sunday == True:
                dr_rate = driver.rate
            else:
                dr_rate = 0
        else:
            dr_rate = 0
        new_working_day = Working_day(
            driver=driver,
            date=datetime.datetime.today(),
            rate=dr_rate,
            fuel=0,
            penalties=0,
            cash=0,
            cash_card=0,
            cashless=0,
            )
        new_working_day.save()

# Загрузка общего списка тразакций по парку.
def get_park_transactions(fromTime, toTime):
	url = 'https://fleet-api.taxi.yandex.net/v2/parks/transactions/list'
	headers = {'Accept-Language': 'ru',
			'X-Client-ID': config('YA_X_CLIENT_ID'),
			'X-API-Key': config('YA_X_API_KEY')}
	data = {
		"limit": 1000,
		"query": {
			"park": {
				"id": config('YA_ID'),
				"transaction": {
					"category_ids": ['partner_service_manual'],
					"event_at": {
						"from": fromTime,
						"to": toTime
					}
				}
			}
		}
	}
	answer = None
	for i in range(20):
		time.sleep(1)
		try:
			answer = requests.post(url, headers=headers, data=json.dumps(data),)
			transactions = answer.json().get('transactions')
			amount = 0
			qty = len(transactions)
			for item in transactions:
				item_amount = Decimal(abs(float(item.get('amount'))))
				amount += item_amount
			try:
				date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				lines = [
					'{} {} {}'.format(date, url, str(answer.status_code)),
					'{} из Яндекс получено {} транзакций, на сумму {} р.'.format(date, qty, amount.quantize(Decimal("1.00")))
				]
				with open(log_file_path, 'a+') as file:
					for line in lines:
						file.write(line)
						file.write('\n')
			except:
				pass
		except:
			continue
		if answer.status_code == 200:
			break
		time.sleep(i*3)
	if answer:
		return answer.json().get('transactions')
	else:
		return []
	
# Получаем из базы данных водителя по номеру водительского удостоверения (Номер получаем из API Яндекс)
# Если не находим водителя, товозваращаем данные из API Яндекс о водителе
# Если находим водителя, то записываем Яндекс.ID в карточку
def get_driver_by_licence(driver_profile_id):
	drivers_list_url = 'https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/list'
	dr_headers = {'Accept-Language': 'ru',
               'X-Client-ID': config('YA_X_CLIENT_ID'),
               'X-API-Key': config('YA_X_API_KEY')}
	driver_data = {
                "fields": {
					"driver_profile": [
                        "driver_license",
						"first_name",
						"last_name",
						"middle_name"
                    ]
                },
                "query": {
                      "park": {
						"driver_profile": {
							"id": [
								driver_profile_id
							]
						},
                        "id": config('YA_ID')
                      },
                },
    }
	for i in range(10):
		answer = requests.post(drivers_list_url, headers=dr_headers, data=json.dumps(driver_data))	
		if answer.status_code == 200:
			break
		elif answer.status_code == 429:
			time.sleep(i*2)
	if answer:
		response = answer.json()
		driver_profile = response.get('driver_profiles')[0].get('driver_profile')
		driver_license = driver_profile.get('driver_license').get('number')
		driver = Driver.objects.filter(driver_license=driver_license).first()
		if driver:
			driver.driver_profile_id = driver_profile_id
			driver.save()
			return driver
		return [
			driver_license,
			driver_profile.get('last_name'),
			driver_profile.get('first_name'),
			driver_profile.get('middle_name')
		]	

# Поиск рабочего дня водителя по водителю и дате
def get_drivers_working_day(db_driver, current_date):
	working_day = Working_day.objects.filter(driver=db_driver, date=current_date).first()
	if not working_day:
		working_day = Working_day.objects.filter(driver=db_driver).last()
	if working_day:
		return working_day
	else:
		return None

# Сохранение транзакций, загруженных из API Яндекс
def upload_park_transactions(current_date, fromTime, toTime):
	upload_transactions_data = {}
	missing_drivers = []
	summ_of_transactions = 0
	qty_of_transactions = 0
	park_transactions = get_park_transactions(fromTime, toTime)
	if park_transactions:
		for transaction in park_transactions:
			amount = Decimal(abs(float(transaction.get('amount'))))
			driver_profile_id = transaction.get('driver_profile_id')
			driver = Driver.objects.filter(driver_profile_id=driver_profile_id).first()
			# если водитель не найден по Яндекс.ID, то ищем его по номеру водительского удостоверения
			if not driver:
				driver = get_driver_by_licence(driver_profile_id)
			if type(driver) is Driver:
			# поиск рабочего дня водителя, если рабочих дней не найдено, добавляем данные о тразакции в список не Учтенных
				working_day = get_drivers_working_day(driver, current_date)
				if working_day:
					working_day.cashless = working_day.cashless + amount
					working_day.save()
				else:
					missing_drivers.append([
						driver.driver_license,
                        driver.second_name,
                        driver.first_name,
                        driver.third_name,
                        amount,
                        True
                    ])
			else:
				driver.append(amount)
				driver.append(False)
				missing_drivers.append(driver)
			summ_of_transactions += amount
			qty_of_transactions += 1
	upload_transactions_data.update({
		"missing_drivers": missing_drivers,
		"summ_of_transactions": summ_of_transactions,
		"qty_of_transactions": qty_of_transactions
	})
	return upload_transactions_data

def transactions_yandex():
	current_date = datetime.datetime.now() - datetime.timedelta(days=1)
	# fromTime = "2023-11-30T00:00:01+03:00"
	fromTime = current_date.replace(hour=0, minute=0, second=1).isoformat() + '+03:00'
	# toTime = "2023-11-30T23:59:59+03:00"
	toTime = current_date.replace(hour=23, minute=59, second=59).isoformat() + '+03:00'
	upload_transactions_data = upload_park_transactions(current_date, fromTime, toTime)
	qty_of_transactions = upload_transactions_data.get("qty_of_transactions")
	summ_of_transactions = upload_transactions_data.get("summ_of_transactions")
	missing_drivers = upload_transactions_data.get("missing_drivers")
	if qty_of_transactions:
		service_send_mail(missing_drivers, current_date, summ_of_transactions, qty_of_transactions) 
		
def service_send_mail(missing_drivers, current_date, summ_of_transactions, qty_of_transactions):
	current_date = current_date.strftime("%d-%m-%Y")
	HOST = "mail.hosting.reg.ru"
	sender_email = config('MAIL_USER')
	# receiver_email = ['info@annasoft.ru', 'cherbadgi_sn@mail.ru', 'kzamesova@mail.ru', ]
	receiver_email = ['m.pekshev@annasoft.ru', ]
	password = config('MAIL_PASSWORD')
	message = MIMEMultipart("alternative")
	message["Subject"] = "Отчет по загрузке из Яндекс от {}".format(current_date)
	message["From"] = sender_email
	message["To"] = ','.join(receiver_email)
	missing_drivers_text = ""
	text = """\
        """
	if missing_drivers:
		missing_drivers_data = ""
		for item in missing_drivers:
			missing_drivers_data += "<p>{} {} {} {}, сумма : {}, нет рабочих дней: {}</p>".format(
				item[0], item[1], item[2], item[3], item[4], "Да" if item[5] else "Нет")
		missing_drivers_text = 	"""\
			<H3>Список водителей, которые не найдены в базе данных: </H3>
               {0}
            <p>Данные по транзакциям этих водителей за {1} необходимо загрузить вручную!</p>
        """.format(missing_drivers_data, current_date)
		text = """\
		{}""".format(missing_drivers_text)
	html = """\
		<html>
			<body>
			<H3>{0} загружено {2} транзакций на сумму {1}р. </H3>
			{3}
			</body>
		</html>
	""".format(current_date, summ_of_transactions.quantize(Decimal("1.00")), qty_of_transactions, missing_drivers_text)
	part1 = MIMEText(text, "plain")
	part2 = MIMEText(html, "html")
	message.attach(part1)
	message.attach(part2)
	context = ssl.create_default_context()
	try:
		server = smtplib.SMTP(HOST, 587)
		server.starttls()
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email , message.as_string())
		server.quit()
		try:
			with open(log_file_path, 'a+') as file:
				file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' загружено транзакций ' + str(qty_of_transactions)  + ' на сумму ' + str(summ_of_transactions.quantize(Decimal("1.00"))) + ', письмо отправлено!'   + '\n')
		except:
			pass		
		return True	
	except Exception as e:
		try:
			with open(log_file_path, 'a+') as file:
				file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' загружено транзакций ' + str(qty_of_transactions)  + ' на сумму ' + str(summ_of_transactions.quantize(Decimal("1.00"))) + ' письмо отправить не удалось. Код ошибки: ' + str(e) + '\n')
		except:
			pass
		return False