# intelligent_test_generator_optimized.py

import json
import os
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
# from langchain_llm7 import ChatLLM7
from langchain_core.prompts import ChatPromptTemplate
# from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import requests
from dotenv import load_dotenv

# ============================================================
# STEP 1: Define Structured Output (Solve Problem 2)
# ============================================================
# Get llm7 api key
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
class TestCase(BaseModel):
    """Structured test case output"""
    name: str = Field(description="Test method name in camelCase")
    description: str = Field(description="What this test validates")
    scenario: str = Field(description="Test scenario (e.g., 'invalid_id', 'sql_injection')")
    input_data: Dict = Field(description="Input parameters or body")
    expected_status: int = Field(description="Expected HTTP status code")
    test_type: str = Field(description="Type:  functional, edge_case, security, negative")
    priority: str = Field(description="Priority:  HIGH, MEDIUM, LOW")
    reasoning: str = Field(description="Why this test is important")

class TestSuggestions(BaseModel):
    """Collection of test suggestions"""
    endpoint:  str
    method: str
    suggested_tests: List[TestCase] = Field(description="List of suggested test cases")
    coverage_assessment: str = Field(description="Assessment of what's missing")

# ============================================================
# STEP 2: Smart LLM Usage (Solve Problems 1, 3, 4)
# ============================================================

class SmartTestGenerator:
    """Uses LLM efficiently - only for creative suggestions"""
    
    def __init__(self, openapi_spec_path: str, config_path: str):
        if openapi_spec_path.startswith('http'):
            response = requests.get(openapi_spec_path)
            response.raise_for_status()
            self.spec = response.json()
        else:
            self.spec = self._load_json(openapi_spec_path)
        
        
        # Keep path for later updates to config.json
        self.config_path = config_path
        # Load config if present; default to empty when missing
        try:
            self.config = self._load_json(config_path)
        except FileNotFoundError:
            self.config = {}
        
        # Initialize LLM (use gpt-4o-mini for cost savings)
        self.llm = ChatOpenAI(
            base_url="https://api.llm7.io/v1",
            api_key=os.getenv("LLM7_API_KEY"),
            model_name="gpt-4.1-nano-2025-04-14",  # 15x cheaper than gpt-4! 
            temperature=0.3,  # Slightly creative but consistent
            max_tokens=1000   # Limit output to control costs
        )
        
        # Setup output parser
        self.llm = self.llm.with_structured_output(TestSuggestions)
        
        # Track LLM usage
        self.llm_calls = 0
        self.total_tokens = 0
    
    def _load_json(self, path: str) -> dict:
        with open(path, 'r') as f:
            return json. load(f)
    
    def generate_tests(self):
        """Main entry point"""
        
        print("🤖 Smart Test Generator Starting.. .\n")
        
        # STEP 1: Parse OpenAPI (NO LLM)
        print("📖 Step 1: Parsing OpenAPI spec (no LLM, free)...")
        all_endpoints = self._parse_openapi()
        print(f"   ✓ Found {len(all_endpoints)} endpoints\n")
        
        # STEP 2: Analyze existing tests (NO LLM)
        print("🔍 Step 2: Analyzing existing tests (no LLM, free)...")
        tested_endpoints = self._analyze_existing_tests()
        print(f"   ✓ Found tests for {len(tested_endpoints)} endpoints\n")
        
        # STEP 3: Identify gaps (NO LLM)
        print("📊 Step 3: Identifying gaps (no LLM, free)...")
        gaps = self._identify_gaps(all_endpoints, tested_endpoints)
        print(f"   ✓ Found {len(gaps)} untested endpoints\n")
        
        # STEP 4: Generate basic tests (NO LLM)
        print("⚙️  Step 4: Generating basic tests (no LLM, free)...")
        basic_tests = self._generate_basic_tests(gaps)
        print(f"   ✓ Generated {sum(len(t) for t in basic_tests. values())} basic tests\n")
        
        # STEP 5: LLM enhancement for creative edge cases (USE LLM)
        print("🧠 Step 5: Getting LLM suggestions for creative edge cases...")
        enhanced_tests = self._get_llm_enhancements(gaps, basic_tests)
        print(f"   ✓ LLM suggested {sum(len(t) for t in enhanced_tests.values())} additional tests")
        print(f"   💰 LLM calls made: {self.llm_calls}")
        print(f"   💸 Estimated cost: ${self._estimate_cost():.4f}\n")
        
        # STEP 6: Write Java files
        print("📝 Step 6: Writing Java test files...")
        self._write_java_files(basic_tests, enhanced_tests)
        print("   ✓ Complete!\n")
        
        return {
            'basic_tests': basic_tests,
            'llm_enhanced_tests': enhanced_tests,
            'llm_calls': self.llm_calls,
            'estimated_cost': self._estimate_cost()
        }
    
    def _parse_openapi(self) -> Dict:
        """Parse OpenAPI spec - NO LLM NEEDED"""
        endpoints = {}
        
        for path, methods in self.spec['paths'].items():
            for method, details in methods.items():
                key = f"{method.upper()} {path}"
                endpoints[key] = {
                    'path': path,
                    'method': method. upper(),
                    'summary': details.get('summary', ''),
                    'parameters': details.get('parameters', []),
                    'requestBody': details.get('requestBody', {}),
                    'responses': details.get('responses', {}),
                    'security': details.get('security', []),
                    'tags': details. get('tags', [])
                }
        
        return endpoints
    
    def _analyze_existing_tests(self) -> Dict:
        """Analyze existing tests from config - NO LLM NEEDED"""
        tested = {}
        
        for route, details in self.config. get('routes', {}).items():
            if 'methods' in details:
                for method, method_details in details['methods'].items():
                    if method_details.get('status') == 'IMPLEMENTED':
                        key = f"{method} {route}"
                        tested[key] = method_details
            elif details.get('status') == 'IMPLEMENTED':
                key = f"{details['method']} {route}"
                tested[key] = details
        
        return tested
    
    def _identify_gaps(self, all_endpoints: Dict, tested_endpoints: Dict) -> Dict:
        """Find untested endpoints - NO LLM NEEDED"""
        gaps = {}
        
        for endpoint_key, details in all_endpoints.items():
            if endpoint_key not in tested_endpoints:
                gaps[endpoint_key] = details
        
        return gaps
    
    def _generate_basic_tests(self, gaps: Dict) -> Dict:
        """Generate standard tests - NO LLM NEEDED"""
        tests = {}
        
        for endpoint_key, details in gaps.items():
            endpoint_tests = []
            
            # Happy path
            endpoint_tests.append({
                'name': self._build_test_name(endpoint_key, 'ValidRequest', 'Success'),
                'type': 'functional',
                'description': f"Test {endpoint_key} with valid data",
                'expected_status': 200 if details['method'] == 'GET' else 201
            })
            
            # Auth test if required
            if details['security']:
                endpoint_tests.append({
                    'name': self._build_test_name(endpoint_key, 'NoAuth', '401'),
                    'type': 'security',
                    'description':  f"Test {endpoint_key} without authentication",
                    'expected_status': 401
                })
            
            # Parameter edge cases
            for param in details['parameters']:
                if param.get('schema', {}).get('type') == 'integer':
                    endpoint_tests. append({
                        'name':  self._build_test_name(endpoint_key, f'Invalid{param["name"]. title()}', '422'),
                        'type': 'edge_case',
                        'description': f"Test with invalid {param['name']}",
                        'expected_status': 422
                    })
            
            tests[endpoint_key] = endpoint_tests
        
        return tests
    
    def _get_llm_enhancements(self, gaps: Dict, basic_tests: Dict) -> Dict:
        """Use LLM ONLY for creative suggestions - EFFICIENT"""
        
        enhanced_tests = {}
        
        # Only call LLM for HIGH-PRIORITY endpoints (save money)
        high_priority_endpoints = self._select_high_priority(gaps)
        
        for endpoint_key in high_priority_endpoints[: 5]:  # Limit to top 5
            print(f"   🧠 Asking LLM for creative tests:  {endpoint_key}")
            
            # Create SMALL, focused prompt (100-300 tokens)
            suggestions = self._ask_llm_for_endpoint(
                endpoint_key, 
                gaps[endpoint_key],
                basic_tests. get(endpoint_key, [])
            )
            
            if suggestions:
                enhanced_tests[endpoint_key] = suggestions
                self.llm_calls += 1
        
        return enhanced_tests
    
    def _ask_llm_for_endpoint(self, endpoint_key: str, endpoint_details: Dict, existing_tests: List) -> List[TestCase]:
        """Ask LLM for ONE endpoint - SMALL PROMPT"""
        
        # Build focused prompt with ChatPromptTemplate
        prompt = ChatPromptTemplate(
            [
                ("system", "You are an expert QA engineer specializing in API testing."),
                ("human", """For this SINGLE endpoint:
- Endpoint: {endpoint}
- Method: {method}
- Summary: {summary}
- Parameters: {parameters}
- Security: {security}

We already have these basic tests:
{existing_tests}

Suggest 3-5 CREATIVE edge cases or security tests we might have missed.
Focus on:
- Unusual but valid inputs
- Security vulnerabilities (SQL injection, XSS, etc.)
- Race conditions
- Business logic edge cases""")
            ]
        )
        
        # Prepare compact input
        existing_tests_str = "\n".join([f"- {t['name']}: {t['description']}" for t in existing_tests[: 3]])
        
        params_str = ", ".join([p['name'] for p in endpoint_details. get('parameters', [])])
        
        # Call LLM
        try:
            chain = prompt | self.llm 
            
            result = chain.invoke({
                "endpoint": endpoint_key,
                "method": endpoint_details['method'],
                "summary": endpoint_details. get('summary', 'No summary'),
                "parameters": params_str or "None",
                "security": "Required" if endpoint_details['security'] else "None",
                "existing_tests":  existing_tests_str or "None yet"
            })
            
            # Track tokens (approximate)
            self.total_tokens += 500  # Rough estimate
            
            return result.suggested_tests if result else []
            
        except Exception as e:
            print(f"      ⚠️  LLM call failed: {e}")
            return []
    
    def _select_high_priority(self, gaps: Dict) -> List[str]:
        """Select high-priority endpoints - NO LLM"""
        
        priorities = []
        
        for endpoint_key, details in gaps. items():
            score = 0
            
            # Critical tags
            if 'Orders' in details['tags']:
                score += 50
            if 'Cart' in details['tags']:
                score += 40
            if 'Authentication' in details['tags']:
                score += 45
            
            # Has parameters (more edge cases)
            score += len(details['parameters']) * 5
            
            # Requires auth (security critical)
            if details['security']: 
                score += 15
            
            priorities.append((endpoint_key, score))
        
        # Sort by score
        priorities.sort(key=lambda x: x[1], reverse=True)
        
        return [ep for ep, score in priorities]
    
    def _build_test_name(self, endpoint_key: str, scenario: str, expected:  str) -> str:
        """Build test name"""
        parts = endpoint_key.split()
        method = parts[0] if parts else 'Test'
        path = parts[1] if len(parts) > 1 else ''
        
        resource = path.replace('/', ' ').replace('{', '').replace('}', '').title().replace(' ', '')
        
        return f"test{method. capitalize()}{resource}_{scenario}_{expected}"
    
    def _estimate_cost(self) -> float:
        """Estimate LLM cost"""
        # gpt-4o-mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens
        input_cost = (self.total_tokens * 0.5) * (0.15 / 1_000_000)  # 50% input
        output_cost = (self.total_tokens * 0.5) * (0.60 / 1_000_000)  # 50% output
        return input_cost + output_cost
    
    def _write_java_files(self, basic_tests: Dict, enhanced_tests: Dict):
        """Write Java test files and update config.json with implemented tests"""
        # Combine basic + enhanced
        all_tests = {}
        for endpoint, tests in basic_tests.items():
            all_tests[endpoint] = tests + enhanced_tests.get(endpoint, [])

        # Collect updates for config.json
        config_updates = {}

        # Write files
        for endpoint, tests in all_tests.items():
            class_name, method_names, rel_java_file = self._write_java_file(endpoint, tests)
            if class_name:
                config_updates[class_name] = {
                    'file': rel_java_file,
                    'methods': method_names,
                }

        # Append/merge into config.json
        if config_updates:
            self._update_config_with_tests(config_updates)
    
    def _write_java_file(self, endpoint: str, tests: List):
        """Write single Java file and return metadata for config update"""
        class_name = endpoint.replace(' ', '_').replace('/', '_').replace('{', '').replace('}', '').title().replace('_', '') + 'Test'
        
        java_code = f"""package generated;

import config.BaseTest;
import org.testng.annotations.Test;
import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

/**
 * GENERATED TESTS
 * Endpoint: {endpoint}
 * Tests: {len(tests)} (Basic + LLM-suggested)
 */
public class {class_name} extends BaseTest {{
"""
        method_names = []
        for test in tests:
            # Handle both dict (basic tests) and TestCase objects (LLM tests)
            if isinstance(test, dict):
                test_name = test['name']
                test_desc = test['description']
            else:  # TestCase object
                test_name = test.name
                test_desc = test.description
            method_names.append(test_name)
            java_code += f"""
    @Test
    public void {test_name}() {{
        // {test_desc}
        // TODO: Implement test logic
    }}
"""
        
        java_code += "}\n"
        
        # Write file
        output_path = f"../java-tests/src/test/java/generated/{class_name}.java"
        os.makedirs(os.path. dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(java_code)
        
        print(f"      ✓ {class_name}.java ({len(tests)} tests)")
        # Return class metadata and relative path used inside config.json
        return class_name, method_names, f"src/test/java/generated/{class_name}.java"

    def _update_config_with_tests(self, updates: Dict[str, Dict[str, List[str]]]):
        """Append/merge implemented test information into config.json under 'implemented_tests'.

        updates format:
            {
              "ClassNameTest": {"file": "src/test/java/...", "methods": ["m1", "m2"]},
              ...
            }
        """
        # Load current config from disk to avoid stale state
        try:
            with open(self.config_path, 'r') as f:
                current = json.load(f)
        except FileNotFoundError:
            current = {}

        implemented = current.get('implemented_tests', {})

        for cls, meta in updates.items():
            if cls in implemented:
                # Merge methods without duplicates
                existing_methods = set(implemented[cls].get('methods', []))
                new_methods = set(meta.get('methods', []))
                merged = sorted(existing_methods.union(new_methods))
                # Preserve existing file path if present; otherwise set it
                file_path = implemented[cls].get('file') or meta.get('file')
                implemented[cls]['file'] = file_path
                implemented[cls]['methods'] = merged
            else:
                implemented[cls] = {
                    'file': meta.get('file'),
                    'methods': sorted(list(set(meta.get('methods', []))))
                }

        current['implemented_tests'] = implemented

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        # Write back to disk
        with open(self.config_path, 'w') as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        # Update in-memory copy
        self.config = current


# ============================================================
# USAGE
# ============================================================

if __name__ == "__main__":
    generator = SmartTestGenerator(
        openapi_spec_path='http://localhost:8000/openapi.json',
        config_path='../java-tests/src/test/resources/config.json'
    )
    
    results = generator.generate_tests()
    
    print("\n" + "="*60)
    print("📊 GENERATION SUMMARY")
    print("="*60)
    print(f"Basic tests generated: {sum(len(t) for t in results['basic_tests'].values())}")
    print(f"LLM-enhanced tests:  {sum(len(t) for t in results['llm_enhanced_tests'].values())}")
    print(f"LLM calls made: {results['llm_calls']}")
    print(f"Estimated cost: ${results['estimated_cost']:.4f}")
    print("="*60)