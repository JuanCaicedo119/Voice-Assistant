# from ipaddress import ip_address
# from pickle import APPEND
# from unittest.mock import sentinel
# import requests
# import wikipedia
import pywhatkit as kit
# from email.message import EmailMessage
# import smtplib
from decouple import config

NEWS_API_KEY = config("NEWS_API_KEY")

def play_on_youtube(video):
    kit.playonyt(video)

def search_on_google(query):
    kit.search(query)

# def create_event():




