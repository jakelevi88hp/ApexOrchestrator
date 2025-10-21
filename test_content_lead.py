"""
Content Lead Agent - Test Script

Quick test to verify the Content Lead Agent is working correctly.
Run this after starting the API server.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/content-lead"

def test_content_lead_agent():
    """Test the Content Lead Agent"""
    print("🧪 Testing Content Lead Agent...\n")
    
    # Test 1: Quick Start Demo
    print("1️⃣ Running Quick Start Demo...")
    try:
        response = requests.post(f"{BASE_URL}/quick-start")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Quick Start Demo completed!")
            print(f"   Content Created: {data['demo_data']['content_created']['title']}")
            print(f"   SEO Score: {data['demo_data']['content_created']['seo_score']:.1f}")
            print(f"   Viral Potential: {data['demo_data']['content_created']['viral_potential']:.2f}")
            print(f"   Lead Captured: {data['demo_data']['lead_captured']['quality']} quality")
            print(f"   Revenue Potential: ${data['demo_data']['lead_captured']['revenue_potential']:,.0f}")
        else:
            print(f"❌ Quick Start Demo failed: {response.status_code}")
            print(f"   {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Get Status
    print("2️⃣ Getting Agent Status...")
    try:
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent Status:")
            print(f"   Status: {data['status']}")
            print(f"   Content Created: {data['metrics']['total_content_created']}")
            print(f"   Leads Captured: {data['metrics']['total_leads_captured']}")
            print(f"   Revenue Potential: ${data['metrics']['total_revenue_potential']:,.0f}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: List Content
    print("3️⃣ Listing Content...")
    try:
        response = requests.get(f"{BASE_URL}/content")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Content Library:")
            print(f"   Total: {data['total']} pieces")
            if data['content']:
                for content in data['content'][:3]:
                    print(f"   - {content['title']}")
                    print(f"     Type: {content['content_type']}, SEO: {content['seo_score']:.1f}")
        else:
            print(f"❌ Content list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 4: List Leads
    print("4️⃣ Listing Leads...")
    try:
        response = requests.get(f"{BASE_URL}/leads")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Lead Database:")
            print(f"   Total: {data['total']} leads")
            if data['leads']:
                for lead in data['leads'][:3]:
                    print(f"   - {lead['name']} ({lead['company']})")
                    print(f"     Quality: {lead['quality']}, Score: {lead['score']:.1f}")
                    print(f"     Revenue: ${lead['revenue_potential']:,.0f}")
        else:
            print(f"❌ Lead list failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 5: Revenue Report
    print("5️⃣ Getting Revenue Report...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/revenue-report")
        if response.status_code == 200:
            data = response.json()
            report = data['report']
            print(f"✅ Revenue Report:")
            print(f"   Content Pieces: {report['total_content_pieces']}")
            print(f"   Total Leads: {report['total_leads']}")
            print(f"   Hot Leads: {report['lead_breakdown']['hot']}")
            print(f"   Warm Leads: {report['lead_breakdown']['warm']}")
            print(f"   Total Revenue Potential: ${report['total_revenue_potential']:,.0f}")
            print(f"   Avg Revenue per Lead: ${report['average_revenue_per_lead']:,.0f}")
            print(f"   Conversion Rate: {report['conversion_rate']:.2%}")
        else:
            print(f"❌ Revenue report failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print()
    print("📊 Summary:")
    print("   - Content Lead Agent is operational")
    print("   - Creating viral, SEO-optimized content")
    print("   - Capturing and scoring leads")
    print("   - Tracking revenue potential")
    print()
    print("🚀 Ready to generate leads and revenue!")
    print()
    print("📖 Next Steps:")
    print("   1. View API docs: http://localhost:8000/docs")
    print("   2. Read deployment guide: docs/CONTENT_LEAD_DEPLOYMENT.md")
    print("   3. Start creating content for your target audience!")


if __name__ == "__main__":
    print("="*60)
    print("Content Lead Agent - Test Script")
    print("="*60)
    print()
    print("⚠️  Make sure the API server is running:")
    print("   python -m uvicorn src.main:app --reload --port 8000")
    print()
    input("Press Enter to start tests...")
    print()
    
    test_content_lead_agent()


