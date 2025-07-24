from pydantic import BaseModel
from typing import List

class Expense(BaseModel):
    category: str
    amount: float

class BudgetData(BaseModel):
    user: str
    income: float
    expenses: List[Expense]
