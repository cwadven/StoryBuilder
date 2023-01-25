import attr


@attr.s
class UserPointInfoResponseDTO(object):
    total_point = attr.ib(type=int)

    def to_dict(self):
        return attr.asdict(self, recurse=True)
