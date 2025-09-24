# importa todos tus modelos aquí para que se registren en Base.metadata
from app.models.users import Users
from app.models.clients import Clients
from app.models.chats import Chats
from app.models.chatDetails import ChatDetails
from app.models.documents import Documents
from app.models.tableXClients import TableXClients

__all__ = ["Users", "Clients", "Chats", "ChatDetails", "Documents", "TableXClients"]