import google.generativeai as genai
import google.api_core.exceptions as exceptions
import sys
import random
import os

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def read_properties_file(filename):
    properties = {}
    with open(filename, 'r') as file:
        for line in file:
            # Ignore lines starting with '#' (comments) or empty lines
            if line.strip() and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                properties[key.strip()] = value.strip()
    return properties

def count_lines(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            num_lines = len(lines)
        return num_lines
    except FileNotFoundError:
        print("File not found!")
        return -1  # Return -1 to indicate error
    
def generate_random_numbers(n, start, end):
    random_numbers = []
    while len(random_numbers) < n:
        new_number = random.randint(start, end)
        if new_number not in random_numbers:
            random_numbers.append(new_number)
    return random_numbers

def get_nth_line(filename, n):
    try:
        with open(filename, 'r') as file:
            for i, line in enumerate(file):
                if i == n - 1:  # Adjusting for 0-based indexing
                    return line.strip()
            # If the loop completes without finding the nth line
            return f"Line {n} does not exist in the file."
    except FileNotFoundError:
        return "File not found!"
    
def create_pdf(text, pdf_file):
        # Define the styles for bold and bullet points
        styles = getSampleStyleSheet()
        style_bold = styles['Heading1']
        style_bullet = styles['Bullet']

        # Split the text by newline
        paragraphs = text.split('\n')

        # Create a PDF document
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)

        # Initialize a list to hold the content
        content = []

        # Iterate through each paragraph and add to the content list with appropriate style
        for para in paragraphs:
            content.append(Paragraph(para))

        # Build the PDF document
        doc.build(content)

        print(f"PDF created successfully: {pdf_file}")

""" keyfile = 'key.txt'
properties = read_properties_file(keyfile)

GOOGLE_API_KEY = properties['key'] """

GOOGLE_API_KEY = input('Enter API KEY: ')

print('api key = ' + GOOGLE_API_KEY)

genai.configure(api_key=GOOGLE_API_KEY)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print(f'{type(e).__name__}: {e}')
    sys.exit(1)
""" except exceptions.InvalidArgument as ex:
    print('Error: ' + ex.message)
    sys.exit(1) """

model = genai.GenerativeModel('gemini-1.0-pro')

wordlist = 'wordlist.txt'

num_lines = count_lines(wordlist)
if num_lines != -1:
    print("Number of lines in the file:", num_lines)

while True:

    n = int(input('Enter number of documents to generate: '))

    random_numbers = generate_random_numbers(n,0,num_lines-1)

    words = []

    print('List of random words: ')

    for n in random_numbers:
        word = get_nth_line(wordlist, n)
        words.append(word)
        print(word)

    for i in range (len(words)):
        print(f'\nDocument #{i}:\n')
        try:
            word = words[i]
            message = f"Write an essay about {word} in Markdown format"
            print(f'Message: {message}')
            response = model.generate_content(message)
            print('\nResponse:\n')
            print(response.text)
            create_pdf(response.text,"output/output.pdf")
        except Exception as e:
            print(f'{type(e).__name__}: {e}')

    again = input('Again? (Y/N): ').strip().upper()
    
    if(again == 'Y'):
        continue
    elif(again == 'N'):
        break
    else:
        print('Invalid input. Please enter Y or N')

