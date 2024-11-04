from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class Operation:
    """Class for operation unit in balance"""
    id: int = field(init=False)
    is_processed: bool = field(init=False)
    date: datetime = field(init=False)
    corr_account: str = field(init=False)
    debit_amount: Optional[int] = field(init=False)
    credit_amount: Optional[int] = field(init=False)

    def __init__(self, id: int, date: str, status: str, corr_account: str, dbt: str, cdt: str):
        self.id = id
        self.is_processed = status == 'Выполнена'
        self.date = datetime.strptime(date, "%d-%m-%Y")
        self.corr_account = str(corr_account)
        self.debit_amount = int(dbt) if dbt else None
        self.credit_amount = int(cdt) if cdt else None