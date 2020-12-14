from bs4 import BeautifulSoup
import requests
import math
import time
import csv
import re

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
headers = { "User-Agent": user_agent, "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "ru,en-us;q=0.7,en;q=0.3", "Accept-Charset": "windows-1251,utf-8;q=0.7,*;q=0.7", "Keep-Alive": "300", "Connection": "keep-alive", "Referer": "http://www.kinopoisk.ru/" }

# настройки кук для парсинга. куки можно взять залогинившись на kinopoisk
# и зайдя в chrome devtools > application > cookies > https://www.kinopoisk.ru
session_id = ""
phpsessid = ""
l = ""
sso_status = "sso.passport.yandex.ru:synchronized"

user_id = ""

cookies = { "Session_id": session_id, "PHPSESSID": phpsessid, "L": l, "sso_status": sso_status  }

class movieVote:
	def __init__(self, name_ru, name_eng, date, vote):
		self.name_ru = name_ru
		self.name_eng = name_eng
		self.date = date
		self.vote = vote

def parse_text(soup_instance):
	names = soup_instance.find_all("div", class_="nameRus")
	names_eng = soup_instance.find_all("div", class_="nameEng")
	dates = soup_instance.find_all("div", class_="date")
	votes = soup_instance.find_all("div", class_="vote")

	names_text = [x.text for x in names]
	names_eng_text = [x.text for x in names_eng]
	dates_text = [x.text for x in dates]
	votes_text = [x.text for x in votes]

	# в даты попадает div заголовка
	dates_text.pop(0)
	# в голоса попадают два элемента из "мои оценки"
	votes_text.pop(0)
	votes_text.pop(0)

	for i, vote in enumerate(votes_text):
		parsing_results.append(movieVote(names_text[i], names_eng_text[i], dates_text[i], votes_text[i]))

parsing_results = []

r = requests.get("https://www.kinopoisk.ru/user/" + user_id + "/votes/list/ord/date/vs/vote/perpage/200/page/1/", headers=headers, cookies=cookies)

soup = BeautifulSoup(r.text, "html.parser")
pages_count_div = soup.find("div", class_="pagesFromTo")
pages_count = math.ceil(int(re.split(r" из ", pages_count_div.text.strip())[1]) / 200)

parse_text(soup)

for x in range (2, pages_count + 1):
	r = requests.get("https://www.kinopoisk.ru/user/" + user_id + "/votes/list/ord/date/vs/vote/perpage/200/page/" + str(x), headers=headers, cookies=cookies)

	soup = BeautifulSoup(r.text, "html.parser")
	parse_text(soup)

	time.sleep(2)

with open("results.csv", mode="w", encoding="utf-8", newline="") as csv_file:
	fieldnames = ["name_ru", "name_eng", "date", "vote"]
	writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter="\t")

	writer.writeheader()
	for obj in parsing_results:
		writer.writerow({ "name_ru": obj.name_ru, "name_eng": obj.name_eng, "date": obj.date, "vote": obj.vote })