from fastapi import FastAPI, status, HTTPException, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

class TransactionCreate(BaseModel):
    details: str

class Transaction(BaseModel):
    id: int
    details: str

transactions_db: list[Transaction] = [Transaction(id=0, details="10 100")]

# Маршруты API
@app.get("/transactions", response_model=list[Transaction])
async def read_transactions() -> list[Transaction]:
    return transactions_db

@app.get("/transactions/{transaction_id}", response_model=Transaction)
async def read_transaction(transaction_id: int) -> Transaction:
    for transaction in transactions_db:
        if transaction.id == transaction_id:
            return transaction
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

@app.post("/transactions", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction_create: TransactionCreate) -> Transaction:
    next_id = max((tr.id for tr in transactions_db), default=-1) + 1
    new_transaction = Transaction(id=next_id, details=transaction_create.details)
    transactions_db.append(new_transaction)
    return new_transaction

@app.put("/transactions/{transaction_id}", response_model=Transaction, status_code=status.HTTP_200_OK)
async def update_transaction(transaction_id: int, transaction_create: TransactionCreate) -> Transaction:
    for i, tr in enumerate(transactions_db):
        if tr.id == transaction_id:
            update_transaction = Transaction(id=transaction_id, details=transaction_create.details)
            transactions_db[i] = update_transaction
            return update_transaction
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

@app.delete("/transactions", status_code=status.HTTP_200_OK)
async def delete_transactions() -> dict:
    transactions_db.clear()
    return {"detail": "All transactions deleted!"}

@app.delete("/transactions/{transaction_id}", status_code=status.HTTP_200_OK)
async def delete_transaction(transaction_id: int) -> dict:
    for i , tr in enumerate(transactions_db):
        if tr.id == transaction_id:
            transactions_db.pop(i)
            return {"detail": f"Transaction ID={transaction_id} deleted!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

# Маршруты фронта
@app.get("/web/transactions", response_class=HTMLResponse)
async def get_transactions_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "transactions": transactions_db })

## Страница совершения перевода
@app.get("/web/transactions/create", response_class=HTMLResponse)
async def get_create_transaction_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})

## Обработка формы совершения перевода
@app.post("/web/transactions", response_class=HTMLResponse)
async def create_transaction_form(request: Request, details: str = Form(...)):
    next_id = max((trn.id for trn in transactions_db), default=-1) + 1
    new_transaction = Transaction(id=next_id, details=details)
    transactions_db.append(new_transaction)
    return templates.TemplateResponse("index.html", {"request": request, "transactions": transactions_db})

## Страница детализации платежа
@app.get("/web/transactions/{transaction_id}", response_class=HTMLResponse)
async def get_transaction_detail_page(request: Request, transaction_id: int):
    for transaction in transactions_db:
        if transaction.id == transaction_id:
            return templates.TemplateResponse("detail.html", {"request": request, "transaction": transaction})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Платёж не найден")
