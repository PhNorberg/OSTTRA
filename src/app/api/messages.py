from datetime import datetime, date
from fastapi import APIRouter, Body, Request, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

import logging 

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


router = APIRouter( 
    prefix="/api",
    tags=["messages"]
)


class SubmitMessage(BaseModel):
    to_user: str 
    message: str  = Field(..., min_length=1, description="Message cannot be empty")


class DeleteMessagesRequest(BaseModel):
    ids: List[int] = Field(..., min_length=1, description="List cannot be empty")


class ResponseMessage(BaseModel):
    id: int
    to_user: str 
    message: str
    date_sent: datetime


class ResponseMessageStatus(BaseModel):
    message: str
    

@router.get("/messages", response_model=List[ResponseMessage])
async def api_get_messages(request : Request, start : int = Query(...), stop : int = Query(...)):
    pool = request.app.state.pool
    response = await db_get_messages(pool, start, stop)
    return response 


@router.post("/messages", response_model=ResponseMessageStatus)
async def api_submit_message(message: SubmitMessage, request : Request):
    pool = request.app.state.pool
    response = await db_submit_message(message.to_user, message.message, pool)
    return response 


@router.delete("/messages", response_model=ResponseMessageStatus)
async def api_delete_messages(request : Request, delete_request : DeleteMessagesRequest):
    pool = request.app.state.pool
    response = await db_delete_messages(delete_request.ids, pool)
    return response 
    

@router.get("/messages/new", response_model=List[ResponseMessage])
async def api_get_new_messages(request : Request):
    pool = request.app.state.pool
    response = await db_get_new_messages(pool)
    return response 


async def db_get_messages(pool, start, stop):
    query = """
    SELECT * FROM messages
    WHERE id BETWEEN $1 and $2
    ORDER BY date_sent
    """

    async with pool.acquire() as connection:
        try:
            messages = await connection.fetch(query, start, stop)

            if messages:
                return [ResponseMessage(**message) for message in messages]
            
            return []
        
        except Exception as e:
            log.error(f"Database failure while fetching messages: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failure when fetching messages."
            )


async def db_submit_message(to_user, message, pool):
    query = """
    INSERT INTO messages (to_user, message)
    VALUES ($1, $2)
    """

    async with pool.acquire() as connection:
        try:
            await connection.execute(query, to_user, message)
           
            return {"message": "Message successfully sent"}
        
        except Exception as e:
            log.error(f"Database failure while submitting message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit the message."
            )
        

async def db_delete_messages(ids : List[int], pool):
    query_find_ids = """
    SELECT id
    FROM messages 
    WHERE id = ANY($1::int[])
    """

    query_delete = """
    DELETE FROM messages
    WHERE id = ANY($1::int[])
    """

    async with pool.acquire() as connection:
        try:

            query_ids = await connection.fetch(query_find_ids, ids)
            found_ids = [record['id'] for record in query_ids]

            diff_ids = list(set(ids) - set(found_ids))
            same_ids = list(set(ids) & set(found_ids))

            if not same_ids:
                log.info(f"No messages found with IDs {ids}")
                return {"message" : f"No messages found with IDs {ids}"}

            await connection.execute(query_delete, ids)

            if diff_ids:
                log.info(f"Deleted messages with IDs {same_ids} successfully. IDs {diff_ids} doesnt exist")
                return {"message": f"Successfully deleted messages with IDs {same_ids}. IDs {diff_ids} doesnt exist"}
            
            log.info(f"Deleted messages with IDs {same_ids} successfully.")
            return {"message": f"Successfully deleted messages with IDs {same_ids}."}

        except Exception as e:
            log.error(f"Database failure while deleting messages: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete messages."
            )


async def db_get_new_messages(pool):
    query_fetch = """
    SELECT * FROM messages
    WHERE read = false
    """

    query_update = """
    UPDATE messages
    SET read = true
    WHERE read = false
    """

    async with pool.acquire() as connection:
        try:
            
            new_messages = await connection.fetch(query_fetch)
           
            if new_messages:
                log.info(f"New messages found. Updating their read status")

                try:
                    await connection.execute(query_update)
                    log.info(f"Read status updated succesfully")
                
                except Exception as e:
                    log.error(f"Database failure while updating Read status: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to fetch new messages."
                    )

            else:
                log.info("No new messages found")
            
            return [ResponseMessage(**message) for message in new_messages]
        
        except HTTPException as e:
            raise e 
            
        except Exception as e:
            log.error(f"Database failure while getting new messages: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch new messages."
            )
