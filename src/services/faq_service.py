from sqlalchemy.orm import Session, joinedload
from ..database.models import FAQ, FAQCategory
from ..utils import Helpers
from typing import List, Optional

class FAQService:
    """Service for managing FAQs"""
    
    @staticmethod
    def get_all_active_faqs(db: Session) -> List[FAQ]:
        """Get all active FAQs ordered by category and order_index"""
        return db.query(FAQ).options(joinedload(FAQ.faq_category)).filter(
            FAQ.is_active == True
        ).join(FAQCategory).order_by(
            FAQCategory.order_index,
            FAQ.order_index,
            FAQ.created_at
        ).all()
    
    @staticmethod
    def get_faqs_by_category(db: Session, category_id: int) -> List[FAQ]:
        """Get active FAQs by category ID"""
        return db.query(FAQ).options(joinedload(FAQ.faq_category)).filter(
            FAQ.is_active == True,
            FAQ.category_id == category_id
        ).order_by(FAQ.order_index, FAQ.created_at).all()
    
    @staticmethod
    def get_faqs_by_category_slug(db: Session, category_slug: str) -> List[FAQ]:
        """Get active FAQs by category slug"""
        return db.query(FAQ).options(joinedload(FAQ.faq_category)).join(FAQCategory).filter(
            FAQ.is_active == True,
            FAQCategory.slug == category_slug
        ).order_by(FAQ.order_index, FAQ.created_at).all()
    
    @staticmethod
    def get_all_categories(db: Session) -> List[str]:
        """Get list of all unique FAQ category slugs that have active FAQs"""
        categories = db.query(FAQCategory).join(FAQ).filter(
            FAQ.is_active == True
        ).distinct().all()
        return [cat.slug for cat in categories]
    
    @staticmethod
    def get_faq_by_id(db: Session, faq_id: int) -> Optional[FAQ]:
        """Get FAQ by ID with category"""
        return db.query(FAQ).options(joinedload(FAQ.faq_category)).filter(FAQ.id == faq_id).first()
    
    @staticmethod
    def create_faq(db: Session, question: str, answer: str, category_id: int, 
                   is_active: bool = True, order_index: int = 0) -> FAQ:
        """Create new FAQ"""
        # Verify category exists
        category = db.query(FAQCategory).filter(FAQCategory.id == category_id).first()
        if not category:
            raise ValueError(f"Category with ID {category_id} does not exist")
        
        faq = FAQ(
            question=question,
            answer=answer,
            category_id=category_id,
            is_active=is_active,
            order_index=order_index
        )
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq
    
    @staticmethod
    def update_faq(db: Session, faq_id: int, question: str = None, answer: str = None,
                   category_id: int = None, is_active: bool = None, order_index: int = None) -> Optional[FAQ]:
        """Update existing FAQ"""
        faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
        if not faq:
            return None
        
        # Verify category exists if updating
        if category_id is not None:
            category = db.query(FAQCategory).filter(FAQCategory.id == category_id).first()
            if not category:
                raise ValueError(f"Category with ID {category_id} does not exist")
        
        if question is not None:
            faq.question = question
        if answer is not None:
            faq.answer = answer
        if category_id is not None:
            faq.category_id = category_id
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
        return db.query(FAQ).options(joinedload(FAQ.faq_category)).filter(
            FAQ.is_active == True,
            (FAQ.question.ilike(search_term) | FAQ.answer.ilike(search_term))
        ).order_by(FAQ.order_index, FAQ.created_at).all()
    
    # Category Management Methods
    @staticmethod
    def get_all_faq_categories(db: Session) -> List['FAQCategory']:
        """Get all FAQ categories"""
        return db.query(FAQCategory).order_by(FAQCategory.order_index, FAQCategory.name).all()
    
    @staticmethod
    def get_active_faq_categories(db: Session) -> List['FAQCategory']:
        """Get all active FAQ categories"""
        return db.query(FAQCategory).filter(
            FAQCategory.is_active == True
        ).order_by(FAQCategory.order_index, FAQCategory.name).all()
    
    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> Optional['FAQCategory']:
        """Get FAQ category by ID"""
        return db.query(FAQCategory).filter(FAQCategory.id == category_id).first()
    
    @staticmethod
    def get_category_by_slug(db: Session, slug: str) -> Optional['FAQCategory']:
        """Get FAQ category by slug"""
        return db.query(FAQCategory).filter(FAQCategory.slug == slug).first()
    
    @staticmethod
    def create_category(db: Session, name: str, slug: str, description: str = None, 
                       icon: str = None, is_active: bool = True, order_index: int = 0) -> 'FAQCategory':
        """Create new FAQ category"""
        # Check if slug already exists
        existing = db.query(FAQCategory).filter(FAQCategory.slug == slug).first()
        if existing:
            raise ValueError(f"Category with slug '{slug}' already exists")
        
        category = FAQCategory(
            name=name,
            slug=slug,
            description=description,
            icon=icon,
            is_active=is_active,
            order_index=order_index
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def update_category(db: Session, category_id: int, name: str = None, slug: str = None,
                       description: str = None, icon: str = None, is_active: bool = None, 
                       order_index: int = None) -> Optional['FAQCategory']:
        """Update FAQ category"""
        category = db.query(FAQCategory).filter(FAQCategory.id == category_id).first()
        if not category:
            return None
        
        # Check if new slug conflicts with existing
        if slug and slug != category.slug:
            existing = db.query(FAQCategory).filter(FAQCategory.slug == slug).first()
            if existing:
                raise ValueError(f"Category with slug '{slug}' already exists")
        
        if name is not None:
            category.name = name
        if slug is not None:
            category.slug = slug
        if description is not None:
            category.description = description
        if icon is not None:
            category.icon = icon
        if is_active is not None:
            category.is_active = is_active
        if order_index is not None:
            category.order_index = order_index
        
        db.commit()
        db.refresh(category)
        return category
    
    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """Delete FAQ category"""
        category = db.query(FAQCategory).filter(FAQCategory.id == category_id).first()
        if not category:
            return False
        
        # Check if category has FAQs
        faq_count = db.query(FAQ).filter(FAQ.category_id == category_id).count()
        if faq_count > 0:
            raise ValueError(f"Cannot delete category. {faq_count} FAQ(s) are using this category.")
        
        db.delete(category)
        db.commit()
        return True
    
    @staticmethod
    def get_category_faq_count(db: Session, category_id: int) -> int:
        """Get count of FAQs in a category"""
        return db.query(FAQ).filter(
            FAQ.category_id == category_id,
            FAQ.is_active == True
        ).count()

    def get_all_faqs(self, db: Session, page: int = 1, per_page: int = 20):
        """Get all FAQs with pagination"""
        faqs = db.query(FAQ).order_by(FAQ.order_index, FAQ.id).all()
        
        # Apply pagination
        paginated_faqs = Helpers.paginate(faqs, page, per_page)
        
        return {
            'success': True,
            'faqs': paginated_faqs,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(faqs),
                'total_pages': (len(faqs) + per_page - 1) // per_page
            }
        }
    
    def get_faqs_by_category(self, db: Session, category_id: int, page: int = 1, per_page: int = 20):
        """Get FAQs by category with pagination"""
        faqs = db.query(FAQ).filter(
            FAQ.category_id == category_id,
            FAQ.is_active == True
        ).order_by(FAQ.order_index, FAQ.id).all()
        
        # Apply pagination
        paginated_faqs = Helpers.paginate(faqs, page, per_page)
        
        return {
            'success': True,
            'faqs': [{
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category_id': faq.category_id,
                'is_active': faq.is_active,
                'order_index': faq.order_index,
                'created_at': Helpers.format_timestamp(faq.created_at) if faq.created_at else None
            } for faq in paginated_faqs],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(faqs),
                'total_pages': (len(faqs) + per_page - 1) // per_page
            }
        }
    
    def search_faqs(self, db: Session, search_term: str, page: int = 1, per_page: int = 20):
        """Search FAQs with pagination"""
        search_term = Helpers.sanitize_input(search_term.lower())
        
        faqs = db.query(FAQ).filter(
            FAQ.is_active == True
        ).all()
        
        # Filter by search term
        filtered_faqs = [
            faq for faq in faqs
            if search_term in faq.question.lower() or search_term in faq.answer.lower()
        ]
        
        # Apply pagination
        paginated_faqs = Helpers.paginate(filtered_faqs, page, per_page)
        
        return {
            'success': True,
            'faqs': [{
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category_id': faq.category_id,
                'category_name': faq.category.name if faq.category else None
            } for faq in paginated_faqs],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(filtered_faqs),
                'total_pages': (len(filtered_faqs) + per_page - 1) // per_page
            }
        }