import re


def normalize(text):
    text=text.replace('\r\n','\n').replace('\r','\n').replace('\u00a0',' ').replace('\ufeff','')
    return '\n'.join(re.sub(r'[\t ]+',' ',line).strip() for line in text.split('\n')).strip()
