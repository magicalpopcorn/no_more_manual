from typing import List, Optional

import yaml
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from src.server.db import accounts_collection, characters_collection
from src.server.models import Account

router = APIRouter(prefix="/api/v1/accounts", tags=["Accounts"])


# ------------------ CRUD ------------------


@router.get("", response_model=List[Account])
async def list_accounts(
    kingdom: Optional[int] = Query(None, description="Filter by kingdom"),
    min_power: Optional[int] = Query(None, description="Filter by minimum power"),
):
    """
    Retrieve all accounts with optional filters.
    """
    query = {}
    if kingdom:
        query["kingdom"] = kingdom
    if min_power:
        query["power"] = {"$gte": min_power}

    accounts = await accounts_collection.find(query).to_list(length=None)
    return accounts


@router.get("/{account_id}", response_model=Account)
async def get_account(account_id: str):
    """
    Retrieve a single account by ID.
    """
    account = await accounts_collection.find_one({"_id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.post("", status_code=201)
async def create_account(account_id: str, account: Account):
    """
    Create a new account.
    """
    existing = await accounts_collection.find_one({"_id": account_id})
    if existing:
        raise HTTPException(status_code=400, detail="Account already exists")
    await accounts_collection.insert_one({"_id": account_id, **account.model_dump()})
    return JSONResponse(content={"message": f"Created {account.id}"}, status_code=201)


@router.put("/{account_id}")
async def replace_account(account_id: str, account: Account):
    """
    Replace an entire account document.
    """
    result = await accounts_collection.replace_one(
        {"_id": account_id}, {"_id": account_id, **account.model_dump()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": f"Replaced {account_id}"}


@router.delete("/{account_id}")
async def delete_account(account_id: str):
    """
    Delete an account.
    """
    result = await accounts_collection.delete_one({"_id": account_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": f"Deleted {account_id}"}


@router.get("/{account_id}/characters")
async def get_account_characters(account_id: str):
    """
    Retrieve all characters that belong to a specific account.
    """
    account = await accounts_collection.find_one({"_id": account_id})
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    character_ids = account.get("characters", [])
    if not character_ids:
        return {"message": f"Account {account_id} has no characters"}

    characters = await characters_collection.find({"_id": {"$in": character_ids}}).to_list(
        length=None
    )

    return {"account_id": account_id, "account_name": account["name"], "characters": characters}
