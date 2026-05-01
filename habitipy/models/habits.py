from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import Annotated, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..pagination import Pagination


class HabitipyBaseModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    def to_request_body(self) -> dict[str, object]:
        return cast(
            dict[str, object],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )

    def to_query_params(self) -> dict[str, str]:
        serialized: dict[str, str] = {}
        for key, value in self.model_dump(by_alias=True, exclude_none=True, mode="json").items():
            if isinstance(value, bool):
                serialized[key] = str(value).lower()
            else:
                serialized[key] = str(value)
        return serialized


def _prune_empty_dicts(value: object) -> object | None:
    if isinstance(value, dict):
        pruned = {
            key: pruned_value
            for key, item in value.items()
            if (pruned_value := _prune_empty_dicts(item)) is not None
        }
        return pruned or None

    if isinstance(value, list):
        return [
            pruned_item for item in value if (pruned_item := _prune_empty_dicts(item)) is not None
        ]

    return value


class HabitType(str, Enum):
    GOOD = "good"
    BAD = "bad"


class LogMethod(str, Enum):
    MANUAL = "manual"
    AUTO = "auto"


class GoalPeriodicity(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class UnitSymbol(str, Enum):
    M = "m"
    KM = "kM"
    FT = "ft"
    YD = "yd"
    MI = "mi"
    FLOOR = "floor"
    LITER = "L"
    MILLILITER = "mL"
    FLUID_OUNCE = "fl oz"
    CUP = "cup"
    SECOND = "sec"
    MINUTE = "min"
    HOUR = "hr"
    MILLISECOND = "ms"
    KILOGRAM = "kg"
    GRAM = "g"
    MILLIGRAM = "mg"
    OUNCE = "oz"
    POUND = "lb"
    MICROGRAM = "mcg"
    JOULE = "J"
    KILOJOULE = "kJ"
    KILOCALORIE = "kCal"
    CALORIE = "cal"
    REP = "rep"
    STEP = "step"


class HabitStackTriggerType(str, Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    REMINDER = "reminder"


class HabitStackTimerType(str, Enum):
    IMMEDIATELY = "immediately"
    AFTER = "after"


class ReminderTime(HabitipyBaseModel):
    hour: int
    minute: int


class ReminderOccurrenceFilter(HabitipyBaseModel):
    week_days: list[int] | None = Field(default=None, alias="weekDays")


class TimeTrigger(HabitipyBaseModel):
    time: ReminderTime
    occurrence_filter: ReminderOccurrenceFilter | None = Field(
        default=None, alias="occurrenceFilter"
    )
    show_live_activity: bool | None = Field(default=None, alias="showLiveActivity")
    show_as_alarm: bool | None = Field(default=None, alias="showAsAlarm")


class HabitStack(HabitipyBaseModel):
    id: str | None = None
    condition_habit_id: str = Field(alias="conditionHabitId")
    type: HabitStackTriggerType
    timer_type: HabitStackTimerType = Field(alias="timerType")
    timer_delay_secs: int | None = Field(default=None, alias="timerDelaySecs")


HabitCreateReminderTime = ReminderTime
HabitCreateReminderOccurrenceFilter = ReminderOccurrenceFilter
HabitCreateTimeTrigger = TimeTrigger
HabitCreateHabitStack = HabitStack


class HabitCreateReminders(HabitipyBaseModel):
    time_triggers: list[TimeTrigger] = Field(default_factory=list, alias="timeTriggers")
    habit_stacks: list[HabitStack] = Field(default_factory=list, alias="habitStacks")


class HabitUpdateReminders(HabitipyBaseModel):
    time_triggers: list[TimeTrigger] | None = Field(default=None, alias="timeTriggers")
    habit_stacks: list[HabitStack] | None = Field(default=None, alias="habitStacks")


class Reminders(HabitipyBaseModel):
    time_triggers: list[TimeTrigger] = Field(default_factory=list, alias="timeTriggers")
    habit_stacks: list[HabitStack] = Field(default_factory=list, alias="habitStacks")


class DailyOccurrence(HabitipyBaseModel):
    type: Literal["daily"]


class WeekDaysOccurrence(HabitipyBaseModel):
    type: Literal["weekDays"]
    days: list[int]


class MonthDaysOccurrence(HabitipyBaseModel):
    type: Literal["monthDays"]
    days: list[int]


class IntervalDaysOccurrence(HabitipyBaseModel):
    type: Literal["intervalDays"]
    interval: int


HabitCreateDailyOccurrence = DailyOccurrence
HabitCreateWeekDaysOccurrence = WeekDaysOccurrence
HabitCreateMonthDaysOccurrence = MonthDaysOccurrence
HabitCreateIntervalDaysOccurrence = IntervalDaysOccurrence


Occurrence = Annotated[
    DailyOccurrence | WeekDaysOccurrence | MonthDaysOccurrence | IntervalDaysOccurrence,
    Field(discriminator="type"),
]


HabitCreateOccurrence = Annotated[
    DailyOccurrence | WeekDaysOccurrence | MonthDaysOccurrence | IntervalDaysOccurrence,
    Field(discriminator="type"),
]


class DateEndCondition(HabitipyBaseModel):
    id: str
    type: Literal["date"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    date: date


class StreakEndCondition(HabitipyBaseModel):
    id: str
    type: Literal["streak"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    period_type: GoalPeriodicity = Field(alias="periodType")
    streak_length: int = Field(alias="streakLength")


class SuccessPeriodsEndCondition(HabitipyBaseModel):
    id: str
    type: Literal["successPeriods"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    period_type: GoalPeriodicity = Field(alias="periodType")
    total_periods: int = Field(alias="totalPeriods")


class TotalLogValueEndCondition(HabitipyBaseModel):
    id: str
    type: Literal["totalLogValue"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    total_log_value: float = Field(alias="totalLogValue")


class HabitCreateDateEndCondition(HabitipyBaseModel):
    type: Literal["date"]
    date: date


class HabitCreateStreakEndCondition(HabitipyBaseModel):
    type: Literal["streak"]
    streak_length: int = Field(alias="streakLength")


class HabitCreateSuccessPeriodsEndCondition(HabitipyBaseModel):
    type: Literal["successPeriods"]
    total_periods: int = Field(alias="totalPeriods")


class HabitCreateTotalLogValueEndCondition(HabitipyBaseModel):
    type: Literal["totalLogValue"]
    total_log_value: float = Field(alias="totalLogValue")


EndCondition = Annotated[
    DateEndCondition | StreakEndCondition | SuccessPeriodsEndCondition | TotalLogValueEndCondition,
    Field(discriminator="type"),
]


HabitCreateEndCondition = Annotated[
    HabitCreateDateEndCondition
    | HabitCreateStreakEndCondition
    | HabitCreateSuccessPeriodsEndCondition
    | HabitCreateTotalLogValueEndCondition,
    Field(discriminator="type"),
]


class HabitCreateGoal(HabitipyBaseModel):
    periodicity: GoalPeriodicity
    value: float
    unit: UnitSymbol


class Goal(HabitipyBaseModel):
    id: str
    created_at: datetime = Field(alias="createdAt")
    periodicity: GoalPeriodicity
    value: float
    unit: UnitSymbol
    is_active: bool | None = Field(default=None, alias="isActive")


class Area(HabitipyBaseModel):
    id: str
    name: str
    color_hex: str | None = Field(default=None, alias="colorHex")
    icon: str | None = None
    created_at: datetime = Field(alias="createdAt")
    description: str | None = None


class AreaResponse(HabitipyBaseModel):
    data: Area


class AreaListResponse(HabitipyBaseModel):
    data: list[Area]


class AreaCreateRequest(HabitipyBaseModel):
    name: str
    color_hex: str | None = Field(default=None, alias="colorHex")
    icon: str | None = None


class AreaUpdateRequest(HabitipyBaseModel):
    name: str | None = None
    color_hex: str | None = Field(default=None, alias="colorHex")
    icon: str | None = None


class TimeOfDay(HabitipyBaseModel):
    id: str
    name: str
    icon: str | None = None
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    color_hex: str | None = Field(default=None, alias="colorHex")


class Habit(HabitipyBaseModel):
    id: str
    name: str
    icon: str | None = None
    color_hex: str = Field(alias="colorHex")
    type: HabitType
    description: str | None = None
    occurrence: Occurrence
    start_date: date = Field(alias="startDate")
    created_at: datetime = Field(alias="createdAt")
    is_archived: bool = Field(alias="isArchived")
    log_method: LogMethod = Field(alias="logMethod")
    challenge_id: str | None = Field(default=None, alias="challengeId")
    reminders: Reminders | None = None
    end_condition: EndCondition | None = Field(default=None, alias="endCondition")
    goals: list[Goal]
    custom_unit_name: str | None = Field(default=None, alias="customUnitName")
    areas: list[Area] = Field(default_factory=list)
    time_of_days: list[TimeOfDay] = Field(default_factory=list, alias="timeOfDays")


class HabitListPage(HabitipyBaseModel):
    data: list[Habit]
    pagination: Pagination


class HabitJournalStatus(str, Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    IN_PROGRESS = "inprogress"


class HabitJournalStreakUnit(str, Enum):
    DAY = "day"


class HabitJournalCurrentStreak(HabitipyBaseModel):
    length: int
    unit: HabitJournalStreakUnit


class HabitJournalProgress(HabitipyBaseModel):
    current: float
    target: float
    unit: str
    periodicity: GoalPeriodicity


class HabitJournalLogInfo(HabitipyBaseModel):
    type: LogMethod


class HabitJournalEntry(HabitipyBaseModel):
    id: str
    name: str
    status: HabitJournalStatus
    color_hex: str | None = Field(default=None, alias="colorHex")
    icon: str | None = None
    time_of_day_ids: list[str] = Field(default_factory=list, alias="timeOfDayIds")
    type: HabitType
    current_streak: HabitJournalCurrentStreak | None = Field(default=None, alias="currentStreak")
    progress: HabitJournalProgress | None = None
    log_info: HabitJournalLogInfo | None = Field(default=None, alias="logInfo")


class HabitJournalPage(HabitipyBaseModel):
    data: list[HabitJournalEntry]


class HabitStatisticsUnit(HabitipyBaseModel):
    id: str | None = None
    name: str | None = None
    symbol: UnitSymbol | str

    @field_validator("symbol", mode="before")
    @classmethod
    def coerce_known_symbol(cls, value: object) -> object:
        if isinstance(value, str):
            try:
                return UnitSymbol(value)
            except ValueError:
                return value
        return value


class HabitStatisticsDailyProgress(HabitipyBaseModel):
    date: date
    total_log: float = Field(alias="totalLog")
    status: HabitJournalStatus


class HabitStatistics(HabitipyBaseModel):
    id: str
    name: str
    type: HabitType
    total_logs: float = Field(alias="totalLogs")
    skips: int
    fails: int
    completions: int
    unit: HabitStatisticsUnit
    periodicity: GoalPeriodicity
    avg: float
    daily_progress: list[HabitStatisticsDailyProgress] = Field(
        default_factory=list, alias="dailyProgress"
    )


class HabitStatisticsResponse(HabitipyBaseModel):
    data: HabitStatistics


class HabitResponse(HabitipyBaseModel):
    data: Habit


class SuccessMessageResponse(HabitipyBaseModel):
    message: str


class HabitLogRequest(HabitipyBaseModel):
    unit_symbol: UnitSymbol = Field(alias="unitSymbol")
    value: float
    target_date: date | None = Field(default=None, alias="targetDate")


class HabitLogResponse(SuccessMessageResponse):
    pass


class HabitLogActionRequest(HabitipyBaseModel):
    target_date: date | None = Field(default=None, alias="targetDate")


class MoodLevel(str, Enum):
    VERY_LOW = "veryLow"
    LOW = "low"
    NEUTRAL = "neutral"
    HIGH = "high"
    VERY_HIGH = "veryHigh"


class HabitNote(HabitipyBaseModel):
    id: str
    content: str | None = None
    mood_level: MoodLevel | None = Field(default=None, alias="moodLevel")
    photos: list[str] | None = None
    created_at: datetime = Field(alias="createdAt")


class HabitNoteListResponse(HabitipyBaseModel):
    data: list[HabitNote]


class HabitNoteWriteRequest(HabitipyBaseModel):
    content: str | None = None
    mood_level: MoodLevel | None = Field(default=None, alias="moodLevel")
    photos: list[str] | None = None

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> HabitNoteWriteRequest:
        if not self.model_fields_set:
            raise ValueError("At least one note field must be provided.")
        return self


class HabitNoteCreateRequest(HabitNoteWriteRequest):
    pass


class HabitNoteUpdateRequest(HabitNoteWriteRequest):
    def to_request_body(self) -> dict[str, object]:
        return cast(
            dict[str, object],
            self.model_dump(by_alias=True, exclude_unset=True, mode="json"),
        )


class HabitCreateRequest(HabitipyBaseModel):
    name: str
    type: HabitType
    description: str | None = None
    occurrence: HabitCreateOccurrence | None = None
    start_date: date | None = Field(default=None, alias="startDate")
    icon: str | None = None
    color_hex: str | None = Field(default=None, alias="colorHex")
    custom_unit_name: str | None = Field(default=None, alias="customUnitName")
    area_ids: list[str] | None = Field(default=None, alias="areaIds")
    time_of_day_ids: list[str] | None = Field(default=None, alias="timeOfDayIds")
    goal: HabitCreateGoal | None = None
    reminders: HabitCreateReminders | None = None
    end_condition: HabitCreateEndCondition | None = Field(default=None, alias="endCondition")


class HabitUpdateRequest(HabitipyBaseModel):
    name: str | None = None
    description: str | None = None
    occurrence: HabitCreateOccurrence | None = None
    start_date: date | None = Field(default=None, alias="startDate")
    icon: str | None = None
    color_hex: str | None = Field(default=None, alias="colorHex")
    custom_unit_name: str | None = Field(default=None, alias="customUnitName")
    area_ids: list[str] | None = Field(default=None, alias="areaIds")
    time_of_day_ids: list[str] | None = Field(default=None, alias="timeOfDayIds")
    goal: HabitCreateGoal | None = None
    reminders: HabitUpdateReminders | None = None
    end_condition: HabitCreateEndCondition | None = Field(default=None, alias="endCondition")

    def to_request_body(self) -> dict[str, object]:
        payload = self.model_dump(by_alias=True, exclude_none=True, mode="json")
        return cast(dict[str, object], _prune_empty_dicts(payload) or {})


class HabitListParams(HabitipyBaseModel):
    archived: bool | None = None
    area_id: str | None = Field(default=None, alias="areaId")
    habit_type: HabitType | None = Field(default=None, alias="type")
    time_of_day: str | None = Field(default=None, alias="timeOfDay")
    limit: int | None = Field(default=None, ge=1, le=100)
    offset: int | None = Field(default=None, ge=0)


class HabitJournalParams(HabitipyBaseModel):
    journal_date: date | None = Field(default=None, alias="date")


class HabitStatisticsParams(HabitipyBaseModel):
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
