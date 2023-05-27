import attr


@attr.s
class PointPayReadyRequestDTO(object):
    product_id = attr.ib(type=id)
    partner_order_id = attr.ib(type=str)
    partner_user_id = attr.ib(type=str)
    item_name = attr.ib(type=str)
    cid_secret = attr.ib(type=str, default=None)

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class KakaoPayReadyResponseDTO(object):
    tid = attr.ib(type=str)
    next_redirect_mobile_url = attr.ib(type=str)

    @classmethod
    def from_dict(cls, data):
        return cls(
            tid=data['tid'],
            next_redirect_mobile_url=data['next_redirect_mobile_url'],
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)
