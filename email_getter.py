import imaplib
import email
import os
from bs4 import BeautifulSoup
from datetime import date
import pandas as pd
from hidden_variables import EXCLUDED_STRINGS

TODAY = date.today()

imap_server = "imap.gmail.com"
email_address = os.environ.get('MY_PERSONAL_EMAIL')
password = os.environ.get('GOOGLE_MAIL_PASSWORD')

imap = imaplib.IMAP4_SSL(imap_server)
imap.login(email_address, password)

imap.select('Schedule')

tables = []

_, msgnums = imap.search(None, 'ALL')

for msgnum in msgnums[0].split():
    _, table_data = imap.fetch(msgnum,
                               "(RFC822)")  # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
    message = email.message_from_bytes(table_data[0][1])  # getting the mail content

    for part in message.walk():
        if part.get_content_type() == "text/html":
            html = part.get_payload(decode=True)
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find_all('table')
            if table is None:
                pass
            else:
                tables.append(table)

tables.reverse()
schedule = []
day = []
for table in tables:
    soup2 = BeautifulSoup(str(table), 'html.parser')
    for tag in soup2.find_all("td"):
        if tag.string is not None:
            schedule.append(tag.string)
        else:
            pass

for item in schedule:
    [schedule.remove(item) for exclude in EXCLUDED_STRINGS if exclude.lower() == item.lower()]

for item in schedule:
    if item.lower() == 'total hours':
        next_index = schedule.index(item) + 1
        schedule.pop(next_index)
        schedule.remove(item)

# Making new list with list of individual shift times
revised_schedule = []
for x in range(0, 305, 5):
    revised_schedule.append(schedule[x:x + 5])

# print(revised_schedule)
data_df = pd.DataFrame(revised_schedule)
data_df = data_df.drop_duplicates()
print(data_df)

# for i in revised_schedule:
#     i.pop(3)

# final_schedule = []
# for list in revised_schedule:
#     if list not in final_schedule:
#         final_schedule.append(list)


imap.close()
