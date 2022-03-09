#Author: Nasri Binsaleh

CODING-----------------------------------------------------------------------------------------------------------------------------------------------------------

Get/Fetch the file
	With the guide from the project description, 
	in fetchincidents function, the pdf file is read using urllib module. 

Extract texts from pdf
	by using PyPDF2, the text were collected from each page of the pdf, and was concatenated into
	a long string holder called 'page'. It was observed that in this string, each elements in the pdf table
	are separated by a new line (\n). This can be used to organize the data. 

Put elements in a list
	As I was trying to see how I can put all these data into the sqlite dat table, I realized that later on 
	when trying to insert into a table, you need to pass a list of exact number of elements while using .executemany()
	function. So, I tried constructing a list of list, where each list in the list represents a row in the pdf table, 
	and inside the sublist are the elements in that particular row. 

How to Insert
	I realized that we can use execute many
	but we have to pass in 5 elements at a time

How to put in a list of list
	first, I split the string in 'page' by new line (\n) and store it in a list.
	then, I run a loop with 5 iterations each time, to put 5 elements in each row.
	Instinctively, if we start from the first date-time, and put 4 elements after that in together 
	in the same row, we should get each row from the pdf table. Then,
	now we can put it in a list of lists with 5 elements to pass into the sql table

	However, I found out that there are missing values to deal with, or double-lines values that mess up
	this process of adding 5 elements in each row. The data are incorrect. So I had to find another way to
	put the string in a list of list.

Trying to fix the above issue with regular expression
	using re module
		https://www.guru99.com/python-regular-expressions-complete-tutorial.html#3
	using regex for the date-time, by spliting the string at each date-time of the incidents, 
	I succeeded to put each row of the table into a list of list. But now some list (row) will have
	less than 5 elements due to some missing values, or more than 5 elements due to double-line values. 

There is a report posted date at the very bottom
	so that one is removed

Found out that one of the rows included the report header -- 'NORMAN POLICE DEPARTMENT' and 'Daily Incident Summary (Public)'
	so got that removed

Since some row have address longer than a line, so we have to combine the line.
	in the lines list, the address are stored in index 1 and 2, so I combined them and tried to remove element at index 2. But I couldn't remove it.
		https://stackoverflow.com/questions/5401601/problem-deleting-list-items-in-a-for-loop-python
		I tried to copy the list and still doesn't work, as the link says you cannot remove an item from the list you are iterating on. 
		instead of removing the element, I thought of another way, and just recreate the list at that row instead by appending just index 0, 1, 3, and 4.  

Now, to deal with missing values in some rows, which gave an error when trying to insert in the table because the # of fields do not match
	deal with missing values
		since the missing values are not present in the list, the list with less than 5 elements have missing values. 
		the missing values ('NaN') are then added to the index between the incident number and ORI

Now that each row in the list has strctly 5 elements, I can proceed to stored them in sqlite database

Connect with sqlite in python
	using 'sqlite3' module in python, I can connect with sqlite database and use sql command through python easily. 

Create table in sqlite database
	con = sqlite3.connect('normanpd.db') would connnect to normanpd.db, but if file does not exist, it will also create one.
	then using .execute('''CREATE TABLE IF NOT EXISTS incidents
                   		(incident_time TEXT,
                    		incident_number TEXT,
                    		incident_location TEXT,
                    		nature TEXT,
                    		incident_ori TEXT)''')
	the table is created with the above 5 columns. 

How to see what's in the table
	since we should look at what's in the table, several sql commands are useful to see if our program works. 
	'''
	data=cur.execute('''SELECT * FROM incidents''')
	for column in data.description:
    		print(column[0])
	'''
	the above code chunk can check for the column names in the table. 
	'''
	data=cur.execute('''SELECT * FROM incidents''')
	for row in data:
    		print(row)
    	'''
	and this one above checks for the values in the table. 

As I ran the program several times, but I kept writing data into the same database, the number of incidents from previous run is still there
	so the data in the database table are cleared every time at the end of the program. 


TESTING------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
At first, the simple download test was done to check if the website was connected and the pdf was downloaded. Also to learn how pytest works.
Now, I moved on to try and test the functions
	The first function is 'fetchincidents', this function download the data from the online pdf into a variable 'data'
		So I would try to test if the pdf data is successfully obtain and stored.
		At first, I thought that the data stored in 'data' from .read() would be in str type. so I tested to see if the stored data 
		are stored, and stored as a string type. but it failed the test, then I realized that it actually stored in bytes format. 
		So, I changed the condition to compare type(data) to bytes. 
	The next function is 'extractincidents' function 
		-In this function, the data are converted into a list of strings, organized into rows, and fixed up. I was testing whether 
		the data in 'data' are converted into a string and stored in variable 'page'. 
		-After the data were converted into a string, the string was then put into a list of strings. Then the list of strings are 
		broken into a list of lists containing strings called 'lines'. Here, I tested if the conversion to the list of string was 
		successful by comparing if type(lines) is a list. 
		-The regular expression for the dates were used to split the data into each row of that list of list and stored in 'incidents_list'. 
		So, I tested if the first string of each row is the 'incident date-time'. 
		-After fixing up the double-rows, and missing values, all the rows in 'incidents_list' mumst have 5 elements. Therefore, I tested if 
		each row has 5 elements. 
		-The report date was also extracted into the list, so it had to be removed. So, the test to check if the right date was removed was done. 
	After extracting data, then it has to be put in the database. The next function is 'createdb' function.
		-In this function, the table is created with the headers, so the test was done to check if the table was created with the right 
		column names. 
	Then the data was put in the table using 'populatedb' function.
		-The test for checking if all the data was put in the table was done by comparing the number of incidents in the table with the actual 
		on from the pdf.
	The last function is the 'status' function to report the natures and their frequency. 
		-In this function, the test was done to check if the nature and its corresponding frequency is correct. 
		


   

