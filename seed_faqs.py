from src.database.connection import SessionLocal
from src.services.faq_service import FAQService

def seed_faqs():
    """Seed initial FAQ data"""
    db = SessionLocal()
    faq_service = FAQService()
    
    try:
        # Check if FAQs already exist
        existing = faq_service.get_all_active_faqs(db)
        if existing:
            print("FAQs already exist. Skipping seed.")
            return
        
        faqs_data = [
            {
                "question": "How do I start a chat?",
                "answer": "To start a chat session:\n1. Click on '💬 Start Chat' button from the main menu\n2. You will be connected to an available agent\n3. Start typing your message to begin the conversation",
                "category": "getting_started",
                "order_index": 1
            },
            {
                "question": "How do I contact support?",
                "answer": "To contact our support team:\n1. Use the chat feature by clicking '💬 Start Chat'\n2. An agent will assist you with your inquiry\n3. You can also send us a direct message anytime\n4. For urgent matters, mention 'URGENT' in your message",
                "category": "general",
                "order_index": 2
            },
            {
                "question": "What are your operating hours?",
                "answer": "Our support is available:\n🕐 24/7 - Round the clock support\n📅 7 days a week - Including weekends\n🚀 Instant response - Average response time: 2-5 minutes\n🌍 Global coverage - Support in multiple time zones",
                "category": "general",
                "order_index": 3
            },
            {
                "question": "How do I view my chat history?",
                "answer": "To access your chat history:\n1. Click '📜 View Chat History' from the main menu\n2. You'll see all your previous conversations\n3. Each session shows the agent and timestamp\n4. You can review past conversations anytime",
                "category": "getting_started",
                "order_index": 4
            },
            {
                "question": "Can I attach files or images?",
                "answer": "Yes! You can send:\n📎 Documents (PDF, DOC, etc.)\n🖼️ Images and screenshots\n📹 Videos\n🎵 Audio files\n\nSimply use the attachment button in Telegram to send files during your chat session.",
                "category": "technical",
                "order_index": 5
            },
            {
                "question": "How long does it take to get a response?",
                "answer": "Response times:\n⚡ Instant - For automated FAQs\n👤 2-5 minutes - During business hours\n🌙 5-15 minutes - Outside business hours\n\nWe strive to respond as quickly as possible!",
                "category": "general",
                "order_index": 6
            }
        ]
        
        for faq_data in faqs_data:
            faq_service.create_faq(
                db=db,
                question=faq_data["question"],
                answer=faq_data["answer"],
                category=faq_data["category"],
                is_active=True,
                order_index=faq_data["order_index"]
            )
        
        print(f"✅ Successfully seeded {len(faqs_data)} FAQs!")
        
    except Exception as e:
        print(f"❌ Error seeding FAQs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Seeding FAQ data...")
    seed_faqs()
    print("Done!")