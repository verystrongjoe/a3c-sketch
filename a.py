import threading, requests, time


class HtmlGetter(threading.Thread):
    def __init__(self, url):
        print('what!!')
        threading.Thread.__init__(self)
        self.url = url

    def run(self):
        resp = requests.get(self.url)
        time.sleep(1)
        print(self.url, len(resp.text), ' chars')


t = HtmlGetter('http://google.com')
t.start()

print("### End ###")