#!/usr/bin/env python3
"""
Test WhatsApp Content Template Sending

This script tests sending WhatsApp messages using Twilio content templates.
"""

import os
from dotenv import load_dotenv
from src.notifications.channels.whatsapp import send_whatsapp

load_dotenv()

def test_whatsapp_template():
    """Test WhatsApp content template sending."""
    print("="*70)
    print("  WHATSAPP CONTENT TEMPLATE TEST")
    print("="*70)
    
    # Your test number
    test_number = "+919110233527"  # Replace with your test number
    
    # Test 1: Simple text message
    print(f"\n📱 Test 1: Simple Text Message")
    print(f"   To: {test_number}")
    try:
        result = send_whatsapp(
            to=test_number,
            message="Hello from Guru API! This is a test message."
        )
        if result.get("success"):
            print(f"   ✅ Message sent successfully!")
            print(f"   Message SID: {result.get('message_sid')}")
            print(f"   Status: {result.get('status')}")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Content template (as per your example)
    print(f"\n📱 Test 2: Content Template Message")
    print(f"   To: {test_number}")
    print(f"   Content SID: HXb5b62575e6e4ff6129ad7c8efe1f983e")
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
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70)
    print("\n💡 Note:")
    print("   - For sandbox, recipient must join first")
    print("   - Send 'join [code]' to +14155238886")
    print("   - Check Twilio console for sandbox code")

if __name__ == "__main__":
    test_whatsapp_template()

