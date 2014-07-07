#! python

import requests

def get_website(url):
    return requests.get(url)

if __name__ == '__main__':
    response = get_website('http://localhost:8001/admin/')

    if response.status_code == 200:
        print 'HTTP Status Code: OK'
    else:
        print 'Error: Unexpected HTTP Status Code %d' % (response.status_code)
        exit(1)
