# https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-20-zh
# https://appsecco.com/books/subdomain-enumeration/active_techniques/zone_walking.html

from common.module import Module
from common import utils


class CheckNSEC(Module):
    def __init__(self, domain):
        Module.__init__(self)
        self.domain = self.register(domain)
        self.module = 'check'
        self.source = "CheckNSEC"

    def walk(self):
        domain = self.domain
        while True:
            answer = utils.dns_query(domain, 'NSEC')
            if answer is None:
                break
            subdomain = str()
            for item in answer:
                record = item.to_text()
                subdomains = self.match_subdomains(self.domain, record)
                subdomain = ''.join(subdomains)  # 其实这里的subdomains的长度为1 也就是说只会有一个子域
                self.subdomains = self.subdomains.union(subdomains)
                self.gen_record(subdomains, record)
            if subdomain == self.domain:  # 当查出子域为主域 说明完成了一个循环 不再继续查询
                break
            domain = subdomain
        return self.subdomains

    def run(self):
        """
        类执行入口
        """
        self.begin()
        self.walk()
        self.finish()
        self.save_json()
        self.gen_result()
        self.save_db()


def do(domain):  # 统一入口名字 方便多线程调用
    """
    类统一调用入口

    :param str domain: 域名
    """
    brute = CheckNSEC(domain)
    brute.run()


if __name__ == '__main__':
    do('iana.org')
