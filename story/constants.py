from config.common.enums import StrValueLabel, IntValueSelector


class StoryErrorMessage(StrValueLabel):
    ALREADY_SOLVED = ('ALREADY_SOLVED', '이미 문제를 해결한 기록이 있습니다.')


class StoryLevel(IntValueSelector):
    EASY = (0, '하')
    NORMAL = (1, '중')
    HARD = (2, '상')
    EXPERT = (3, '최상')
    NOT_FOUND = (999, '?')

    @classmethod
    def _missing_(cls, value):
        return cls.NOT_FOUND


DEFAULT_POPULAR_KILL_SWITCH_STORY_COUNT = 6
