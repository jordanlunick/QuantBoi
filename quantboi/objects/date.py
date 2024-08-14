from dataclasses import dataclass, field
import datetime as dt
import QuantLib as ql
from typing import Optional

    
@dataclass
class Date:
    """
    A dataclass to represent a date object. \n
    The date object can be initialized with a day, month, and year, or a date string and date format. \n
    The date object can be converted to a datetime object, QuantLib date object, or a serial number.
    
    Attributes
    ----------
    year : int
        The year.
    month : int
        The month of the year.
    day : int
        The day of the month.
    date_string : str
        The date string.
    date_format : str
        The date format.
    serial_number : int
        The serial number.
    dt_date : datetime.datetime
        The datetime object.
    ql_date : QuantLib.Date
        The QuantLib date object.
    """
    # /// Date Attributes ///
    year: Optional[int] = field(default=None)
    month: Optional[int] = field(default=None)
    day: Optional[int] = field(default=None)
    date_string: Optional[str] = field(default=None)
    date_format: Optional[str] = field(default=None)
    serial_number: Optional[int] = field(default=None)

    # /// Date Objects ///
    date: Optional[str] = field(default=None)
    dt_date: Optional[dt.datetime] = field(default=None)
    ql_date: Optional[ql.Date] = field(default=None)

    def to_dt(self) -> dt.datetime:
        if self.dt_date is None:
            self.dt_date = dt.datetime(self.year, self.month, self.day)
        return self.dt_date
    
    def to_ql(self) -> ql.Date:
        if self.ql_date is None:
            if self.day and self.month and self.year:
                self.ql_date = ql.Date(self.day, self.month, self.year)
        return self.ql_date
    
    def to_serial(self) -> int:
        if self.serial_number is None:
            if self.dt_date is None:
                self.to_dt()
            self.serial_number = self.dt_date.toordinal()
        return self.serial_number

    def to_string(self) -> str:
        """
        Convert the date object to a string in the format 'YYMMDD'
        """
        if self.date_string is None:
            if self.day and self.month and self.year:
                self.date_string = f"{str(self.year)[-2:]}{self.month:02d}{self.day:02d}"
        return self.date_string