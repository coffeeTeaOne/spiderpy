import random
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware
from ICrawlerSpiders import useragent


class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        # 这句话用于随机选择user-agent
        ua = random.choice(useragent.user_agent_list)
        if ua:
            print('User-Agent:' + ua)
            request.headers.setdefault('User-Agent', ua)

            # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape