import grequests as greq, sys

list_of_p_domains = [
    'https://www.hrzzhfs.xyz/', 
    'https://www.financial-pay.info/', 
    'https://www.westernunion-pay.com/',
    'https://dkozzlfods.info/', 
    'https://www.online-shopping-payment.com/',
    'https://www.walmart-payment.com/',
    'https://etooicdfi.studio/',
    'https://www.client-mail-services.com/',
    'https://mail.google-services.com/'
]

def test_request():
# Make sure that grequest is working as expected
    try:
        r = greq.get('https://www.google.com/')
        print('Google is online, this function is working.')
    except:
        sys.exit('Something is wrong, abandon ship.')

def exception_handler(res, excp):
    print('Request failed: {}'.format(res.url))

def async_requests():
    # Trying async to be fancy
    rs = (greq.get(u) for u in list_of_p_domains)
    try:
        reqs = greq.map(rs, exception_handler=exception_handler)
        for link in reqs:
            print('Website ONLINE: {}'.format(link.url))
    except:
        print('One of more of the asynchronous requests failed.')

if __name__ == '__main__':
    test_request()
    async_requests()
