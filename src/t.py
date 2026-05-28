from telegram import Document, Message, PhotoSize, Update, User


class HumanMessage(Message):
    from_user: User


class MessageUpdate(Update):
    message: Message


class TextMessage(HumanMessage):
    text: str


class TextMessageUpdate(MessageUpdate):
    message: TextMessage


class PhotoMessage(HumanMessage):
    photo: tuple[PhotoSize]
    text: str | None


class FileMessageUpdate(MessageUpdate):
    message: PhotoMessage


class DocumentMessage(HumanMessage):
    document: Document
    caption: str | None


class DocumentMessageUpdate(MessageUpdate):
    message: DocumentMessage
