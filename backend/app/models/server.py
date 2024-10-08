from sqlmodel import SQLModel


class ServerMessage(SQLModel):
    maimai_version: str
    server_motd: str
    author_motd: str
