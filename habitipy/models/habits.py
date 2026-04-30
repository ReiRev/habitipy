from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import Annotated, Literal, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..pagination import Pagination


class HabitModel(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


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


class ReminderTime(HabitModel):
    hour: int
    minute: int


class ReminderOccurrenceFilter(HabitModel):
    week_days: list[int] | None = Field(default=None, alias="weekDays")


class TimeTrigger(HabitModel):
    time: ReminderTime
    occurrence_filter: ReminderOccurrenceFilter | None = Field(
        default=None, alias="occurrenceFilter"
    )
    show_live_activity: bool | None = Field(default=None, alias="showLiveActivity")
    show_as_alarm: bool | None = Field(default=None, alias="showAsAlarm")


class HabitStack(HabitModel):
    id: str | None = None
    condition_habit_id: str = Field(alias="conditionHabitId")
    type: HabitStackTriggerType
    timer_type: HabitStackTimerType = Field(alias="timerType")
    timer_delay_secs: int | None = Field(default=None, alias="timerDelaySecs")


class HabitCreateReminderTime(HabitModel):
    hour: int
    minute: int


class HabitCreateReminderOccurrenceFilter(HabitModel):
    week_days: list[int] | None = Field(default=None, alias="weekDays")


class HabitCreateTimeTrigger(HabitModel):
    time: HabitCreateReminderTime
    occurrence_filter: HabitCreateReminderOccurrenceFilter | None = Field(
        default=None, alias="occurrenceFilter"
    )
    show_live_activity: bool | None = Field(default=None, alias="showLiveActivity")
    show_as_alarm: bool | None = Field(default=None, alias="showAsAlarm")


class HabitCreateHabitStack(HabitModel):
    condition_habit_id: str = Field(alias="conditionHabitId")
    type: HabitStackTriggerType
    timer_type: HabitStackTimerType = Field(alias="timerType")
    timer_delay_secs: int | None = Field(default=None, alias="timerDelaySecs")


class HabitCreateReminders(HabitModel):
    time_triggers: list[HabitCreateTimeTrigger] = Field(default_factory=list, alias="timeTriggers")
    habit_stacks: list[HabitCreateHabitStack] = Field(default_factory=list, alias="habitStacks")


class Reminders(HabitModel):
    time_triggers: list[TimeTrigger] = Field(default_factory=list, alias="timeTriggers")
    habit_stacks: list[HabitStack] = Field(default_factory=list, alias="habitStacks")


class DailyOccurrence(HabitModel):
    type: Literal["daily"]


class WeekDaysOccurrence(HabitModel):
    type: Literal["weekDays"]
    days: list[int]


class MonthDaysOccurrence(HabitModel):
    type: Literal["monthDays"]
    days: list[int]


class IntervalDaysOccurrence(HabitModel):
    type: Literal["intervalDays"]
    interval: int


class HabitCreateDailyOccurrence(HabitModel):
    type: Literal["daily"]


class HabitCreateWeekDaysOccurrence(HabitModel):
    type: Literal["weekDays"]
    days: list[int]


class HabitCreateMonthDaysOccurrence(HabitModel):
    type: Literal["monthDays"]
    days: list[int]


class HabitCreateIntervalDaysOccurrence(HabitModel):
    type: Literal["intervalDays"]
    interval: int


Occurrence = Annotated[
    DailyOccurrence | WeekDaysOccurrence | MonthDaysOccurrence | IntervalDaysOccurrence,
    Field(discriminator="type"),
]


HabitCreateOccurrence = Annotated[
    HabitCreateDailyOccurrence
    | HabitCreateWeekDaysOccurrence
    | HabitCreateMonthDaysOccurrence
    | HabitCreateIntervalDaysOccurrence,
    Field(discriminator="type"),
]


class DateEndCondition(HabitModel):
    id: str
    type: Literal["date"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    date: date


class StreakEndCondition(HabitModel):
    id: str
    type: Literal["streak"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    period_type: GoalPeriodicity = Field(alias="periodType")
    streak_length: int = Field(alias="streakLength")


class SuccessPeriodsEndCondition(HabitModel):
    id: str
    type: Literal["successPeriods"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    period_type: GoalPeriodicity = Field(alias="periodType")
    total_periods: int = Field(alias="totalPeriods")


class TotalLogValueEndCondition(HabitModel):
    id: str
    type: Literal["totalLogValue"]
    created_at: datetime = Field(alias="createdAt")
    is_met: bool = Field(alias="isMet")
    total_log_value: float = Field(alias="totalLogValue")


class HabitCreateDateEndCondition(HabitModel):
    type: Literal["date"]
    date: date


class HabitCreateStreakEndCondition(HabitModel):
    type: Literal["streak"]
    streak_length: int = Field(alias="streakLength")


class HabitCreateSuccessPeriodsEndCondition(HabitModel):
    type: Literal["successPeriods"]
    total_periods: int = Field(alias="totalPeriods")


class HabitCreateTotalLogValueEndCondition(HabitModel):
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


class HabitCreateGoal(HabitModel):
    periodicity: GoalPeriodicity
    value: float
    unit: UnitSymbol


class Goal(HabitModel):
    id: str
    created_at: datetime = Field(alias="createdAt")
    periodicity: GoalPeriodicity
    value: float
    unit: UnitSymbol
    is_active: bool | None = Field(default=None, alias="isActive")


class Area(HabitModel):
    id: str
    name: str
    color_hex: str | None = Field(default=None, alias="colorHex")
    icon: str | None = None
    created_at: datetime = Field(alias="createdAt")
    description: str | None = None


class TimeOfDay(HabitModel):
    id: str
    name: str
    icon: str | None = None
    start_time: time = Field(alias="startTime")
    end_time: time = Field(alias="endTime")
    color_hex: str | None = Field(default=None, alias="colorHex")


class Habit(HabitModel):
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


class HabitListPage(HabitModel):
    data: list[Habit]
    pagination: Pagination


class HabitJournalStatus(str, Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"
    IN_PROGRESS = "inprogress"


class HabitJournalStreakUnit(str, Enum):
    DAY = "day"


class HabitJournalCurrentStreak(HabitModel):
    length: int
    unit: HabitJournalStreakUnit


class HabitJournalProgress(HabitModel):
    current: float
    target: float
    unit: str
    periodicity: GoalPeriodicity


class HabitJournalLogInfo(HabitModel):
    type: LogMethod


class HabitJournalEntry(HabitModel):
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


class HabitJournalPage(HabitModel):
    data: list[HabitJournalEntry]


class HabitStatisticsUnit(HabitModel):
    id: str
    name: str
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


class HabitStatisticsDailyProgress(HabitModel):
    date: date
    total_log: float = Field(alias="totalLog")
    status: HabitJournalStatus


class HabitStatistics(HabitModel):
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


class HabitStatisticsResponse(HabitModel):
    data: HabitStatistics


class HabitCreateRequest(HabitModel):
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

    def to_request_body(self) -> dict[str, object]:
        return cast(
            dict[str, object],
            self.model_dump(by_alias=True, exclude_none=True, mode="json"),
        )


class HabitListParams(HabitModel):
    archived: bool | None = None
    area_id: str | None = Field(default=None, alias="areaId")
    habit_type: HabitType | None = Field(default=None, alias="type")
    time_of_day: str | None = Field(default=None, alias="timeOfDay")
    limit: int | None = Field(default=None, ge=1, le=100)
    offset: int | None = Field(default=None, ge=0)

    def to_query_params(self) -> dict[str, str]:
        serialized: dict[str, str] = {}
        for key, value in self.model_dump(by_alias=True, exclude_none=True).items():
            if isinstance(value, bool):
                serialized[key] = str(value).lower()
            elif isinstance(value, Enum):
                serialized[key] = value.value
            else:
                serialized[key] = str(value)
        return serialized


class HabitJournalParams(HabitModel):
    journal_date: date | None = Field(default=None, alias="date")

    def to_query_params(self) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in self.model_dump(
                by_alias=True,
                exclude_none=True,
                mode="json",
            ).items()
        }


class HabitStatisticsParams(HabitModel):
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")

    def to_query_params(self) -> dict[str, str]:
        return {
            key: str(value)
            for key, value in self.model_dump(
                by_alias=True,
                exclude_none=True,
                mode="json",
            ).items()
        }
