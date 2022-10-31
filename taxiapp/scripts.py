from decouple import config

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import datetime

from .models import Driver, Working_day

 

def driver_mailing():


		HOST = "mail.hosting.reg.ru"
		sender_email = config('MAIL_USER')
		password = config('MAIL_PASSWORD')

		for driver in Driver.objects.filter(active=True):

			if driver.email:	

				receiver_email = [ driver.email ]

				message = MIMEMultipart("alternative")
				message["Subject"] = "Таксопарк ИП Дивиченко О.И. - {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
				message["From"] = sender_email
				message["To"] = ','.join(receiver_email)

				text = """\
				"""

				html = """\
			    <html>
					<body>
						<div style="max-width: 610px; width:100%">
							<H4 style="margin-left: 20px;" >Уважаемый (ая) {2} {3}!</H4>
							<H4 style="margin-left: 20px;">Ваш долг на {0} составляет {1}р.</H4>
							<p style="margin-left: 20px;">* В расчете НЕ УЧТЕНО топливо сегодняшнего дня</p>
						</div>
					</body>
				</html>
			    """.format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), driver.debt, driver.second_name,  driver.first_name)

				part1 = MIMEText(text, "plain")
				part2 = MIMEText(html, "html")
			     
				message.attach(part1)
				message.attach(part2)
			    
				context = ssl.create_default_context()
				server = smtplib.SMTP(HOST, 587)
				server.starttls()
				server.login(sender_email, password)
				server.sendmail(
					sender_email, receiver_email , message.as_string()
				)
				server.quit()

def create_27():
					
	drivers = Driver.objects.filter(active=True)

	date = datetime.datetime.strptime('29/03/2022 01/0/00', "%d/%m/%Y %H/%M/%S")

	today = datetime.datetime.weekday(date)
	
	i = 0

	for driver in drivers:

		try:

			wd = Working_day.objects.get(driver=driver, date=date)

			print('день создан ------------------------', driver, wd.date)


		except:

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

			new_working_day = Working_day(driver=driver,date=date,rate=dr_rate,fuel=0,penalties=0,cash=0,cash_card=0,cashless=0,)
			new_working_day.save()


			i += 1

	print(i)
		# print(today)

		