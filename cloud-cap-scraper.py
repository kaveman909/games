#!/opt/homebrew/bin/python3.9

import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import re
import smtplib
from email.message import EmailMessage
import schedule
import time
import os
from datetime import datetime

REMOVE_RETRY = 3

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)


class Crawler:

  def __init__(self, urls=[], db_file='db.txt'):
    self.top_level_urls = urls
    self.retry = REMOVE_RETRY
    self.urls_this_run = []
    self.visited_urls = []
    self.urls_to_visit = []
    self.urls_in_db = []
    self.db_file = db_file
    if (os.path.exists(self.db_file)):
      # read the current db and load it into the array
      with open(self.db_file, 'r') as db:
        for line in db:
          self.urls_in_db.append(line.rstrip())
    else:
      # Create empty db file
      open(self.db_file, 'w').close()

  def download_url(self, url):
    return requests.get(url).text

  def get_linked_urls(self, url, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
      path = link.get('href')
      if path and path.startswith('/'):
        path = urljoin(url, path)
      yield path

  def add_url_to_visit(self, url, url2):
    if url != url2 and url2 is not None and url2 not in self.visited_urls and url2 not in self.urls_to_visit and re.search(r'/page\d+', url2):
      self.urls_to_visit.append(url2)

  def crawl(self, url):
    html = self.download_url(url)
    for url2 in self.get_linked_urls(url, html):
      self.add_url_to_visit(url, url2)
      if url2 is not None and re.search(r'.*html', url2) and not re.search(r'(card-games|imports-trick-takers)/page\d+', url2):
        if url2 not in self.urls_this_run:
          self.urls_this_run.append(url2)

  def send_email(self, urls_new, urls_removed):
    # set your email and password
    # please use App Password
    email_address = "xxx@gmail.com"
    email_password = "xxx"
    send_addr_text = "xxx@sms.clicksend.com"
    send_addr_email = "xxx@gmail.com"

    # always create email
    msg = EmailMessage()
    msg['Subject'] = f'{len(urls_new)} new, {len(urls_removed)} removed card games at Cloud Cap!'
    msg['From'] = email_address
    msg['To'] = send_addr_email
    msg.set_content('New Games:\n{}\nRemoved Games:\n{}'.format(
        '\n'.join(urls_new), '\n'.join(urls_removed)))

    # if we have new games, also send brief text so we have real-time alert
    msg_new = EmailMessage()
    if urls_new:
      msg_new['Subject'] = 'NEW'
      msg_new['From'] = email_address
      msg_new['To'] = send_addr_text
      msg_new.set_content('{} new games at CC'.format(len(urls_new)))

    # send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
      smtp.login(email_address, email_password)
      logging.info('Sending email to: {}'.format(send_addr_email))
      smtp.send_message(msg)
      if urls_new:
        logging.info('Sending text to: {}'.format(send_addr_text))
        smtp.send_message(msg_new)

  def run(self):
    self.urls_this_run = []
    self.visited_urls = []
    self.urls_to_visit = self.top_level_urls.copy()
    while self.urls_to_visit:
      url = self.urls_to_visit.pop(0)
      logging.info(f'Crawling: {url}')
      try:
        self.crawl(url)
      except Exception:
        logging.exception(f'Failed to crawl: {url}')
      finally:
        if url is not None and url not in self.visited_urls:
          self.visited_urls.append(url)

    urls_new = []
    urls_removed = []
    self.urls_this_run.sort()

    for url_this in self.urls_this_run:
      if url_this not in self.urls_in_db:
        # means that we have something new!
        urls_new.append(url_this)
    for url_db in self.urls_in_db:
      if url_db not in self.urls_this_run:
        # means that something is now out of stock
        urls_removed.append(url_db)

    if urls_removed and self.retry > 0:
      # workaround for issue where sometimes things are removed just for one run
      logging.info(
          "Games removed; retrying {} more times before confirming removal".format(self.retry))
      self.retry -= 1
      self.run()
      return
    self.retry = REMOVE_RETRY
    if urls_new or urls_removed:
      self.send_email(urls_new, urls_removed)
      self.urls_in_db = self.urls_this_run.copy()
      with open(self.db_file, 'w') as db:
        db.writelines('{}\n'.format(x) for x in self.urls_in_db)

    logging.info("Number of games seen this run: {}".format(
        len(self.urls_this_run)))


if __name__ == '__main__':
  crawler = Crawler(urls=['https://cloud-cap-games.shoplightspeed.com/imports-trick-takers',
                          'https://cloud-cap-games.shoplightspeed.com/card-games'])

  crawler.run()

  sched = 5
  schedule.every(sched).minutes.do(crawler.run)

  print("Starting scheduler to scrape for games! (runs every {} mins)".format(sched))
  while True:
    schedule.run_pending()
    time.sleep(1)
