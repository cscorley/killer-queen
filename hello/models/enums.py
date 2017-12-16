import enum
import inspect

class BaseEnum(enum.IntEnum):
    @classmethod
    def choices(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not(inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not(m[0][:2] == '__')]
        # format into django choice tuple
        return tuple([(int(p[1]), p[0]) for p in props])

@enum.unique
class TournamentStyle(BaseEnum):
    SINGLE_ELIMINATION_BRACKET = 1
    DOUBLE_ELIMINATION_BRACKET = 2
    ROUND_ROBIN = 3