import requests
import json
import time
import re

class Bilibili:
    def __init__(self):
        self.ssion = requests.session()
        self.head = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        }

    def get_reply(self, url):
        # get cookies
        self.ssion.get(url)
        # get bv id
        try:
            res = re.search(r'BV([^/?]*)', url).span()
        except Exception as e:
            print('wrong url')
            return []
        bid = url[res[0]:res[1]]
        # get cid
        burl = 'https://api.bilibili.com/x/player/pagelist?bvid=' + bid + '&jsonp=jsonp'
        res = self.ssion.get(burl, headers=self.head).text
        cid = json.loads(res)['data'][0]['cid']
        # get oid
        aurl =  'https://api.bilibili.com/x/web-interface/view?cid='+str(cid)+'&bvid='+bid+''
        res = self.ssion.get(aurl, headers=self.head).text
        oid = str(json.loads(res)['data']['aid'])
        # safe delta
        time.sleep(0.1)
        # replies
        contents = []
        # scroll stage
        now = 0
        # no more stage
        tried = 0
        # mark no more new reply
        isnew = True
        # count no more new reply
        lianxu = 0
        # reply api
        rurl = "https://api.bilibili.com/x/v2/reply/main"
        while True:
            isnew = False
            data = {
                "mode" : 3,
                "next" : now,
                "oid" :  oid,
                "plat" : 1,
                "type" : 1
            }
            # when next == 0, it had a extra null key
            if now == 0:
                data["seek_rpid"] = ""
            # get reply
            reply = self.ssion.get(rurl, params=data,headers=self.head)
            try:
                replies = json.loads(reply.text)['data']['replies']
                for each in replies:
                    # IF you want, you can get all replies to this reply, and it replies's replies...
                    # print(each['replies'][0]['contents']['message'])
                    each = each['content']['message']
                    if each not in contents:
                        contents.append(each)
                        isnew = True
                now += 1
            except Exception as e:
                if tried < 3:
                    now -= 1
                    tried += 1
                else:
                    tried = 0
                pass
            if lianxu > 6:
                break
            if isnew:
                lianxu = 0
            else:
                lianxu += 1
            if now % 20 == 0:
                # safe delta
                time.sleep(5)
            else:
                # safe delta
                time.sleep(0.5)
        return contents
