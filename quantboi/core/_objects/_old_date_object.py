from collections.abc import Iterable
from dataclasses import dataclass, field
import datetime as dt
import QuantLib as ql
from typing import Optional

class DateObjectWrapper(ql.Date):
    """
    DateObject class is a wrapper around QuantLib Date class. It provides a simple interface to work with dates.
    The class can be initialized with: day, month and year, date string and date format, datetime object or serial number.
    """
    def __init__(
        self, 
        day: int = None, month: int = None, year: int = None,
        date_string: str = None, date_format: str = None,
        datetime_object: dt.datetime = None,
        serial_number: int = None, 
        ) -> None:
        """
        Initialize the DateObject class with: (day, month and year), (date_string and date_format), 
        (datetime_object) or (serial_number).

        Args:
            day (int): Day of the date
            month (int): Month of the date
            year (int): Year of the date
            date_string (str): Date string
            date_format (str): Date format
            datetime_object (dt.datetime): Datetime object
            serial_number (int): Serial number of the date
        """
        if day and month and year:
            #self._init_day_month_year(day, month, year)
            super().__init__(day, month, year)
        elif date_string and date_format:
            self._init_date_string(date_string, date_format)
        if datetime_object:
            self._init_datetime_object(datetime_object)
        elif serial_number:
            self._init_serial_number(serial_number)
        else:
            pass

    def __getstate__(self) -> object:
        """
        Returns the state of the date object
        """
        state = self.serial_number()
        return state
    
    def __setstate__(self, state: object) -> None:
        """
        Set the state of the date object so that it can be pickled
        
        Args:
            state (object): State of the date object
        """
        self.__init__(serial_number=state)

# Did not hide methods, will do it later
#    def __dir__(self) -> None:
#        methods_to_hide = [
#            'todaysDate', 'minDate', 'maxDate', 'isLeap', 
#            'endOfMonth', 'isEndOfMonth', 'nextWeekday', 'nthWeekday',
#        ]
#        attributes = super().__dir__()
#        return [method for method in attributes if method not in methods_to_hide]

    def __repr__(self) -> str:
        try:
            super().__repr__()
        except:
            return f"No valid date object initialized"

    def _init_serial_number(self, serial_number: int) -> ql.Date:
        """
        Initialize the date object with a serial number

        Args:
            serial_number (int): Serial number of the date
        """
        ql.Date.__init__(self, serial_number)

    def _init_day_month_year(self, day: int, month: int, year: int) -> ql.Date:
        """
        Initialize the date object with day, month and year

        Args:
            day (int): Day of the date
            month (int): Month of the date
            year (int): Year of the date
        """
        ql.Date.__init__(self, day, month, year)
    
    def _init_date_string(self, date_string: str, date_format: str) -> ql.Date:
        """
        Initialize the date object with a date string

        Args:
            date_string (str): Date string
            date_format (str): Date format
        """
        ql.Date.__init__(self, date_string, date_format)

    def _init_datetime_object(self, datetime_object: dt.datetime) -> ql.Date:
        """
        Initialize the date object with a datetime object

        Args:
            datetime_object (dt.datetime): Datetime object
        """
        self._init_day_month_year(
            datetime_object.day, datetime_object.month, datetime_object.year)
    
    def __repr__(self) -> str:
        """
        Returns the string representation of the date object
        """
        try: 
            return super().__repr__()
        except:
            return f"No valid date object initialized"

    # /// Member functions ///
    def iso(self) -> str:
        """
        Returns the date in ISO format
        """        
        return self.ISO()
    
    def day_of_week(self) -> int:
        """
        Returns the weekday of the date as an integer:
            Sunday: 1
            Monday: 2
            Tuesday: 3
            Wednesday: 4
            Thursday: 5
            Friday: 6
            Saturday: 7
        """
        return super().weekday()
    
    def day_of_month(self) -> int:
        """
        Returns the day of the month as an integer
        """
        return super().dayOfMonth()
    
    def day_of_year(self) -> int:
        """
        Returns the day of the year as an integer
       """
        return super().dayOfYear()
    
    def month(self) -> int:
        """
        Returns the month as an integer
        """
        return super().month()
    
    def year(self) -> int:
        """
        Returns the year as an integer
        """
        return super().year()
    
    def serial_number(self) -> int:
        """
        Returns the serial number as an integer
        """
        return super().serialNumber()

    # /// Static functions ///
    @staticmethod
    def todays_date() -> ql.Date:
        """
        Returns today's date
        """
        return ql.Date.todaysDate()
    
    @staticmethod
    def min_date() -> ql.Date:
        """
        Returns the minimum date that can be represented
        """
        return ql.Date.minDate()
    
    @staticmethod
    def max_date() -> ql.Date:
        """
        Returns the maximum date that can be represented
        """
        return ql.Date.maxDate()
    
    @staticmethod
    def is_leap_year(year: int) -> bool:
        """
        Returns True if the year is a leap year, False otherwise

        Args:
            year (int): Year
        """
        return ql.Date.isLeap(year)

    @staticmethod
    def end_of_month(date: ql.Date) -> ql.Date:
        """
        Returns the end of the month date

        Args:
            date (ql.Date): Date
        """
        return ql.Date.endOfMonth(date)

    @staticmethod
    def is_end_of_month(date: ql.Date) -> bool:
        """
        Returns True if the date is the end of the month, False otherwise

        Args:
            date (ql.Date): Date
        """
        return ql.Date.isEndOfMonth(date)
    
    @staticmethod
    def next_weekday(date: ql.Date, weekday: int ) -> ql.Date:
        """
        WIP: there might be an error in weekday?
        
        Returns the next weekday date

        Args:
            date (ql.Date): Date
            weekday (int): Weekday
        """
        return ql.Date.nextWeekday(date, weekday)
    
    @staticmethod
    def nth_weekday(n: int, weekday: int, month: int, year: int) -> ql.Date:
        """
        Returns the nth weekday date

        Args:
            n (int): Nth
            weekday (int): Weekday
            month (int): Month
            year (int): Year
        """
        return ql.Date.nthWeekday(n, weekday, month, year)
    
@dataclass
class DateObject:
    day: Optional[int] = field(default=None)
    month: Optional[int] = field(default=None)
    year: Optional[int] = field(default=None)
    ql_date: Optional[ql.Date] = field(init=False)

    def __post_init__(self):
        if self.day is not None and self.month is not None and self.year is not None:
            self.ql_date = ql.Date(self.day, self.month, self.year)
        else:
            raise ValueError("day, month, and year must be provided to initialize TestDate")

    def to_datetime(self) -> dt.datetime:
        return self.ql_date.to_datetime()

    def add_days(self, days: int):
        self.ql_date.add_days(days)

    def subtract_days(self, days: int):
        self.ql_date.subtract_days(days)

    def __str__(self):
        return str(self.ql_date)