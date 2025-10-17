from sqlalchemy.orm import Session
from ..database.models import FAQ
from typing import List, Optional

class FAQService:
    """Service for managing FAQs"""
    
    @staticmethod
    def get_all_active_faqs(db: Session) -> List[FAQ]:
        """Get all active FAQs ordered by category and order_index"""
        return db.query(FAQ).filter(
            FAQ.is_active == True
        ).order_by(
            FAQ.category,
            FAQ.order_index,
            FAQ.created_at
        ).all()
    
    @staticmethod
    def get_faqs_by_category(db: Session, category: str) -> List[FAQ]:
        """Get active FAQs by category"""
        return db.query(FAQ).filter(
            FAQ.is_active == True,
            FAQ.category == category
        ).order_by(FAQ.order_index, FAQ.created_at).all()
    
    @staticmethod
    def get_all_categories(db: Session) -> List[str]:
        """Get list of all unique FAQ categories"""
        categories = db.query(FAQ.category).filter(
            FAQ.is_active == True
        ).distinct().all()
        return [cat[0] for cat in categories]
    
    @staticmethod
    def get_faq_by_id(db: Session, faq_id: int) -> Optional[FAQ]:
        """Get FAQ by ID"""
        return db.query(FAQ).filter(FAQ.id == faq_id).first()
    
    @staticmethod
    def create_faq(db: Session, question: str, answer: str, category: str = "general", 
                   is_active: bool = True, order_index: int = 0) -> FAQ:
        """Create new FAQ"""
        faq = FAQ(
            question=question,
            answer=answer,
            category=category,
            is_active=is_active,
            order_index=order_index
        )
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq
    
    @staticmethod
    def update_faq(db: Session, faq_id: int, question: str = None, answer: str = None,
                   category: str = None, is_active: bool = None, order_index: int = None) -> Optional[FAQ]:
        """Update existing FAQ"""
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return None
        
        if question is not None:
            faq.question = question
        if answer is not None:
            faq.answer = answer
        if category is not None:
            faq.category = category
        if is_active is not None:
            faq.is_active = is_active
        if order_index is not None:
            faq.order_index = order_index
        
        db.commit()
        db.refresh(faq)
        return faq
    
    @staticmethod
    def delete_faq(db: Session, faq_id: int) -> bool:
        """Delete FAQ"""
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return False
        
        db.delete(faq)
        db.commit()
        return True
    
    @staticmethod
    def search_faqs(db: Session, query: str) -> List[FAQ]:
        """Search FAQs by question or answer"""
        search_term = f"%{query.lower()}%"
        return db.query(FAQ).filter(
            FAQ.is_active == True,
            (FAQ.question.ilike(search_term) | FAQ.answer.ilike(search_term))
        ).order_by(FAQ.order_index, FAQ.created_at).all()