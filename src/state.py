from pydantic import BaseModel, Field
from typing import List, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

# 邮件紧急程度等级
class EmailUrgencyLevel:
    LOW = "low"          # 低紧急程度
    MEDIUM = "medium"    # 中等紧急程度
    HIGH = "high"        # 高紧急程度
    URGENT = "urgent"    # 紧急

class Email(BaseModel):
    id: str = Field(..., description="Unique identifier of the email")
    threadId: str = Field(..., description="Thread identifier of the email")
    messageId: str = Field(..., description="Message identifier of the email")
    references: str = Field(..., description="References of the email")
    sender: str = Field(..., description="Email address of the sender")
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Body content of the email")
    imap_id: bytes = Field(default=b'', description="IMAP ID for marking as read")
    urgency_level: str = Field(default=EmailUrgencyLevel.LOW, description="Urgency level of the email (low/medium/high/urgent)")
    urgency_keywords: list = Field(default_factory=list, description="Keywords that triggered the urgency level")
    
class GraphState(TypedDict):
    emails: List[Email]
    current_email: Email
    email_category: str
    generated_email: str
    rag_queries: List[str]
    retrieved_documents: str
    writer_messages: Annotated[list, add_messages]
    sendable: bool
    trials: int
    urgency_level: str