from getpass import getpass
import requests
from sys import argv
import re
from time import sleep
UA='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:56.0) Gecko/20100101 Firefox/56.0'


def csrf(html):
    result = re.search('name="CSRFValue" value="?([0-9]+)"?>', html, flags=(re.MULTILINE | re.IGNORECASE))
    if result == None:
        print('html body len %d returned no matches :(' % len(html))
        print('heres an excerpt:')
        index = html.find('CSRFValue')
        print(html[index:index+30])
        return None
    return result.group(1)

def reboot(host, sess):
    formaddr = host + '/goform/system/switch-mode'
    mode = 4 # router mode in my fw version, not like it lets you switch anyway...

    body = sess.get(host + '/system/switch-mode.asp').text
    token = csrf(body)
    data = { 'CSRFValue': token, 'SwitchMode': 4}
    result = sess.post(formaddr, data=data)
    return result

def login(host, pw, user='admin', extra_data={}, sess=None):
    formaddr = host + '/goform/login'
    sess = sess or requests.session()
    sess.headers.update({'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'})
    token = csrf(sess.get(host).text)
    print('token:', token)
    data = { 'CSRFValue': token, 'loginUsername': user, 'loginPassword': pw, 'logoffUser': 0}
    data.update(extra_data)
    sleep(0.5)
    try:
        response = sess.post(formaddr, data=data, headers={'Referer':host+'/'})
        return sess, response
    except Exception as ex:
        print('login faiiiiil')
        print(ex)
        return None

if __name__ == '__main__':
    if len(argv) < 2:
        print('please specify ip/hostname of your upc router/modem abomination, e.g %s 192.168.0.1' % argv[0])
        exit(1)
    host = 'http://'+argv[1].strip()
    print('please enter admin pw for %s' % host)
    pw = getpass()

    sess, response = login(host,pw)
    response = reboot(host, sess)
    print(response,'\n',response.text)
