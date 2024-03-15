
from typing import Union
import asyncpg
import aiopg
from config import args as parser_args
from config import loop
from loguru import logger


async def connect_db(user: str, password: str, host: str, dbname: str):
    try:
        pool = await aiopg.create_pool(f"dbname={dbname} user={user} password={password} host={host}")
        logger.debug(f"{user} connected to db")

        conn = await pool.acquire()
        return conn

    except Exception as error:
        logger.error(f"{user} CAN'T CONNECT TO BASE: {error}")

async def disconnect_db(connection):
    if connection:
        await connection.close()
        logger.debug("DB is disconnected...")

async def get_request(request: str, args: tuple, *, output=True) -> Union[tuple, None]:
    connection = await connect_db(parser_args.user,
                                  parser_args.password,
                                  parser_args.host,
                                  parser_args.dbname)

    try:
        cursor = await connection.cursor()
        logger.debug(f"Running request: {request}")
        await cursor.execute(request, args)

        if output:
            return (await cursor.fetchall())

    except Exception as error:
        logger.error(error)

    finally:
        await disconnect_db(connection)

pool = loop.run_until_complete(
    asyncpg.create_pool(user=parser_args.user, password=parser_args.password,
                        database=parser_args.dbname, host=parser_args.host,
                        min_size=0, max_size=900, loop=loop))
