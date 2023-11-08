# -*- coding: utf-8 -*-
# python desire_pearl.py 10/20/2023 3 2
import re
import sys
import requests
import lxml.html
import json
from bs4 import BeautifulSoup
import time


def scrape(date, nights, adults=None):
    d_array = date.split('/')
    DATERANGESTART_DAY = d_array[1]
    DATERANGESTART_MONTH = d_array[0]
    DATERANGESTART_YEAR = d_array[2]
    checkin = DATERANGESTART_YEAR+"/"+DATERANGESTART_MONTH+"/"+DATERANGESTART_DAY
    facility = 'All Room Types'
    resrooms = 1
    availability = 'Book Now'
    send = 'Check Availability!'

    def scrape_promo_message(payload):

        if not payload:
            return ""

        url = "https://booking.desire-experience.com/desire-riviera-maya-pearl-resort/booking2.asp"

        # time.sleep(500)
        r = requests.post(url, data=payload)
        soup = BeautifulSoup(r.text, "html.parser")
        # print(soup)

        hxs = lxml.html.document_fromstring(r.text)

        table = hxs.xpath('//table[@class="listDates padtable"]')

        if not table:
            return ""

        promo_description = table[0].xpath(
            "//input[@name='subtotal']/following-sibling::tr[1]/descendant::*/text()")

        return "".join(promo_description).strip()

    #  ? starts from here
    data = {
        'Hotel': 'Desire Pearl',
        'DATERANGESTART_MONTH': DATERANGESTART_MONTH,
        'DATERANGESTART_DAY': DATERANGESTART_DAY,
        'DATERANGESTART_YEAR': DATERANGESTART_YEAR,
        'nights': nights,
        'Adults': adults,
        'facility': facility,
        'Res_Rooms': resrooms,
        'availability': availability,
        'checkin': checkin
    }

    # r = requests.post(
    # "https://booking.desire-experience.com/desire-riviera-maya-pearl-resort/booking1.asp", data=data)
    # "https://booking.originalresorts.com/desirepearl/booking1.asp", data=data)
    r = requests.post(
        "https://reservations.originalaffiliates.com/booking1.asp", data=data)

    soup = BeautifulSoup(r.text, "html.parser")
    rooms = soup.find_all("table", attrs={"class": "room-table"})
    rooms_data = []

    for index, room in enumerate(rooms, start=0):
        room_dict = {}
        room_name_tag = room.find("h3", class_="text-left")
        room_name_text = ""

        # ? room name
        for content in room_name_tag.contents:
            if content.name is None:
                room_name_text = room_name_text+str(content)
        room_dict['name'] = room_name_text

        # ? availablity of rooms
        availability_of_room = []
        days_of_week = room.find_all('td', attrs={"class": "final-price"})
        room_dict['availability'] = [
            s.text for s in days_of_week if 'N/A' not in s.text]

        # ? total price
        total_price = soup.find_all(
            'span', attrs={"style": "font-weight: bold;"})[index].text
        room_dict['total_price'] = total_price

        # ? rate description
        rate_description_text = soup.find_all(
            "td", attrs={"class": "rate-description"})[index].text
        room_dict['rate-description'] = rate_description_text

        # ? promo message
        promo_message = soup.find_all('b')[index].text
        room_dict['promo_message'] = promo_message.replace(
            "[Click for Promo Details]", "").strip()

        # ? check if available for booking
        try:
            available_for_booking = soup.find_all(
                "input", attrs={"value": "Book Now"})[index]
            room_dict['available_for_booking'] = 1
        except:
            room_dict['available_for_booking'] = 0

        # ? scraping additional promo message
        form_fields = soup.find_all("input")
        payload = {}

        for field in soup.find_all('input'):  # Example: finding all input tags
            name = field.get("name")
            value = field.get("value")
            if name is not None and value is not None:
                payload[name] = value

        promo_message = scrape_promo_message(payload)
        room_dict["additional_promo_message"] = promo_message

        # adding data to list
        rooms_data.append(room_dict)
        # print(room_dict)

    # print(json.dumps(rooms_data))
    return rooms_data


# scrape("10/20/2023", 3, 2)
