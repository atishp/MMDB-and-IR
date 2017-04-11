from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import os
from os import curdir, sep
import cgi
import thread
import threading
import time
import psycopg2
import sys
import re
import operator
from collections import Counter
PORT_NUMBER = 8080

#Handles incoming requests from browser
class myHandler(BaseHTTPRequestHandler):
	
	#GET requests
	def do_GET(self):
		# Set the default page
		if self.path=="/":
			self.path="/index.html"

		try:
			#Check the file extension and set the appropriate mime type
			sendReply = False
			if self.path.endswith(".html"):
				mimetype='text/html'
				sendReply = True
			if self.path.endswith(".py"):
				mimetype='application/cgi'
				sendReply = True
			if self.path.endswith(".jpg"):
				mimetype='image/jpg'
				sendReply = True
			if self.path.endswith(".js"):
				mimetype='application/javascript'
				sendReply = True
			if self.path.endswith(".css"):
				mimetype='text/css'
				sendReply = True
				
			#load the index page
			if sendReply == True:
				#Open the static file requested and send it
				f = open(curdir + sep + self.path) # curdir - return current directory, sep - returns separator
				self.send_response(200) # code 200 - OK header 
				self.send_header('Content-type',mimetype) #set the mime type
				self.end_headers()
				self.wfile.write(f.read())
				f.close()
			return

		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	#POST requests Handler
	def do_POST(self):

		if self.path=="/save_file":
			form = cgi.FieldStorage( # FieldStorage is used to get submitted data in the form of 'form[key]'
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			# Get filename here.
			fileitem = form['filename']
			#print fileitem
			# Upload the file
			if fileitem.filename:
			   #print fileitem.filename
			   fn = 'F:/research- MMDB/code/tmp/'+os.path.basename(fileitem.filename)
			   open(fn, 'w+').write(fileitem.file.read())
			   ''' with open(fn) as f:
				passage = f.read()
			   words = re.findall(r'\w+', passage)
			   cap_words = [word.upper() for word in words]
			   word_counts = Counter(cap_words)
			  #print word_counts
			   print max(word_counts.iteritems(), key=operator.itemgetter(1))[0]'''
			   message = 'The file "' + fn + '" was uploaded successfully'
			   
			else:
			   message = 'No file was uploaded'

			#Redirect the browser to the main page 
			self.send_response(302)
			self.send_header('Location','/')
			self.end_headers()
			return			
		
		if self.path=="/search_file":
			form = cgi.FieldStorage(
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
					 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			print form["search_box"].value
			self.send_response(302)
			self.send_header('Location','/')
			self.end_headers()
			return	
			
		if self.path=="/search_images":
			form = cgi.FieldStorage(
			fp=self.rfile, 
			headers=self.headers,
			environ={'REQUEST_METHOD':'POST',
			'CONTENT_TYPE':self.headers['Content-Type'],
			})
			#print form["image_path_box"].value
			os.system("python search.py --index index.csv --query queries/103100.png --result-set dataset")
			self.send_response(302)
			self.send_header('Location','/')
			self.end_headers()
			return
	
		if self.path=="/insert_doc":
			form = cgi.FieldStorage( 
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			fileitem = form['filename']
			
			if fileitem.filename:
				fn = 'F:/research- MMDB/code/documents/'+os.path.basename(fileitem.filename)
				open(fn, 'w+').write(fileitem.file.read())
				message = 'The file "' + fn + '" was uploaded successfully'	
				con = None
				try:		 
					con = psycopg2.connect(host='localhost', database='Library', user='Atish',password='shivratna') 
					cur = con.cursor()
					#cur.execute('''INSERT INTO Books (Id,Name,Location,NoOfCopies,Language,Edition) VALUES ('5', 'Lost World', 'shelf 1', 15, 'English','Second Revised' );''')
					cur.execute("""INSERT INTO books VALUES (%s,%s, %s,%s, %s, %s, %s);""",( form['id'].value, form['name'].value, form['location'].value,form['copies'].value, form['language'].value,fn,form['edition'].value))
				except psycopg2.DatabaseError, e:
					print 'Error %s' % e    
					sys.exit(1)	
					
				finally:		
					if con:
						con.commit()
						con.close()
			
			else:
			   message = 'No file was uploaded'
			#Redirect the browser to the main page 
			self.send_response(302)
			self.send_header('Location','/')
			self.end_headers()
			return

		if self.path=="/search_doc":
			form = cgi.FieldStorage( 
				fp=self.rfile, 
				headers=self.headers,
				environ={'REQUEST_METHOD':'POST',
		                 'CONTENT_TYPE':self.headers['Content-Type'],
			})
			try:		 
				con = psycopg2.connect(host='localhost', database='Library', user='Atish',password='shivratna') 
				cur = con.cursor()
				cur.execute("SELECT * from books where name like 'Allen';")
				rows = cur.fetchall()
				for row in rows:
					print "ID = ", row[0]
					print "NAME = ", row[1]
					print "LOCATION = ", row[2]
					print "COPIES = ", row[3] 
					print "LANGUAGE= ",row[4]
					print "PATH",row[5]
					print "EDITION",row[6],"\n"
			except psycopg2.DatabaseError, e:
				print 'Error %s' % e    
				sys.exit(1)	
			finally:
				if con:
					con.commit()
					con.close()
			self.send_response(302)
			self.send_header('Location','/')
			self.end_headers()
			return
			
def WebServerThread():			
	try:
		#Create a web server and define the handler to handle the requets
		
		server = HTTPServer(('', PORT_NUMBER), myHandler)
		print 'Started httpserver on port ' , PORT_NUMBER
		
		#Run server infinitely to serve incoming http requests
		server.serve_forever()

	except KeyboardInterrupt:
		#print '^C received, shutting down the web server'
		server.socket.close()

#Method for postgres connection
def postgreconnectionThread():
	con = None
	try:		 
		con = psycopg2.connect(host='localhost', database='Library', user='Atish',password='shivratna') 
		cur = con.cursor()
		"""
		cur.execute('''INSERT INTO Books (Id,Name,Location,NoOfCopies,Language,Edition) 
      VALUES (3, 'Lost World', 'shelf 1', 5, 'English','Second Revised' );''')
		#cur.execute("SET search_path TO public;");
		cur.execute(''' CREATE TABLE LibraryItem(Id SERIAL PRIMARY KEY NOT NULL,Name            TEXT    NOT NULL,Location        TEXT  ,NoOfCopies      INT);''');
		
		cur.execute('''CREATE TABLE Books
		(Language       TEXT    NOT NULL,
		Edition        TEXT    NOT NULL)INHERITS (LibraryItem);''');"""
		#ver = cur.fetchone()
		#print "Table Books created successfully"
		
	except psycopg2.DatabaseError, e:
		print 'Error %s' % e    
		sys.exit(1)	
		
	finally:		
		if con:
			con.commit()
			con.close()
			
#Initialize document clustering			
#def documentCluster():
#	import document_clustering

# Multithreading for parallel execution
# Runs the web server thread
webServer=threading.Thread(target=WebServerThread)
webServer.start()

#Postgres connection
postgreConnection=threading.Thread(target=postgreconnectionThread)
postgreConnection.start()
postgreConnection.join()

#document cluster formation
#documentClusterThred=threading.Thread(target=documentCluster)
#documentClusterThred.start()