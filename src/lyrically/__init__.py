from random import choice
import os
import time
import logging

import requests
from bs4 import BeautifulSoup

LOGS_DIR_PATH = f"../storage/logs"

if not os.path.exists(LOGS_DIR_PATH): os.mkdir(LOGS_DIR_PATH)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler(f"{LOGS_DIR_PATH}/lyrically.log", "w")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)

class Lyrically:
	def __init__(self, use_proxies):
		self.BASE_URL = "https://www.azlyrics.com"
		self.USE_PROXIES = use_proxies
		self.proxies = []

		logger.info("An instance of XIFY has been created.")

	def setup(self):
		# load proxies into obj variables
		if self.USE_PROXIES:
			with open("../storage/proxies/proxies.txt") as f:
				for line in f.readlines():
					line = line.strip()
					if line: 
						self.proxies.append(line)
		
		logger.info("Setup has been completed.")
	
	def get_proxy(self):
		proxy_ip = choice(self.proxies)

		if proxy_ip.count(":") > 1: # checking to see if proxy potentially has auth details
			proxy_ip_parts = proxy_ip.split(":")
				
			proxy_ip, proxy_port = proxy_ip_parts[0], proxy_ip_parts[1]
			username, password = proxy_ip_parts[2], proxy_ip_parts[3]

			proxy_auth = f"{username}:{password}@{proxy_ip}:{proxy_port}"
			proxy = {
				"http":f"http://{proxy_auth}",
				"https":f"http://{proxy_auth}",
			}
			
			logger.info("Proxies (with username & password) have been retrieved.")

			return proxy
		else:
			proxy = {
				"http":f"http://{proxy_ip}",
				"https":f"http://{proxy_ip}",
			}

			logger.info("Proxies have been retrieved.")
			
			return proxy
	
	def get_page_content(self, url):
		proxy = None

		if self.USE_PROXIES:
			proxy = self.get_proxy()

		headers = {
			"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
			"accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"accept-language": "en-US,en;q=0.9",
			"accept-encoding": "gzip, deflate, br"
		}
		
		if not proxy:
			r = requests.get(url, headers = headers)
			page_content = r.text
		else:
			valid_request = False

			while not valid_request:
				try:
					r = requests.get(url, headers = headers, proxies = proxy, timeout = 3.5)
					page_content = r.text

					valid_request = True
				except Exception as e:
					proxy = self.get_proxy()

		logger.info(f"Page content for '{url}' has been scraped.")

		return page_content

	def get_artist_songs(self, artist_name):
		# construct url for artist page
		artist_name = artist_name.lower()
		artist_url = self.BASE_URL + f"/{artist_name[0]}/{artist_name.replace(' ', '')}.html"

		# get page html
		artist_page_content = self.get_page_content(artist_url)

		# get obj containing album song links with respect to the album
		album_song_links = self.get_artist_song_links(artist_page_content)

		# make sure artist has appropiate storage location
		artist_storage_path = f"../storage/artists/{artist_name.lower()}"

		if not (os.path.exists(artist_storage_path)):
			os.mkdir(artist_storage_path)

		for album in album_song_links:
			# make sure album has appropiate storage location
			album_storage_path = f"{artist_storage_path}/{album.lower()}"

			if not (os.path.exists(album_storage_path)):
				os.mkdir(album_storage_path)
			
			# store lyrics in storage
			for song_link in album_song_links[album]:
				# check to see if song already exists in storage first
				song_name_with_no_spaces = song_link.split("/")
				song_name_with_no_spaces = song_name_with_no_spaces[len(song_name_with_no_spaces) - 1].split(".html")[0]

				song_storage_path = f"{album_storage_path}/{song_name_with_no_spaces}.txt"

				if os.path.isfile(song_storage_path):
					continue

				else:
					time.sleep(3)
					# get song content
					song_page_content = self.get_page_content(song_link)

					# get song title
					song_title = self.get_song_title(song_page_content)
					
					# get song lyrics
					song_lyrics = self.get_song_lyrics(song_page_content)

					# store song lyrics in storage
					with open(song_storage_path, "a+", encoding="utf-8") as f:
						f.write(f"{song_title.encode('latin-1').decode('utf-8')}\n\n")
						for lyric in song_lyrics:
							f.write(f"\n{lyric.encode('latin-1').decode('utf-8')}")

						logger.info(f"Successfully stored lyrics into '{song_storage_path}'.")
		
	def get_artist_song_links(self, page_content):
		soup = BeautifulSoup(page_content, 'html.parser')

		# get songs links (in relation to each album from the artist)
		album_song_main_div = soup.find("div", id = "listAlbum")

		album_song_divs = album_song_main_div.find_all("div")

		current_album_title = ""
		current_album_links = []
		album_song_links = {}

		for div in album_song_divs:
			if "class" in div.attrs:
				
				if "album" in div.attrs["class"]:
					raw_album_title = div.find("b").get_text()
					title = raw_album_title.replace('"', '')

					if current_album_title == "":
						current_album_title = title
					
					else:
						album_song_links[current_album_title] = current_album_links
						current_album_title = title
						current_album_links = []
				
				elif "listalbum-item" in div.attrs["class"]:
					song_endpoint = div.find("a").attrs["href"]

					if "azlyrics.com" in song_endpoint:
						song_url = song_endpoint
					else:
						song_url = self.BASE_URL + song_endpoint 
					
					current_album_links.append(song_url)
		
		album_song_links[current_album_title] = current_album_links

		logger.info("Successfully scraped artist song lyrics from artist page content.")

		return album_song_links
	
	def get_song_title(self, page_content):
		logger.info("Attempting to get song title from song lyric page content.")

		soup = BeautifulSoup(page_content, 'html.parser')

		# get title from html
		raw_title = soup.find("h1").get_text()

		# parse actual title from tag
		title = raw_title[1:len(raw_title) - 8]

		logger.info("Successfully retrieved song title!")

		return title
	
	def get_song_lyrics(self, page_content):
		logger.info("Attempting to get song lyrics from song lyric page content.")

		soup = BeautifulSoup(page_content, 'html.parser')

		# get raw lyrics from html
		lyric_div = soup.find("div", attrs = {"class": None, "id": None})

		raw_lyrics = lyric_div.get_text()

		# parse lyrics into list
		lyrics = []

		for line in raw_lyrics.split("\n"):
			if line:
				lyrics.append(line)
		
		logger.info("Successfully retrieved song lyrics!")
		
		return lyrics
