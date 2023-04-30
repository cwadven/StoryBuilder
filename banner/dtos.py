import attr

from banner.models import Banner


@attr.s
class BannerListItemDTO(object):
    id = attr.ib(type=int)
    title = attr.ib(type=str)
    background_image = attr.ib(type=str)
    background_color = attr.ib(type=str)
    banner_type_name = attr.ib(type=str)

    @classmethod
    def of(cls, banner: Banner):
        return cls(
            id=banner.id,
            title=banner.title,
            background_image=banner.background_image,
            background_color=banner.background_color,
            banner_type_name=banner.banner_type.name,
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)


@attr.s
class BannerDetailItemDTO(object):
    id = attr.ib(type=int)
    title = attr.ib(type=str)
    description = attr.ib(type=str)
    background_image = attr.ib(type=str)
    background_color = attr.ib(type=str)
    banner_type_name = attr.ib(type=str)
    created_at = attr.ib(type=str)

    @classmethod
    def of(cls, banner: Banner):
        return cls(
            id=banner.id,
            title=banner.title,
            description=banner.description,
            background_image=banner.background_image,
            background_color=banner.background_color,
            banner_type_name=banner.banner_type.name,
            created_at=banner.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        )

    def to_dict(self):
        return attr.asdict(self, recurse=True)
