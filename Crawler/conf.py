from datetime import datetime, timedelta

'''
The daterange is [STARTDATE, ENDDATE-1]
'''

''' week '''
# STARTDATE = datetime.strptime('06 15 2019', '%m %d %Y')

''' month '''
STARTDATE = datetime.strptime('05 22 2019', '%m %d %Y') # month

''' 1 day testing '''
# STARTDATE = datetime.strptime('06 21 2019', '%m %d %Y') # test

ENDDATE = datetime.strptime('06 22 2019', '%m %d %Y')


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)