"""Canonical selector values are independent of translated widget labels."""
def valid_group(catalog,value):
 return value if value in {'ALL',*(m['group'] for m in catalog)} else 'ALL'

def indicator_options(catalog,group):
 return [m['code'] for m in catalog if group=='ALL' or m['group']==group]

def valid_indicator(options,value):
 return value if value in options else options[0]
