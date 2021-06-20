import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait

# CONFIG
TELEGRAM_API = "Telegram Token" # BOT TOKEN
TELEGRAM_ID = 0 # USER ID

def start_browser():
	chrome_options = Options()
	# If you using forked chrome, ex: brave browser
	# chrome_options.binary_location = 'C:/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe'
	chrome_options.add_argument("--start-maximized")
	chrome_options.add_extension('LINE_v2.4.5.crx')
	driver = webdriver.Chrome(options=chrome_options)
	driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'})
	return driver

def install_extension():
	driver.get("https://chrome.google.com/webstore/detail/line/ophjlpahpchlmihnnnihgmmeilfjmjjc")
	print(driver.current_url)

def login(driver):
	driver.get("chrome-extension://ophjlpahpchlmihnnnihgmmeilfjmjjc/index.html")

def alert(driver, text):
	try:
		driver.execute_script("alert('{}');".format(text))
	except WebDriverException:
		pass

def sendMsgTelegram(text):
	TG_API = f"https://api.telegram.org/bot{TELEGRAM_API}/sendMessage"
	data = {"chat_id": TELEGRAM_ID, "text": text, "parse_mode": "html"}
	req = requests.post(TG_API, json=data).json()
	return req['ok']

def readChat(driver, chat_id):
	try:
		read = driver.find_element_by_xpath(f"//div[@data-chatid='{chat_id}']")
	except NoSuchElementException:
		return 0
	read.click()
	return 1

def checkChat(driver):
	soup = BeautifulSoup(driver.page_source, "lxml")
	chats = soup.find('ul', {'id': '_chat_list_body'})
	results = []
	for chat in chats.findAll("li"):
		chat_title = chat['title']
		chat_id = chat.find('div', {'class': 'chatList'})['data-chatid']
		chat_pic = chat.find('img')['src']
		chat_text = chat.find('p').text
		chat_time = chat.time.text
		chat_unread = chat.find("div", {"class": "MdIcoBadge01"}).text
		results.append({"chat_title": chat_title,
						"chat_id": chat_id,
						"chat_pic": chat_pic,
						"chat_text": chat_text,
						"chat_time": chat_time,
						"chat_unread": chat_unread})
	return results

# Start the browser UI
try:
	driver = start_browser()
except WebDriverException as err:
	print(f"> {err}")
	print("> Please download latest chromedriver and place in current directory")
	print("> Download: https://sites.google.com/a/chromium.org/chromedriver/downloads")
	exit(1)
# Login, go to exstension web url
login(driver)
#alert(driver, "Please login first")

# Check if user was logged in, sleep 1s for prevent high CPU usage
while True:
	try:
		exist = driver.find_element_by_id('wrap_settings')
	except NoSuchElementException:
		time.sleep(1)
		continue
	break

# If user was logged in
print("> Login successfully")

# Monitor incoming new msg every 1s
while True:
	chats = checkChat(driver)
	curr_chat = chats[0]
	if curr_chat['chat_unread'] and int(curr_chat['chat_unread']) >= 1:
		print("> {}: {}".format(curr_chat['chat_title'], curr_chat['chat_text']))
		text_maker = f"<b>{curr_chat['chat_title']}</b>\n{curr_chat['chat_text']}"
		sent = sendMsgTelegram(text_maker)
		read = readChat(driver, curr_chat['chat_id'])
		readDmy = readChat(driver, chats[-1]['chat_id'])
	time.sleep(1)
