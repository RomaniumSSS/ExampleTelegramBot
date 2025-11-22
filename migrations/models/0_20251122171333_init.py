from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" CHAR(36) NOT NULL PRIMARY KEY,
    "telegram_id" BIGINT NOT NULL UNIQUE,
    "username" VARCHAR(255),
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_users_telegra_ab91e9" ON "users" ("telegram_id");
CREATE TABLE IF NOT EXISTS "mood_logs" (
    "id" CHAR(36) NOT NULL PRIMARY KEY,
    "value" INT NOT NULL,
    "note" TEXT,
    "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" CHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmG1P2zAQx79KlVdMYqikhXbTNCl9ADpoO0G6IRCK3NhNIxy7JM6gQv3us908NU8Uxk"
    "OZeAPN3Tm5+8W5+yf3ikMhwt5On1J4Qi3la+VeIcBB/EfatV1RwGwWO4SBgTEOYik0MLWk"
    "FYw95gKTcccEYA9xE0Se6dozZlPCrcTHWBipyQNtYsUmn9g3PjIYtRCbIpc7Lq+42SYQ3S"
    "EvPJxdGxMbYbiSrg3FtaXdYPOZtI1Gvc6BjBSXGxsmxb5D4ujZnE0picJ934Y7Yo3wWYgg"
    "FzAEE2WILIOSQ9MyY25gro+iVGFsgGgCfCxgKN8mPjEFg4q8kvhT/648Ao9JiUBrEyZY3C"
    "+WVcU1S6siLtU+0k63avufZJXUY5YrnZKIspALAQPLpZJrDPIPwLygDMseYfkoo/gUTZ7l"
    "UziGhhhkvIlCkiGhp2HjKfF/n9XdeqPerO3XmzxE5hJZGiVkewNdAoyBEcpyeOnorgBYGJ"
    "/ixVNcg1ewq14RVwkLvXuui5wdz7vBwjD4pZ3KrdfXzuXec+aB52Q4OAzDKe8Oy74xaJ8M"
    "WymcpotE+QZgWagd7mG2g/LBrq5M4YXB0p3wx4ZuTl4DHBI8D+51Gf1ev3uma/2fK7ego+"
    "ld4VFX8IfWrWVLiO9AdJLK755+VBGHlYvhoJtuHFGcfqGInIDPqEHorQFgotmF1hDMyo31"
    "PeQaj2vTiSXP2avf9KF5oDWLATe5zu3MgkaW3gF1kW2RYzSXDHs8D0DMvA4TTPRRcJqNpR"
    "Zb453lgtto6Ce3BS+PF4WYLLCtnbW1TleREMfAvL4FLjRWaAoPVWnKEsVmXY7qpC2AAEvW"
    "L6oQOSfB5kioEHixfhIFfWin96+dGN+Klguc3DbXsq1CEZVa+DxS6mGszyKkvqhqrdZQq7"
    "X95l690dhrViNFlXWVSatW71Coq5X5lJVb4lmRvzOA21PgFs+RcM07kV28zdwZGBGLTfmh"
    "urdXAi5UXTwqNd5DQaYufR9K679VWhndUDwDkwMq8d6e6lbB0oPjU4SBhFuoKBLfCDbvPh"
    "eJisVLSgENubY5zRMDgadUDoA4ZmP0QOHoWndiBRt3AwbWP775l3w64SoueFDWnUyJJU8a"
    "TG/ROF9+MolH4xEQg/D3CXC3Wl0DII8qBCh9qdFOCUMkZ67/OBsOCmZ6vCQFckR4gZfQNt"
    "l2Bdseu9pMrCUURdXlH6rS36RSQ1mcoJX3dv6ab5qLv0UWlpQ="
)
