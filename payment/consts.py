from config.common.enums import StrValueLabel


class OrderStatus(StrValueLabel):
    READY = ('READY', '주문 준비중')
    FAIL = ('FAIL', '주문 실패')
    CANCEL = ('CANCEL', '주문 취소')
    SUCCESS = ('SUCCESS', '주문 성공')
    REFUND = ('REFUND', '환불')


class ProductType(StrValueLabel):
    POINT = ('POINT', '포인트')
    ADDITIONAL_POINT = ('ADDITIONAL_POINT', '포인트')


class PaymentType(StrValueLabel):
    KAKAOPAY = ('KAKAOPAY', '카카오페이')
    KAKAOPAY_CARD = ('KAKAOPAY_CARD', '카카오페이-카드')
    KAKAOPAY_MONEY = ('KAKAOPAY_MONEY', '카카오페이-머니')


class PointGivenStatus(StrValueLabel):
    READY = ('READY', '지급 준비중')
    SUCCESS = ('SUCCESS', '지급 완료')
    FAIL = ('FAIL', '지급 실패')
    CANCEL = ('CANCEL', '지급 취소')
