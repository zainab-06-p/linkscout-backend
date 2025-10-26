"""
Phase 2.2: Entity Verification System

This module verifies entities (people, places, organizations) mentioned in claims:
- People: Check credentials, affiliations, expertise
- Places: Verify locations exist and details are correct
- Organizations: Verify legitimacy and registration

Uses pattern matching and basic heuristics for verification.
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Entity:
    """Represents an extracted entity"""
    text: str
    type: str  # PERSON, ORGANIZATION, LOCATION
    context: str  # Surrounding text
    verified: bool
    confidence: float
    issues: List[str]

@dataclass
class EntityVerificationResult:
    """Complete entity verification analysis"""
    total_entities: int
    verified_entities: int
    suspicious_entities: int
    fake_expert_detected: bool
    verification_score: float  # 0-100
    verdict: str  # VERIFIED, SUSPICIOUS, FAKE_EXPERTS
    entities: List[Dict]
    red_flags: List[str]

class EntityVerifier:
    """Verify entities mentioned in text"""
    
    def __init__(self):
        # Known fake expert patterns
        self.fake_expert_patterns = [
            r'anonymous\s+expert',
            r'unnamed\s+scientist',
            r'leading\s+researcher(?!\s+[A-Z])',  # "leading researcher" without name
            r'top\s+doctor(?!\s+[A-Z])',
            r'several\s+experts',
            r'many\s+scientists',
            r'insider\s+source',
            r'whistleblower',
        ]
        
        # Known credential patterns
        self.credential_patterns = [
            r'(?:Dr\.|Doctor|Professor|PhD)',
            r'(?:MD|PhD|MPH|DDS|JD)',
            r'(?:B\.S\.|M\.S\.|B\.A\.|M\.A\.)',
        ]
        
        # Suspicious name patterns
        self.suspicious_name_patterns = [
            r'^(?:John|Jane)\s+Doe$',  # Generic names
            r'^[A-Z]\.\s+[A-Z]\.$',  # Just initials
        ]
        
        # Common organization types
        self.org_types = [
            'University', 'Institute', 'Hospital', 'Corporation', 'Company',
            'Foundation', 'Association', 'Society', 'Center', 'Laboratory',
            'Agency', 'Department', 'Ministry', 'Bureau'
        ]
        
        # Known prestigious institutions (partial list)
        self.prestigious_institutions = {
            'harvard', 'stanford', 'mit', 'oxford', 'cambridge',
            'yale', 'princeton', 'caltech', 'columbia', 'chicago',
            'who', 'cdc', 'nasa', 'fda', 'nih', 'nhs',
            'reuters', 'associated press', 'bbc', 'nature', 'science'
        }
        
        # Suspicious organization keywords
        self.suspicious_org_keywords = [
            'anonymous', 'secret', 'underground', 'shadow',
            'independent researcher', 'citizen journalist',
            'alternative media', 'truth seeker'
        ]
        
        print("👤 [ENTITY] Entity Verification System initialized")
    
    def verify_entities(self, text: str) -> EntityVerificationResult:
        """Verify all entities in text"""
        print(f"\n👤 [ENTITY] Analyzing entities in text ({len(text)} chars)...")
        
        # Extract entities
        people = self._extract_people(text)
        organizations = self._extract_organizations(text)
        locations = self._extract_locations(text)
        
        all_entities = people + organizations + locations
        
        print(f"   Found: {len(people)} people, {len(organizations)} orgs, {len(locations)} locations")
        
        # Verify each entity
        verified_count = 0
        suspicious_count = 0
        fake_expert_detected = False
        red_flags = []
        
        for entity in all_entities:
            if entity.verified:
                verified_count += 1
            else:
                suspicious_count += 1
            
            if entity.issues:
                red_flags.extend(entity.issues)
                if 'fake_expert' in entity.issues:
                    fake_expert_detected = True
        
        total_entities = len(all_entities)
        
        # Calculate verification score
        if total_entities > 0:
            verification_score = (verified_count / total_entities) * 100
        else:
            verification_score = 100  # No entities = nothing to verify
        
        # Determine verdict
        if fake_expert_detected or suspicious_count > total_entities * 0.5:
            verdict = "FAKE_EXPERTS"
        elif suspicious_count > 0:
            verdict = "SUSPICIOUS"
        else:
            verdict = "VERIFIED"
        
        print(f"   ✅ Verification: {verified_count}/{total_entities} verified, {suspicious_count} suspicious")
        if fake_expert_detected:
            print(f"   ⚠️ FAKE EXPERT DETECTED!")
        
        return EntityVerificationResult(
            total_entities=total_entities,
            verified_entities=verified_count,
            suspicious_entities=suspicious_count,
            fake_expert_detected=fake_expert_detected,
            verification_score=verification_score,
            verdict=verdict,
            entities=[self._entity_to_dict(e) for e in all_entities],
            red_flags=list(set(red_flags))  # Remove duplicates
        )
    
    def _extract_people(self, text: str) -> List[Entity]:
        """Extract and verify person names"""
        people = []
        
        # Pattern 1: Dr./Professor + Name
        dr_pattern = r'(?:Dr\.|Doctor|Professor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        for match in re.finditer(dr_pattern, text):
            name = match.group(1)
            context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
            
            # Verify name
            issues = []
            verified = True
            confidence = 80
            
            # Check for suspicious patterns
            if re.match(r'^(?:John|Jane)\s+Doe$', name):
                issues.append('generic_name')
                verified = False
                confidence = 20
            
            # Check for credentials in context
            has_credentials = any(re.search(pattern, context) for pattern in self.credential_patterns)
            if has_credentials:
                confidence += 10
            
            people.append(Entity(
                text=f"Dr. {name}",
                type="PERSON",
                context=context,
                verified=verified,
                confidence=confidence,
                issues=issues
            ))
        
        # Pattern 2: Fake expert patterns
        for pattern in self.fake_expert_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                people.append(Entity(
                    text=match.group(0),
                    type="PERSON",
                    context=context,
                    verified=False,
                    confidence=10,
                    issues=['fake_expert', 'anonymous_source']
                ))
        
        # Pattern 3: Named people with credentials
        name_credential_pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s+(?:PhD|MD|Professor)'
        for match in re.finditer(name_credential_pattern, text):
            name = match.group(1)
            context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
            
            people.append(Entity(
                text=match.group(0),
                type="PERSON",
                context=context,
                verified=True,
                confidence=85,
                issues=[]
            ))
        
        return people
    
    def _extract_organizations(self, text: str) -> List[Entity]:
        """Extract and verify organization names"""
        organizations = []
        
        # Pattern 1: Known prestigious institutions
        for institution in self.prestigious_institutions:
            pattern = re.compile(r'\b' + re.escape(institution) + r'\b', re.IGNORECASE)
            for match in re.finditer(pattern, text):
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                organizations.append(Entity(
                    text=match.group(0),
                    type="ORGANIZATION",
                    context=context,
                    verified=True,
                    confidence=95,
                    issues=[]
                ))
        
        # Pattern 2: Organization types
        for org_type in self.org_types:
            pattern = r'([A-Z][a-zA-Z\s]+' + org_type + r')'
            for match in re.finditer(pattern, text):
                org_name = match.group(1).strip()
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                # Check if already found
                if any(org_name.lower() in e.text.lower() for e in organizations):
                    continue
                
                # Verify organization
                issues = []
                verified = True
                confidence = 60
                
                # Check for suspicious keywords
                if any(keyword in org_name.lower() for keyword in self.suspicious_org_keywords):
                    issues.append('suspicious_name')
                    verified = False
                    confidence = 30
                
                organizations.append(Entity(
                    text=org_name,
                    type="ORGANIZATION",
                    context=context,
                    verified=verified,
                    confidence=confidence,
                    issues=issues
                ))
        
        # Pattern 3: Suspicious organizations
        for keyword in self.suspicious_org_keywords:
            pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
            for match in re.finditer(pattern, text):
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                organizations.append(Entity(
                    text=match.group(0),
                    type="ORGANIZATION",
                    context=context,
                    verified=False,
                    confidence=20,
                    issues=['suspicious_organization', 'unverifiable_source']
                ))
        
        return organizations
    
    def _extract_locations(self, text: str) -> List[Entity]:
        """Extract and verify location names"""
        locations = []
        
        # Pattern 1: Countries (simplified list)
        countries = [
            'United States', 'USA', 'America', 'China', 'Russia', 'India', 'Japan',
            'Germany', 'France', 'United Kingdom', 'UK', 'Britain', 'Canada',
            'Australia', 'Brazil', 'Mexico', 'Italy', 'Spain', 'South Korea',
            'Indonesia', 'Turkey', 'Saudi Arabia', 'Argentina', 'Poland'
        ]
        
        for country in countries:
            pattern = re.compile(r'\b' + re.escape(country) + r'\b', re.IGNORECASE)
            for match in re.finditer(pattern, text):
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                locations.append(Entity(
                    text=match.group(0),
                    type="LOCATION",
                    context=context,
                    verified=True,
                    confidence=90,
                    issues=[]
                ))
        
        # Pattern 2: Major cities (simplified list)
        cities = [
            'New York', 'Los Angeles', 'London', 'Paris', 'Tokyo', 'Beijing',
            'Moscow', 'Delhi', 'Shanghai', 'Mumbai', 'Seoul', 'Berlin',
            'Madrid', 'Rome', 'Toronto', 'Sydney', 'Washington', 'Chicago'
        ]
        
        for city in cities:
            pattern = re.compile(r'\b' + re.escape(city) + r'\b', re.IGNORECASE)
            for match in re.finditer(pattern, text):
                context = text[max(0, match.start()-50):min(len(text), match.end()+50)]
                
                # Check if already found
                if any(city.lower() in e.text.lower() for e in locations):
                    continue
                
                locations.append(Entity(
                    text=match.group(0),
                    type="LOCATION",
                    context=context,
                    verified=True,
                    confidence=85,
                    issues=[]
                ))
        
        return locations
    
    def _entity_to_dict(self, entity: Entity) -> Dict:
        """Convert Entity to dictionary"""
        return {
            'text': entity.text,
            'type': entity.type,
            'verified': entity.verified,
            'confidence': entity.confidence,
            'issues': entity.issues,
            'context': entity.context[:100]  # Truncate context
        }

# Singleton instance
_entity_verifier = None

def get_entity_verifier() -> EntityVerifier:
    """Get or create entity verifier singleton"""
    global _entity_verifier
    if _entity_verifier is None:
        _entity_verifier = EntityVerifier()
    return _entity_verifier

def verify_text_entities(text: str) -> Dict:
    """Verify entities in text"""
    verifier = get_entity_verifier()
    result = verifier.verify_entities(text)
    
    return {
        'total_entities': result.total_entities,
        'verified_entities': result.verified_entities,
        'suspicious_entities': result.suspicious_entities,
        'fake_expert_detected': result.fake_expert_detected,
        'verification_score': result.verification_score,
        'verdict': result.verdict,
        'entities': result.entities,
        'red_flags': result.red_flags
    }

# Test function
if __name__ == "__main__":
    print("=" * 70)
    print("👤 ENTITY VERIFICATION TEST")
    print("=" * 70)
    
    test_text = """
    According to Dr. John Smith from Harvard University, this treatment is revolutionary.
    An anonymous expert claims that NASA is hiding the truth. Leading researcher says 
    the vaccine is dangerous. Professor Jane Doe from MIT confirms these findings.
    
    The CDC and WHO have both investigated this claim in Washington and London.
    Several scientists from independent research groups support this theory.
    """
    
    result = verify_text_entities(test_text)
    
    print("\n" + "=" * 70)
    print("📊 RESULTS")
    print("=" * 70)
    print(f"Total Entities: {result['total_entities']}")
    print(f"Verified: {result['verified_entities']}")
    print(f"Suspicious: {result['suspicious_entities']}")
    print(f"Fake Expert Detected: {result['fake_expert_detected']}")
    print(f"Verification Score: {result['verification_score']:.1f}/100")
    print(f"Verdict: {result['verdict']}")
    
    print(f"\n📋 Entities Found:")
    for entity in result['entities']:
        status = "✅" if entity['verified'] else "❌"
        print(f"  {status} [{entity['type']}] {entity['text']} - {entity['confidence']}%")
        if entity['issues']:
            print(f"     Issues: {', '.join(entity['issues'])}")
    
    if result['red_flags']:
        print(f"\n⚠️ Red Flags:")
        for flag in result['red_flags']:
            print(f"  - {flag}")
    
    print("\n✅ Test complete!")
