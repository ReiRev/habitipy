from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

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
    type: str
    timer_type: str = Field(alias="timerType")
    timer_delay_secs: int = Field(alias="timerDelaySecs")


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


Occurrence = Annotated[
    DailyOccurrence | WeekDaysOccurrence | MonthDaysOccurrence | IntervalDaysOccurrence,
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


EndCondition = Annotated[
    DateEndCondition | StreakEndCondition | SuccessPeriodsEndCondition | TotalLogValueEndCondition,
    Field(discriminator="type"),
]


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


class HabitListParams(HabitModel):
    archived: bool | None = None
    area_id: str | None = Field(default=None, alias="areaId")
    habit_type: HabitType | None = Field(default=None, alias="type")
    time_of_day: str | None = Field(default=None, alias="timeOfDay")
    limit: int | None = Field(default=None, ge=1, le=100)
    offset: int | None = Field(default=None, ge=0)

    def to_query_params(self) -> dict[str, Any]:
        serialized: dict[str, Any] = {}
        for key, value in self.model_dump(by_alias=True, exclude_none=True).items():
            if isinstance(value, bool):
                serialized[key] = str(value).lower()
            elif isinstance(value, Enum):
                serialized[key] = value.value
            else:
                serialized[key] = value
        return serialized
