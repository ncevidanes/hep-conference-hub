from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.domain import Subscriber
from app.schemas.domain import SubscriberCreate, SubscriberOut

router = APIRouter(prefix="/newsletter", tags=["newsletter"])


@router.post("/subscribe", response_model=SubscriberOut)
def subscribe(payload: SubscriberCreate, db: Session = Depends(get_db)):
    subscriber = db.scalar(select(Subscriber).where(Subscriber.email == payload.email))
    if not subscriber:
        subscriber = Subscriber(email=payload.email, areas=",".join(payload.areas), frequency=payload.frequency)
        db.add(subscriber)
    else:
        subscriber.active = True
        subscriber.areas = ",".join(payload.areas)
        subscriber.frequency = payload.frequency
    db.commit()
    db.refresh(subscriber)
    return SubscriberOut(id=subscriber.id, email=subscriber.email, confirmed=subscriber.confirmed, message="Assinatura registrada. Conecte um provedor de e-mail para double opt-in em produção.")
