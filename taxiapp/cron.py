from .models        import Driver, Working_day
import datetime 
import time
import requests
import json
from decimal import Decimal

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from decouple import config

import os


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

def transactions_yandex():

    driver_url = 'https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/list'
    dr_headers = {'Accept-Language': 'ru',
               'X-Client-ID': config('YA_X_CLIENT_ID'),
               'X-API-Key': config('YA_X_API_KEY')}

    driver_data = {
                "fields": {

                    "account": [],
                    "car": [],
                    "park": []
                },
                "query": {
                      "park": {
                        "id": config('YA_ID')
                      },
                },

    }

    for i in range(10):
        time.sleep(2)
        answer = requests.post(driver_url, headers=dr_headers, data=json.dumps(driver_data),)
        log_file = open(os.path.abspath(config('LOG_FILE_PATH')), 'a+')
        log_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + driver_url + ' ' + str(answer.status_code) + '\n')
        log_file.close()
        if answer.status_code == 200:
            break  

    response = answer.json()
    profiles = response.get('driver_profiles')

    missing_drivers = []

    day_bt = datetime.datetime.now() - datetime.timedelta(days=1)

    summ_of_transactions = 0
    num_of_transactions = 0

    for p in profiles:

        driver = (p.get('driver_profile'))
        dr_license = driver.get('driver_license')

        n = datetime.datetime.now()
        n = n.replace(hour=0, minute=1)
        y = n - datetime.timedelta(days=1)
        y = y.replace(hour=0,minute=1)

        now         =   n.isoformat() + '+00:00'
        yesterday   =   y.isoformat() + '+00:00'

        url = 'https://fleet-api.taxi.yandex.net/v2/parks/driver-profiles/transactions/list'
        headers = {'Accept-Language': 'ru',
                   'X-Client-ID': config('YA_X_CLIENT_ID'),
                   'X-API-Key': config('YA_X_API_KEY')}

        data = {
                    "query": {
                            "park": {
                                    "driver_profile": {
                                    "id": driver['id']
                                    },
                                  "id": config('YA_ID'),
                                  "transaction": {
                                        "category_ids": ['partner_service_manual',],
                                        "event_at": {
                                          "from": yesterday,
                                          "to": now
                                        }
                                  }
                            }
                    }

        } 

        for i in range(20):

            answer = requests.post(url, headers=headers, data=json.dumps(data),)
            log_file = open(os.path.abspath(config('LOG_FILE_PATH')), 'a+')
            log_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + url + ' ' + str(answer.status_code) + ' ' + driver['id']  + '\n')
            log_file.close()
            if answer.status_code == 200:
                time.sleep(3)
                break

            time.sleep(i*3)

        response = answer.json()
        transactions = response.get('transactions')

        if transactions:

            for key in transactions:
                day_before_today = datetime.datetime.now() - datetime.timedelta(days=1)
                taxidriver = Driver.objects.filter(driver_license=dr_license['number']).first()
                if taxidriver:
                    working_day = Working_day.objects.filter(driver=taxidriver, date=day_before_today).first()
                    if working_day:
                        working_day.cashless = working_day.cashless + Decimal(abs(float(key['amount'])))
                        working_day.save()
                    else:
                        working_day = Working_day.objects.filter(driver=taxidriver).last()
                        if working_day:
                            working_day.cashless = working_day.cashless + Decimal(abs(float(key['amount'])))
                            working_day.save()
                        else:
                            missing_drivers.append([dr_license['number'], driver.get('last_name'), driver.get('first_name'), driver.get('middle_name'), key['amount'], True,])
                            continue

                    summ_of_transactions    += Decimal(abs(float(key['amount'])))
                    num_of_transactions     += 1

                else:
                    missing_drivers.append([dr_license['number'], driver.get('last_name'), driver.get('first_name'), driver.get('middle_name'), key['amount'], False,])

    if num_of_transactions:
        
        send_mail(missing_drivers, day_bt, summ_of_transactions, num_of_transactions) 




def send_mail(missing_drivers, day_before_today, summ_of_transactions, num_of_transactions):


    HOST = "mail.hosting.reg.ru"
    sender_email = config('MAIL_USER')
    receiver_email = ['info@annasoft.ru', 'cherbadgi_sn@mail.ru', 'kzamesova@mail.ru', ]
    password = config('MAIL_PASSWORD')

     
    message = MIMEMultipart("alternative")
    message["Subject"] = "Отчет по загрузке из Яндекс от {}".format(day_before_today.strftime("%Y-%m-%d"))
    message["From"] = sender_email
    message["To"] = ','.join(receiver_email)
    
    test_text = ""
    if missing_drivers:
        for item in missing_drivers:
            no_working_days = 'Нет'
            if item[5]:
                no_working_days = 'Да'
            test_text += "<p>{} {} {} {}, сумма : {}, нет рабочих дней: {}</p>".format(item[0], item[1], item[2], item[3], item[4],no_working_days,)

        text = """\
        {}""".format(test_text)
         
        html = """\
        <html>
          <body>
            <H3>{1} загружено {3} транзакций на сумму {2}р. </H3>

            <H3>Список водителей, которые не найдены в базе данных: </H3>
               {0}
            <p>Данные по транзакциям этих водителей за {1} необходимо загрузить вручную!</p>
          </body>
        </html>
        """.format(test_text, day_before_today.strftime("%Y-%m-%d"), summ_of_transactions.quantize(Decimal("1.00")), num_of_transactions)

    else:

        text = """\
        """
        
        html = """\
        <html>
          <body>
            <H3>{0} загружено {2} транзакций на сумму {1}р. </H3>
          </body>
        </html>
        """.format(day_before_today.strftime("%Y-%m-%d"), summ_of_transactions.quantize(Decimal("1.00")), num_of_transactions)
     
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

        log_file = open(os.path.abspath(config('LOG_FILE_PATH')), 'a+')
        log_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' загружено транзакций ' + str(num_of_transactions)  + ' на сумму ' + str(summ_of_transactions.quantize(Decimal("1.00"))) + ', письмо отправлено!'   + '\n')
        log_file.close()

    except Exception as e: 
        log_file = open(os.path.abspath(config('LOG_FILE_PATH')), 'a+')
        log_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' загружено транзакций ' + str(num_of_transactions)  + ' на сумму ' + str(summ_of_transactions.quantize(Decimal("1.00"))) + ' письмо отправить не удалось. Код ошибки: ' + str(e) + '\n')
        log_file.close()