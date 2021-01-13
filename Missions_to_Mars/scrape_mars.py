from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from splinter import Browser
import pandas as pd
from selenium import webdriver
import requests
import pymongo

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

db = client.mars_db


def init_browser():

    executable_path = {'executable_path': ChromeDriverManager().install()}
    return Browser('chrome', **executable_path, headless=False)


def scrape_info():
    browser = init_browser()
    mars_data = {}

    # Step 1: scrape mars website for latest news title and description
    url = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    browser.visit(url)
    html = browser.html
    soup = BeautifulSoup(html, 'lxml')

    news_title = soup.find_all('div', class_='content_title')[1].text
    mars_data['news_title'] = news_title

    news_p = soup.find_all('div', class_='article_teaser_body')[0].text
    mars_data['news_p'] = news_p

    # Step 2: scrape mars website for featured image

    url_img = 'https://www.jpl.nasa.gov/images/?search=&category=Mars'
    browser.visit(url_img)
    link_bs = BeautifulSoup(browser.html, 'lxml')

    buttons = browser.find_by_tag('button')
    buttons[4].click()
    bs2 = BeautifulSoup(browser.html, 'lxml')

    img = bs2.find_all(
        class_='text-subtitle-sm mb-2')[0].text.replace('\n', '').strip()
    browser.links.find_by_partial_text(img).click()

    bs3 = BeautifulSoup(browser.html, 'lxml')
    browser.links.find_by_partial_text('Download JPG').click()

    bs4 = BeautifulSoup(browser.html, 'lxml')
    featured_img_url = bs4.find_all('img')[0]['src']
    mars_data['featured_img_url'] = featured_img_url

    # Step 3: scrape mars for 4 hemispheres
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    hemispheres_soup = BeautifulSoup(browser.html, 'lxml')

    hemisphere_urls = []
    hemisphere_list = hemispheres_soup.find_all('div', class_='item')

    for hemisphere in hemisphere_list:

        img_name = hemisphere.h3.text
        browser.links.find_by_partial_text(img_name).click()
        new_browser = BeautifulSoup(browser.html, 'lxml')
        title = new_browser.find_all('h2', class_='title')[0].text
        url_link = new_browser.find_all('li')[0].a['href']
        hemisphere_urls.append({
            "title": title,
            "img_url": url_link
        })
    browser.back()

    mars_data['hemisphere_url'] = hemisphere_urls

    db.mars_info.insert_one(mars_data)

    browser.quit()

    return mars_data
