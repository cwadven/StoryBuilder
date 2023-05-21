import requests
from abc import ABC
from django.conf import settings
from typing import Optional


class KakaoPay:
    def __init__(self, handler: 'KakaoPayHandler') -> None:
        self.kakao_pay_api_key = settings.KAKAO_PAY_API_KEY
        self.kakao_pay_ready_url = 'https://kapi.kakao.com/v1/payment/ready'
        self.kakao_pay_approve_url = 'https://kapi.kakao.com/v1/payment/approve'
        self.headers = {
            'Authorization': 'KakaoAK ' + self.kakao_pay_api_key,
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        }
        self.handler = handler

    def ready_to_pay(self, order_id: str, user_id: str, product_name: str, quantity: str, total_amount: str,
                     tax_free_amount: str) -> dict:
        """
        아래와 같은 형태로 return
        {
            "tid": "T469b847306d7b2dc394",
            "tms_result": false,
            "next_redirect_app_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/aInfo",
            "next_redirect_mobile_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/mInfo",
            "next_redirect_pc_url": "https://online-pay.kakao.com/mockup/v1/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46/info",
            "android_app_scheme": "kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46",
            "ios_app_scheme": "kakaotalk://kakaopay/pg?url=https://online-pay.kakao.com/pay/mockup/1d61e5d04016bd94c9ed54406bb51f1194e3772ce297a097fdb3e3604fc42e46",
            "created_at": "2023-05-21T15:20:55"
        }
        """
        params = {
            'cid': settings.KAKAO_PAY_CID,
            'partner_order_id': order_id,
            'partner_user_id': user_id,
            'item_name': product_name,
            'quantity': quantity,
            'total_amount': total_amount,
            'tax_free_amount': tax_free_amount,
            'approval_url': self.handler.approval_url,
            'cancel_url': self.handler.cancel_url,
            'fail_url': self.handler.fail_url,
        }
        res = requests.post(self.kakao_pay_ready_url, headers=self.headers, params=params)
        return res.json()

    def approve_payment(self, tid: str, pg_token: str, order_id: str, user_id: str) -> dict:
        """
        아래와 같은 형태로 return
        {
            "aid": "A469b85a306d7b2dc395",
            "tid": "T469b847306d7b2dc394",
            "cid": "TC0ONETIME",
            "partner_order_id": "test1",
            "partner_user_id": "1",
            "payment_method_type": "MONEY",
            "item_name": "1000 포인트",
            "item_code": "",
            "quantity": 1,
            "amount": {
                "total": 1000,
                "tax_free": 0,
                "vat": 91,
                "point": 0,
                "discount": 0,
                "green_deposit": 0
            },
            "created_at": "2023-05-21T15:20:55",
            "approved_at": "2023-05-21T15:25:31"
        }
        """
        params = {
            'cid': settings.KAKAO_PAY_CID,
            'tid': tid,
            'partner_order_id': order_id,
            'partner_user_id': user_id,
            'pg_token': pg_token,
        }
        res = requests.post(self.kakao_pay_approve_url, headers=self.headers, params=params)
        return res.json()


class KakaoPayHandler(ABC):
    approval_url: Optional[str] = None
    cancel_url: Optional[str] = None
    fail_url: Optional[str] = None


class KakaoPayPointHandler(KakaoPayHandler):
    def __init__(self):
        self.approval_url = 'http://localhost:9000/v1/payment/test_success'
        self.cancel_url = 'http://localhost:9000/v1/payment/test_cancel'
        self.fail_url = 'http://localhost:9000/v1/payment/test_fail'
