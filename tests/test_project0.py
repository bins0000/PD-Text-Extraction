import pytest
import urllib
import urllib.request
from pathlib import Path



# try to download and write a file
response = urllib.request.urlopen("https://www.normanok.gov/sites/default/files/documents/2022-03/2022-03-06_daily_incident_summary.pdf")
file = open('/home/nasri777_nb/cs5293sp22-project0/docs/incidents' + ".pdf", 'wb')
file.write(response.read())
file.close()


def test_download():
    file_download = Path('/home/nasri777_nb/cs5293sp22-project0/docs/incidents.pdf').exists()
    
    assert file_download == True


#fetchincidents 
url = "https://www.normanok.gov/sites/default/files/documents/2022-03/2022-03-06_daily_incident_summary.pdf"
headers = {}
headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()


#test if the data are successfully fetched in fetchincidents function.
def test_fetchincidents():

    assert type(data) == bytes

#extractincidents
import tempfile
fp = tempfile.TemporaryFile()
import PyPDF2
# Write the pdf data to a temp file
fp.write(data)
# Set the curser of the file back to the begining
fp.seek(0)
# Read the PDF into a long string called 'page'
pdfReader = PyPDF2.pdf.PdfFileReader(fp)
pagecount = pdfReader.getNumPages()
page = ''
for pagenum in range(0, pagecount):
    page = page + pdfReader.getPage(pagenum).extractText()


#test for extractincidents function. 
def test_extractincidents():
    
    assert type(page) == str

import re
# split data at each date-time and put it in a list called 'lines'
dateregex = r"(\d{1,2}/\d{1,2}/\d{4}\s\d{1,2}:\d{1,2})"
lines = re.split(dateregex,page)


# test if 'lines' is a list
def test_splitlines():
    
    assert type(lines) == list


# fix up the data
for line in range(len(lines)):
    # split the data in each line at new line
    lines[line] = re.split(r'\n', lines[line])
    # remove an empty string
    while("" in lines[line]) :
        lines[line].remove("")
    # remove the headers of the report
    while('NORMAN POLICE DEPARTMENT' in lines[line]) :
        lines[line].remove('NORMAN POLICE DEPARTMENT')
    while('Daily Incident Summary (Public)' in lines[line]) :
        lines[line].remove('Daily Incident Summary (Public)')
    # combine the 2-lines address
    if(len(lines[line]) > 4):
        lines[line][1] = lines[line][1] + ' ' + lines[line][2]
        lines[line] = [lines[line][0]] + [lines[line][1]] + [lines[line][3]] + [lines[line][4]]


# combine the date and its corresponding data into a new list called 'incidents_list'
incidents_list = []
j = 0
while j < len(lines):
    if re.match(dateregex, lines[j][0]):
            incidents_list.append(lines[j] + lines[j+1])
            j += 2
    else: j += 1
# remove the last element, this element is the date of the report which is not needed
report_date = incidents_list.pop()


# test if the report-date was removed properly. 
def test_reportdate():

    assert report_date == ['3/7/2022 10:25']


# missing values imputation/addition
# to be used as comparisons to determine how many missing values are needed
ORI = {'EMSSTAT', 'OK0140200', '14005'}
for line in range(len(incidents_list)):
    k = 0
    while(len(incidents_list[line]) < 5):
        if(incidents_list[line][k] in ORI):             # if ORI is at position k
            for l in range(1, 5-k):                     # the missing values are added 5-k-1 times
                incidents_list[line].insert(k, 'NaN')
        else: k += 1


# test for data clean-up. 
def test_datacleanups():
    # test for date-time being the first elements. 
    if re.match(dateregex, incidents_list[4][0]):
        clean = True
    else: clean = False
    
    assert clean == True

    # test for each row of the list having exactly 5 elements.
    assert len(incidents_list[4]) == 5


# createdb()
import sqlite3
con = sqlite3.connect('normanpd.db')
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS incidents
                   (incident_time TEXT,
                    incident_number TEXT,
                    incident_location TEXT,
                    nature TEXT,
                    incident_ori TEXT)''')

# insert data
sqlite_insert_query = """INSERT INTO incidents
                              (incident_time, incident_number, incident_location, nature, incident_ori)
                              VALUES (?, ?, ?, ?, ?);"""



# check if the table are created with correst headers
def test_column_names():
    # check the column names
    data=cur.execute('''SELECT * FROM incidents''')
    column_names = {'incident_time', 'incident_number', 'incident_location', 'nature', 'incident_ori'}
    for column in data.description:
        if(column[0] in column_names):
            names = True
        else: names = False

    assert names == True


#populatedb
# insert data
sqlite_insert_query = """INSERT INTO incidents
                              (incident_time, incident_number, incident_location, nature, incident_ori)
                              VALUES (?, ?, ?, ?, ?);"""

cur.execute("DELETE FROM incidents")
cur.executemany(sqlite_insert_query, incidents_list)
con.commit()


# check if the data are placed in the table correctly
def test_datacheck():
    # check if all the data are inserted into the table
    data=cur.execute('''SELECT * FROM incidents''')
    row_num = 0
    for row in data:
        row_num += 1
    
    assert row_num == 266



#status
status = cur.execute('''SELECT nature, count(*) as num_incidents
                        FROM incidents
                        GROUP BY nature
                        ORDER BY num_incidents desc, nature''')
    
rows = []
count = 0
for row in status:
    rows.insert(count, row)
    count += 1


# function to check if the status is correct
def test_status():
    #check if the status is correct
    assert rows[0] == ('Traffic Stop', 32)
    assert rows[45] == ('Barking Dog', 1)


