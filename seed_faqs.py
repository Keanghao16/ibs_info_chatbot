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
        
        # Check if categories exist
        categories = faq_service.get_all_faq_categories(db)
        if not categories:
            print("❌ Error: No categories found. Please run seed_categories.py first!")
            return
        
        # Create slug to ID mapping
        category_map = {cat.slug: cat.id for cat in categories}
        print(f"📁 Found categories: {', '.join(category_map.keys())}")
        
        faqs_data = [
            {
                "question": "How do I start a chat?",
                "answer": "To start a chat session:\n1. Click on '💬 Start Chat' button from the main menu\n2. You will be connected to an available agent\n3. Start typing your message to begin the conversation",
                "category_slug": "getting_started",
                "order_index": 1
            },
            {
                "question": "How do I contact support?",
                "answer": "To contact our support team:\n1. Use the chat feature by clicking '💬 Start Chat'\n2. An agent will assist you with your inquiry\n3. You can also send us a direct message anytime\n4. For urgent matters, mention 'URGENT' in your message",
                "category_slug": "general",
                "order_index": 1
            },
            {
                "question": "What are your operating hours?",
                "answer": "Our support is available:\n🕐 24/7 - Round the clock support\n📅 7 days a week - Including weekends\n🚀 Instant response - Average response time: 2-5 minutes\n🌍 Global coverage - Support in multiple time zones",
                "category_slug": "general",
                "order_index": 2
            },
            {
                "question": "How do I view my chat history?",
                "answer": "To access your chat history:\n1. Click '📜 View Chat History' from the main menu\n2. You'll see all your previous conversations\n3. Each session shows the agent and timestamp\n4. You can review past conversations anytime",
                "category_slug": "getting_started",
                "order_index": 2
            },
            {
                "question": "Can I attach files or images?",
                "answer": "Yes! You can send:\n📎 Documents (PDF, DOC, etc.)\n🖼️ Images and screenshots\n📹 Videos\n🎵 Audio files\n\nSimply use the attachment button in Telegram to send files during your chat session.",
                "category_slug": "technical",
                "order_index": 1
            },
            {
                "question": "How long does it take to get a response?",
                "answer": "Response times:\n⚡ Instant - For automated FAQs\n👤 2-5 minutes - During business hours\n🌙 5-15 minutes - Outside business hours\n\nWe strive to respond as quickly as possible!",
                "category_slug": "general",
                "order_index": 3
            },
            {
                "question": "What should I do if the bot isn't responding?",
                "answer": "If you're experiencing issues:\n1. Try restarting the bot with /start command\n2. Check your internet connection\n3. Clear your Telegram cache\n4. If the problem persists, contact our support team\n\nOur technical team is always ready to help!",
                "category_slug": "troubleshooting",
                "order_index": 1
            },
            {
                "question": "How do I update my account information?",
                "answer": "To update your account:\n1. Your profile is automatically synced with Telegram\n2. Update your Telegram profile (name, photo)\n3. Changes will reflect in our system automatically\n4. For additional info, contact support",
                "category_slug": "account",
                "order_index": 1
            },
            {
                "question": "Is my data secure?",
                "answer": "Yes! We take security seriously:\n🔒 End-to-end encryption for messages\n🛡️ Secure data storage\n🔐 Privacy-focused design\n📋 GDPR compliant\n\nYour privacy and security are our top priorities.",
                "category_slug": "account",
                "order_index": 2
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept various payment methods:\n💳 Credit/Debit Cards (Visa, Mastercard, AMEX)\n🏦 Bank Transfer\n💰 Digital Wallets (PayPal, Apple Pay, Google Pay)\n₿ Cryptocurrency (Bitcoin, Ethereum)\n\nAll transactions are secure and encrypted.",
                "category_slug": "billing",
                "order_index": 1
            },
            {
                "question": "How can I get a refund?",
                "answer": "For refunds:\n1. Contact our billing support team\n2. Provide your transaction ID\n3. Explain the reason for refund\n4. Processing time: 5-7 business days\n\nWe have a 30-day money-back guarantee for most services.",
                "category_slug": "billing",
                "order_index": 2
            },
            {
                "question": "The bot is giving me error messages",
                "answer": "Common solutions for error messages:\n1. Screenshot the error message\n2. Try using /start to restart\n3. Clear conversation history\n4. Update Telegram app\n5. Contact support with the error details\n\nInclude the error screenshot for faster resolution.",
                "category_slug": "troubleshooting",
                "order_index": 2
            },
            {
                "question": "Can I use the bot on multiple devices?",
                "answer": "Yes! You can use our bot on:\n📱 Mobile phones (iOS & Android)\n💻 Desktop (Windows, Mac, Linux)\n🌐 Web browser (Telegram Web)\n\nYour chat history syncs across all devices automatically through Telegram.",
                "category_slug": "technical",
                "order_index": 2
            },
            {
                "question": "How do I report a bug or issue?",
                "answer": "To report issues:\n1. Use the /start command and select 'Start Chat'\n2. Describe the bug in detail\n3. Include steps to reproduce\n4. Attach screenshots if possible\n5. Our team will investigate immediately\n\nBug reports help us improve the service!",
                "category_slug": "troubleshooting",
                "order_index": 3
            },
            {
                "question": "What languages do you support?",
                "answer": "Currently supported languages:\n🇺🇸 English (Primary)\n🇮🇩 Indonesian\n🇪🇸 Spanish\n🇫🇷 French\n🇩🇪 German\n\nMore languages coming soon! Request your language through support.",
                "category_slug": "general",
                "order_index": 4
            }
        ]
        
        # Validate and create FAQs
        created_count = 0
        skipped_count = 0
        
        for faq_data in faqs_data:
            category_slug = faq_data["category_slug"]
            if category_slug not in category_map:
                print(f"⚠️  Skipping FAQ (category '{category_slug}' not found): {faq_data['question']}")
                skipped_count += 1
                continue
            
            try:
                faq_service.create_faq(
                    db=db,
                    question=faq_data["question"],
                    answer=faq_data["answer"],
                    category_id=category_map[category_slug],  # Use category ID instead of slug
                    is_active=True,
                    order_index=faq_data["order_index"]
                )
                created_count += 1
                print(f"✅ Created FAQ: {faq_data['question'][:50]}...")
            except Exception as e:
                print(f"❌ Error creating FAQ '{faq_data['question'][:50]}...': {e}")
                skipped_count += 1
        
        print(f"\n📊 Summary:")
        print(f"   ✅ Successfully created: {created_count} FAQs")
        if skipped_count > 0:
            print(f"   ⚠️  Skipped: {skipped_count} FAQs")
        
    except Exception as e:
        print(f"❌ Error seeding FAQs: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🌱 Seeding FAQ Data")
    print("=" * 60)
    seed_faqs()
    print("=" * 60)
    print("✨ Done!")
    print("=" * 60)