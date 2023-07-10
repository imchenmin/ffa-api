import time
import math
from collections import defaultdict
from typing import Dict, Set
import random


class RateLimit(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after


class BackendError(Exception):
    pass


class PhoneAuthenticator:
    def __init__(self, rate_limit_secs: int):
        self.rate_limit_secs = rate_limit_secs
        self._num_last_sent: Dict[str, int] = defaultdict(lambda: -rate_limit_secs)
        self._num_codes: Dict[str, Set[str]] = defaultdict(set)

    def opcode_generator(self, digit: int):
        l = []
        for i in range(digit):
            rand_num = random.randint(0, 9)
            l.append(str(rand_num))
        return ''.join(l)

    def send(self, num: str):
        interval = time.time() - self._num_last_sent[num]
        if interval < self.rate_limit_secs:
            raise RateLimit(math.ceil(self.rate_limit_secs - interval))
        # if app.config.get("REAL_SMS_SERVICE"):
        #     opcode = self.opcode_generator(6)
        #     # TODO: add per-device limit
        #     # TODO: send code
        #     client = AcsClient(app.config.get("ALIYUN_ACCESS_KEY_ID"), \
        #                        app.config.get("ALIYUN_ACCESS_KEY_SECRET"), \
        #                        app.config.get("ALIYUN_REGION"))
        #
        #     request = CommonRequest()
        #     request.set_accept_format('json')
        #     request.set_domain('dysmsapi.aliyuncs.com')
        #     request.set_method('POST')
        #     request.set_protocol_type('https')  # https | http
        #     request.set_version('2017-05-25')
        #     request.set_action_name('SendSms')
        #
        #     request.add_query_param('RegionId', "cn-hangzhou")
        #     request.add_query_param('PhoneNumbers', num)
        #     request.add_query_param('SignName', "路边停车")
        #     request.add_query_param('TemplateCode', "SMS_193521622")
        #     request.add_query_param('TemplateParam', "{\"code\":\"%s\"}" % opcode)
        #     response = client.do_action_with_exception(request)
        #     print(str(response, encoding='utf-8'))
        else:
            # Do nothing with sms, return 745170
            opcode = "745170"
        self._num_codes[num].add(opcode)
        self._num_last_sent[num] = time.time()

    def verify(self, num: str, code: str) -> bool:
        if code in self._num_codes[num]:
            del self._num_codes[num]
            return True
        return False
