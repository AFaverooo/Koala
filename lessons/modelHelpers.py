from lessons.models import Lesson,UserAccount,UserRole, Gender,LessonStatus,LessonType,LessonDuration

"""helpers to test validity of TextChoices for various models"""
def is_valid_gender(UserAccount):
    return UserAccount.gender in {
        Gender.MALE,
        Gender.FEMALE,
        Gender.PNOT,
        }

def is_valid_role(UserAccount):
    return UserAccount.role in {
        UserRole.STUDENT,
        UserRole.ADMIN,
        UserRole.DIRECTOR,
        UserRole.TEACHER,
        }

def is_valid_lessonStatus(Lesson):
    return Lesson.is_booked in {
        LessonStatus.UNSAVED,
        LessonStatus.PENDING,
        LessonStatus.BOOKED,
        }

def is_valid_lessonDuration(Lesson):
    return Lesson.duration in {
        LessonDuration.THIRTY,
        LessonDuration.FOURTY_FIVE,
        LessonDuration.HOUR,
        }

def is_valid_lessonType(Lesson):
    return Lesson.type in {
        LessonType.INSTRUMENT,
        LessonType.THEORY,
        LessonType.PRACTICE,
        LessonType.PERFORMANCE,
        }
