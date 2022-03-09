def fetchincidents(url):
    import urllib
    import urllib.request

    headers = {}
    headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"                          

    data = urllib.request.urlopen(urllib.request.Request(url, headers=headers)).read()  
    
    return data



def extractincidents(data):

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

    # re module for regular expression
    import re

    # split data at each date-time and put it in a list called 'lines'
    dateregex = r"(\d{1,2}/\d{1,2}/\d{4}\s\d{1,2}:\d{1,2})"
    lines = re.split(dateregex,page)

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
    incidents_list.pop()

    # missing values imputation/addition

    # to be used as comparisons to determine how many missing values are needed
    ORI = {'EMSSTAT', 'OK0140200', '14005'}

    for line in range(len(incidents_list)):
        k = 0
        while(len(incidents_list[line]) < 5):
            if(incidents_list[line][k] in ORI):             # if ORI is at position k
                for l in range(1, 5-k):                     # the missing values is added 5-k-1 times
                    incidents_list[line].insert(k, 'NaN')
            else: k += 1

    return incidents_list



def createdb():

    # connect to sqlite database
    import sqlite3
    con = sqlite3.connect('normanpd.db')

    # cursor
    cur = con.cursor()

    # Create table
    cur.execute('''CREATE TABLE IF NOT EXISTS incidents
                   (incident_time TEXT,
                    incident_number TEXT,
                    incident_location TEXT,
                    nature TEXT,
                    incident_ori TEXT)''')

    return 'normanpd.db'





def populatedb(db, incidents):
    
    # insert data
    sqlite_insert_query = """INSERT INTO incidents
                              (incident_time, incident_number, incident_location, nature, incident_ori) 
                              VALUES (?, ?, ?, ?, ?);"""

    import sqlite3
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("DELETE FROM incidents")
    cur.executemany(sqlite_insert_query, incidents)
    con.commit()

    

def status(db):
    
    # Status
    import sqlite3
    con = sqlite3.connect(db)
    cur = con.cursor()
    
    status = cur.execute('''SELECT nature, count(*) as num_incidents
                            FROM incidents
                            GROUP BY nature
                            ORDER BY num_incidents desc, nature''')

    for row in status:
        print('{}|{}'.format(row[0], row[1]))


