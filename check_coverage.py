import sys

from bs4 import BeautifulSoup

coverage_percent:int
coverage_threshold = int(sys.argv[1])

with open('htmlcov/index.html', 'r') as coverage_file: #pylint:disable=unspecified-encoding
    soup = BeautifulSoup(coverage_file.read(), "html.parser")
    coverage_percent =  int(soup.find('span',{'class':'pc_cov'}).text.replace('%',''))

if coverage_percent < coverage_threshold:
    print(
        'Coverage of ' + str(coverage_percent) +' is below threshold of ' + str(coverage_threshold)
        )
    sys.exit(1)
else:
    print('Good enough coverage! (' + str(coverage_percent) + ')')
    sys.exit(0)
