"""
Test Script - Phase 3
Quick test to verify all systems working before running Streamlit
"""

from data_loader import DataLoader
from query_engine import QueryEngine
from llm_interface import LLMInterface
import json

def test_data_loading():
    """Test 1: Data loads correctly"""
    print("\n" + "="*70)
    print("TEST 1: Data Loading")
    print("="*70)
    
    data = DataLoader().load_all()
    
    assert len(data.entities) > 0, "No entities loaded"
    assert len(data.projects) > 0, "No projects loaded"
    assert len(data.communications) > 0, "No communications loaded"
    
    print("✅ All data loaded successfully!")
    return data

def test_structured_queries(data):
    """Test 2: Structured queries work"""
    print("\n" + "="*70)
    print("TEST 2: Structured Queries")
    print("="*70)
    
    query_engine = QueryEngine(data)
    
    # Test 1: Developers by region
    print("\n🔍 Query 1: ARR projects in Latin America")
    results = query_engine.query_developers_by_region_and_type(
        'ARR', 
        ['Brazil', 'Peru', 'Mexico']
    )
    print(f"   Found {len(results)} developers")
    if results:
        print(f"   Example: {results[0]['developer']}")
    
    # Test 2: Match investors
    print("\n🔍 Query 2: Matching investors for P001")
    results = query_engine.query_matching_investors('P001')
    if results:
        print(f"   Project: {results['project']['DeveloperName']}")
        print(f"   Matching investors: {len(results['matching_investors'])}")
    
    # Test 3: Communications summary
    print("\n🔍 Query 3: Communications for VerdeNova")
    results = query_engine.summarize_communications('VerdeNova')
    if results:
        print(f"   Entity: {results['entity']['canonical_name']}")
        print(f"   Total communications: {results['total_count']}")
    
    # Test 4: Meeting actionables
    print("\n🔍 Query 4: Last meeting with NorthStar")
    results = query_engine.find_actionables_from_meeting('NorthStar')
    if results:
        print(f"   Entity: {results['entity']['canonical_name']}")
        print(f"   Transcript ID: {results['transcript_id']}")
    
    print("\n✅ All structured queries working!")
    return query_engine

def test_semantic_search(query_engine):
    """Test 3: Semantic search"""
    print("\n" + "="*70)
    print("TEST 3: Semantic Search")
    print("="*70)
    
    print("🔍 Initializing embeddings (may take ~30 seconds)...")
    query_engine.init_semantic_search()
    
    print("\n🔍 Searching for: 'community consultations'")
    results = query_engine.semantic_search_communications(
        "community consultations",
        top_k=3
    )
    
    print(f"   Found {len(results)} relevant communications")
    for i, result in enumerate(results[:2], 1):
        print(f"   {i}. [{result['type']}] {result['communication_id']} (score: {result['similarity_score']:.3f})")
    
    print("\n✅ Semantic search working!")

def test_llm_integration(query_engine):
    """Test 4: LLM generates responses"""
    print("\n" + "="*70)
    print("TEST 4: LLM Integration")
    print("="*70)
    
    llm = LLMInterface()
    
    print("🤖 Testing Groq API connection...")
    
    # Simple test query
    results = query_engine.query_developers_by_region_and_type('ARR', ['Brazil'])
    
    print("🤖 Generating response...")
    response = llm.generate_response(
        "Which developers have ARR projects in Brazil?",
        results,
        'developers_by_region'
    )
    
    print("\n📝 Generated Response:")
    print("-" * 70)
    print(response[:300] + "..." if len(response) > 300 else response)
    print("-" * 70)
    
    print("\n✅ LLM integration working!")

def main():
    """Run all tests"""
    print("="*70)
    print("🧪 CALCULUS CARBON - SYSTEM TEST")
    print("="*70)
    
    try:
        # Test 1: Data loading
        data = test_data_loading()
        
        # Test 2: Structured queries
        query_engine = test_structured_queries(data)
        
        # Test 3: Semantic search
        test_semantic_search(query_engine)
        
        # Test 4: LLM
        test_llm_integration(query_engine)
        
        # Summary
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        print("\n🚀 System is ready! Run the chatbot with:")
        print("   streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Fix the error above before running the chatbot.")

if __name__ == "__main__":
    main()