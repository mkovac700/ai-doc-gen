import google.generativeai as genai
import sys
import random
import os
import dotenv
import uuid

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from markdown2 import markdown

DIR = os.path.dirname(os.path.realpath(__file__))

def count_lines(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            num_lines = len(lines)
        return num_lines
    except FileNotFoundError:
        print(f"File {filename} not found!")
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
        return f"File {filename} not found!"
    
def create_pdf(text):
        # Define the styles 
        #styles = getSampleStyleSheet()

        # Define styles for headings
        heading_styles = [
            None,  # No style for level 0 (not used in Markdown)
            getSampleStyleSheet()['Heading1'],
            getSampleStyleSheet()['Heading2'],
            getSampleStyleSheet()['Heading3']
        ]

        paragraphs = text.split('\n')

        content = []

        for para in paragraphs:
            # Heading detection
            if para.startswith('#'):
                level = min(para.count('#'), 3)  # Maximum level 3 heading
                heading_style = heading_styles[level]
                content.append(Paragraph(para.strip('# '), heading_style))
            elif para == "":
                content.append(Paragraph(para))
            else:
                html_content = markdown(para)
                content.append(Paragraph(html_content))

        # Document settings
        unique_filename = str(uuid.uuid4()) + '.pdf'

        output_file = os.path.join(DIR,'output/',unique_filename)

        # Create a PDF document
        doc = SimpleDocTemplate(output_file, pagesize=letter)

        # Build the PDF document

        doc.build(content)

        print(f"\nPDF created successfully: {output_file}")

def check_output_dir():
    path = os.path.join(DIR,'output/')

    try:
        os.mkdir(path)
        print('Output folder created successfully!')
    except OSError as e:
        print(f'{type(e).__name__}: {e}')

env_path = os.path.join(DIR,'.env')

if dotenv.get_key(env_path,'GOOGLE_API_KEY') is None:
    print('API key not found! This program requires Gemini AI API key to work. Please visit https://ai.google.dev/ to obtain key and enter it below.')
    key = input('\nEnter API key: ')

    dotenv.set_key(env_path,'GOOGLE_API_KEY',key)

dotenv.load_dotenv(dotenv_path=env_path)

# GOOGLE_API_KEY = input('Enter API KEY: ')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

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

wordlist = os.path.join(DIR,'wordlist.txt')

num_lines = count_lines(wordlist)
if num_lines != -1:
    print("Number of lines in the file:", num_lines)
else:
    sys.exit(1)

check_output_dir()

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
            print('Generating response...')
            response = model.generate_content(message)
            print('\nResponse:\n')
            print(response.text)
            create_pdf(response.text)
        except Exception as e:
            print(f'{type(e).__name__}: {e}')

    again = input('Again? (Y/N): ').strip().upper()
    
    if(again == 'Y'):
        continue
    elif(again == 'N'):
        break
    else:
        print('Invalid input. Please enter Y or N')

