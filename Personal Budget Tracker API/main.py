from fastapi import FastAPI
from models import BudgetData

app = FastAPI()

@app.post("/calculate-budget")
def calculate_budget(data: BudgetData):
    total_expenses = sum([item.amount for item in data.expenses])
    balance = data.income - total_expenses

    category_spending = {}
    for item in data.expenses:
        if item.category in category_spending:
            category_spending[item.category] += item.amount
        else:
            category_spending[item.category] = item.amount

    return {
        "user": data.user,
        "total_income": data.income,
        "total_expenses": total_expenses,
        "balance": balance,
        "spending_by_category": category_spending
    }
