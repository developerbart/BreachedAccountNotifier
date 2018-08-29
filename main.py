import requests
import json

from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from pylatex import Table, Center, Document, Section, Subsection, Command, Tabular
from pylatex.utils import bold, NoEscape

def check_pwn(email):
	"""Takes a string (email address) as input and checks whether the email
	address is contained within a breach registered in the Haveibeenpwnd database.

	If the request is empty or generates any other errors, nothing is returned.
	This is done to make it testable whether an email address hasn't been pwnd.

	Otherwise the result is a JSON structure of pwnd information.
	"""
	headers = {'api-version': '2', 'User-Agent': 'Pwnbak-checker-Linux'}
	req = requests.get("https://haveibeenpwned.com/api/v2/breachedaccount/%s" % email, headers=headers)
	
	try:
		return req.json()
	except:
		return

def create_tables(pwn_data, pdf, start_entry, stop_entry, counter):
	"""
	Creates tables for use in the PDF document. It takes the output of the check_pwn
	function as a variable pwn_data. PDF equals the LaTeX document object. The start_entry,
	stop_entry and counter are used to limit the size of the table. Otherwise the result
	will be written to one big table. Which turns out ugly in the document.

	The counter value in particular is being used to loop through the classess of data that
	were leaked in the breach. The looping is done to construct a bullet list of classes that
	were breached.

	This function doesn't return anything. It only alters the state of the PDF document object.
	"""
	with pdf.create(Center()) as centered:
		with centered.create(Table(position='h')):
			with pdf.create(Tabular('|l|c|')) as table:
				table.add_hline()
				for entry in pwn_data[start_entry:stop_entry]:
					table.add_row(bold("Title"), pwn_data[counter]["Title"]) 
					table.add_hline()
					table.add_row(bold("Domain"), pwn_data[counter]["Domain"])
					table.add_hline()
					table.add_row(bold("Date of breach"), pwn_data[counter]["BreachDate"])
					table.add_hline()
					first_class = True
					for dataclasses in pwn_data[counter]["DataClasses"]:
						if first_class:
							table.add_row(bold("Affected classes"), dataclasses)
							first_class = False
						else:
							table.add_row("", dataclasses)
					table.add_hline()
					counter = counter + 1
					table.add_hline()


def construct_pdf(email_addr):
	"""
	Takes the list of email addresses as input and makes sure that an API call to Haveibeenpwnd
	is being made for each email address. Afterwards it creates a LaTeX document with a section for
	each email address that was used as input. 

	If the API call doesnt return anything, a standard output text is produced in the LaTeX document.
	This function also calls the function to create tables. Currently I hardcoded the amount of breaches
	that are contained within one table to be 3.

	Finally the function created a PDF file from the LaTeX document in the same directory if this script.
	"""
	pdf = Document()

	pdf.preamble.append(Command('title', 'Overview of breached accounts'))
	pdf.preamble.append(Command('author', 'Python'))
	pdf.preamble.append(Command('date', NoEscape(r'\today')))
	pdf.append(NoEscape(r'\maketitle'))
	
	with pdf.create(Section("Introduction")) as intro_section:
		intro_section.append("This PDF document lists breaches for websites you were registered on. ")
		intro_section.append(" Please note that with each breach the leaked PII is also shown.")
	
	for email_entry in email_addr:
		with pdf.create(Section("Email address: " +  email_entry)) as email_section:	
			data = check_pwn(email_entry)
			start_entry = 0
			stop_entry = 3
			counter = 0
			if data == None:
				email_section.append("The API didn't return anything usable, so probably you're all good!")
			elif stop_entry == len(data):
				create_tables(data, email_section, start_entry, stop_entry, counter)
			else:
				while stop_entry <= (len(data) - 1):
					create_tables(data, email_section, start_entry, stop_entry, counter)
					counter = counter + 3
					start_entry = start_entry + 2
					stop_entry = start_entry + 3
	pdf.generate_pdf("breached")

def send_email(fromaddr, toaddr, smtp_server, username, password):
	"""
	This is the final function. When the PDF file is generated, this function
	transmits the PDF as an attachment in an email to toaddr. fromaddr is used
	to specify the sender. smtp_server, username and password are used to specify
	the SMTP server parameters required to transmit a message.

	Note that STARTTLS is used.
	"""


	message = MIMEMultipart()
	message['From'] = fromaddr
	message['To'] = toaddr
	message['Subject'] = "HaveIBeenPwned overview of breached accounts"

	body = "In the attachments of this email you'll find an overview of haveibeenpwned breaches to which your email addresses belong."
	message.attach(MIMEText(body, 'plain'))
	attachment = open("breached.pdf", "rb")
	part = MIMEBase('application', 'octet-stream')
	part.set_payload((attachment).read())
	encoders.encode_base64(part)
	part.add_header('Content-Disposition', "attachment; filename= breached.pdf")

	message.attach(part)
	server = SMTP(smtp_server, 587)
	server.starttls()
	server.login(username, password)
	text = message.as_string()
	server.sendmail(fromaddr, toaddr, text)
	server.quit()

if __name__ == "__main__":
	"""
	The if statement is used to make sure this script isnt used
	in a module import. Instead this script should be called directly.

	The only thing a user should alter in this script are the variables below.
	"""
	username = "username"
	password = "password"
	smtp_server = "server"
	to_email = "email@domain.tld"
	from_email = "email@domain.tld"
	email_addr = ["email@domain.tld"]

	construct_pdf(email_addr)
	send_email(from_email, to_email, smtp_server, username, password)
