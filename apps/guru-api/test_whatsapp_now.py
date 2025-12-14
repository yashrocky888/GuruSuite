#!/usr/bin/env python3
"""
Test WhatsApp Notifications - Ready to Use

This script tests WhatsApp message sending with your configured Twilio credentials.
"""

import os
from dotenv import load_dotenv
from src.notifications.channels.whatsapp import send_whatsapp

# Load environment variables
load_dotenv()

def test_whatsapp():
    """Test WhatsApp message sending."""
    print("="*70)
    print("  WHATSAPP NOTIFICATION TEST")
    print("="*70)
    
    # Your test number (replace with your actual WhatsApp number)
    test_number = input("\n📱 Enter WhatsApp number to test (with country code, e.g., +919110233527): ").strip()
    
    if not test_number:
        test_number = "+919110233527"  # Default from your example
        print(f"   Using default: {test_number}")
    
    # Ensure number starts with +
    if not test_number.startswith("+"):
        test_number = f"+{test_number}"
    
    print(f"\n📤 Sending test message to: {test_number}")
    
    # Test 1: Simple text message
    print(f"\n🔍 Test 1: Simple Text Message")
    print(f"   Message: 'Hello from Guru API! This is a test notification.'")
    try:
        result = send_whatsapp(
            to=test_number,
            message="Hello from Guru API! This is a test notification. 🌟"
        )
        
        if result.get("success"):
            print(f"   ✅ Message sent successfully!")
            print(f"   Message SID: {result.get('message_sid')}")
            print(f"   Status: {result.get('status')}")
            print(f"   Method: {result.get('method', 'text_message')}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
            print(f"\n   💡 Troubleshooting:")
            if "sandbox" in result.get('error', '').lower() or "not registered" in result.get('error', '').lower():
                print(f"      → For Twilio Sandbox, recipient must join first!")
                print(f"      → Send 'join [code]' to +14155238886")
                print(f"      → Get code from: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Content template (your example)
    print(f"\n🔍 Test 2: Content Template Message")
    print(f"   Content SID: HXb5b62575e6e4ff6129ad7c8efe1f983e")
    print(f"   Variables: {{'1': '12/1', '2': '3pm'}}")
    
    use_template = input("\n   Send template message? (y/n): ").strip().lower()
    if use_template == 'y':
        try:
            result = send_whatsapp(
                to=test_number,
                content_sid="HXb5b62575e6e4ff6129ad7c8efe1f983e",
                content_variables={"1": "12/1", "2": "3pm"}
            )
            
            if result.get("success"):
                print(f"   ✅ Template message sent successfully!")
                print(f"   Message SID: {result.get('message_sid')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Method: {result.get('method')}")
            else:
                print(f"   ❌ Failed: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"   ⏭️  Skipped")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Important Notes:")
    print("   - If using Twilio Sandbox, recipient must join first")
    print("   - Check Twilio Console for message status")
    print("   - For production, get approved WhatsApp Business number")
    print("\n📚 Next Steps:")
    print("   - Test via API: Update user preferences to enable WhatsApp")
    print("   - Test daily notifications: Set delivery_time and wait for scheduler")
    print("   - Check delivery logs: GET /notifications/settings/delivery-logs")

if __name__ == "__main__":
    test_whatsapp()

