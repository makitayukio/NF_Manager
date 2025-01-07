import json
import lxml.etree as ET
from os import listdir
from requests import Session
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from time import sleep
from datetime import date


class NF_Validator:
	def __init__(self):
		self.nf_list = list(filter(lambda x: ".xml" in x, listdir(".")))
		self._cur_nf = {}
		self._session = Session()

		_options = Options()
		_options.add_argument("--app=https://credenciado.personalcard.com.br/auth/login")
		_options.add_argument("--window-size=600,800")
		_options.add_argument("--log-level=3")
		_options.add_experimental_option("useAutomationExtension", False)
		_options.add_experimental_option("excludeSwitches",["enable-automation"])

		prefs = {"credentials_enable_service": False, "profile.password_manager_enabled": False}
		_options.add_experimental_option("prefs", prefs)
		
		self._driver = Chrome(options=_options)
		self._driver.implicitly_wait(60)


	def quit(self):
		try:
			self._driver.quit()
		except WebDriverException:
			pass

	
	def login(self):
		print("Opening Personal Card")

		while("auth/login" in self._driver.current_url):
			pass

		print("Log in done!")

		# sleep(1)

		# driver_cookies = self._driver.get_cookies()
		# for c in driver_cookies:
		# 	self._session.cookies.set(c["name"], c["value"])

		# print(driver_cookies)

		res = self._driver.execute_script("return fetch('https://portal-api.personalcard.com.br/transactions?currentPage=1&perPage=10&recolhida=false&cpf=23606300832&startDate=2023-11-28T03:00:00.000Z&endDate=2025-01-05T14:48:55.196Z', {method: 'GET',headers: {'Accept': 'application/json','Content-Type': 'application/json'},}).then(res => res.json())")

		print(res)

		# self.quit()


	def parse_xml(self, xml):
		tree = ET.parse(xml)
		info = tree.find(".//infCFe")

		self._cur_nf["id"] = info.get("Id")
		self._cur_nf["date"] = info.find(".//dEmi").text
		self._cur_nf["time"] = info.find(".//hEmi").text
		self._cur_nf["value"] = info.find(".//vCFe").text
		self._cur_nf["cpf"] = info.find(".//CPF").text + "}"
		self._cur_nf["signature"] = info.find(".//assinaturaQRCODE").text.strip().replace('/', ';')

	
	def find_nf(self):
		url = f"https://portal-api.personalcard.com.br/transactions?currentPage=1&perPage=10&recolhida=false&cpf={self._cur_nf.get("cpf")}&startDate=2023-11-28T00:00:00.000Z&endDate={date.today().strftime("%Y-%m-%d")}T23:59:59.999Z"

		res = self._session.get(url).json()

		print(res)


	def run(self):
		print(self.nf_list)
		for nf in self.nf_list:

			with open(f"./{nf}", "r") as xml:
				self.parse_xml(xml)

			print(self._cur_nf)
			
			self.find_nf()


if __name__ == "__main__":

	p = NF_Validator()

	try:
		p.login()

		while True: pass
		# p.run()
	except Exception:
		p.quit()
	finally:
		p.quit()
