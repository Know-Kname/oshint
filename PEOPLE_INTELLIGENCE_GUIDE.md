# People Intelligence (PEOPLEINT) - User Guide

## 🎯 Overview

The **People Intelligence Module** is an ethical OSINT tool for gathering publicly available information about individuals using legitimate data sources and search techniques.

---

## ⚠️ CRITICAL: Authorization & Legal Compliance

### **AUTHORIZED USES**
✅ Security assessments (with written authorization)
✅ Background checks (with subject consent)
✅ CTF competitions and training
✅ Educational purposes
✅ Legal investigations
✅ Fraud prevention and due diligence

### **PROHIBITED USES**
❌ Stalking or harassment
❌ Identity theft
❌ Unauthorized surveillance
❌ Privacy violations
❌ Any illegal activity

**YOU ARE RESPONSIBLE FOR LEGAL COMPLIANCE IN YOUR JURISDICTION**

---

## 📋 Features

### Information Types Collected

1. **Basic Information**
   - Full name and aliases
   - Age and date of birth
   - City of birth
   - Current location

2. **Contact Information**
   - Phone numbers
   - Email addresses
   - Physical addresses (historical)

3. **Online Presence**
   - Social media profiles
   - Usernames across platforms
   - Websites and blogs
   - GitHub/professional profiles

4. **Professional Information**
   - Current and past employers
   - Job titles
   - Educational background
   - Professional licenses

5. **Digital Footprint**
   - Domain registrations
   - Public records
   - Data breach involvement
   - Online activity patterns

---

## 🔍 Search Methods

### 1. Search by Name

**Usage:**
```python
from elite_people_intel import PeopleIntelligence

intel = PeopleIntelligence()
profile = await intel.search_by_name(
    full_name="John Doe",
    city="New York",
    state="NY"
)
```

**Data Sources:**
- Public search engines
- Social media platforms (public profiles)
- Professional networks (LinkedIn, etc.)
- People search engines (Whitepages, TruePeopleSearch)
- Public records databases

### 2. Search by Phone Number

**Usage:**
```python
profile = await intel.search_by_phone("+1-555-123-4567")
```

**Data Sources:**
- TrueCaller (requires API key)
- Whitepages reverse lookup
- NumVerify validation
- Carrier information

### 3. Search by Email

**Usage:**
```python
profile = await intel.search_by_email("john.doe@example.com")
```

**Data Sources:**
- Email validation services
- Gravatar profile lookup
- HaveIBeenPwned breach database
- Social media account recovery
- Professional network searches

### 4. Search by Username

**Usage:**
```python
profile = await intel.search_by_username("johndoe123")
```

**Platforms Checked:**
- GitHub
- Twitter/X
- Instagram
- Reddit
- LinkedIn
- Medium
- Dev.to
- Twitch
- YouTube
- TikTok
- Pinterest
- Telegram

### 5. Comprehensive Search

**Usage:**
```python
profile = await intel.search_comprehensive(
    name="John Doe",
    phone="+1-555-123-4567",
    email="john.doe@example.com",
    username="johndoe123",
    city="New York",
    state="NY"
)
```

**Result:** Aggregated profile from all search methods

---

## 🚀 Quick Start

### CLI Interface

```bash
python3 cli_interface.py
```

Select option **[7] People Intelligence (PEOPLEINT)**

Follow the prompts:
1. Choose search method (name, phone, email, username, comprehensive)
2. Enter search parameters
3. View results
4. Export to JSON (optional)

### API Interface

```bash
# Start API server
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Search by name
curl -X POST http://localhost:8000/people/search-by-name \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "city": "New York",
    "state": "NY"
  }'

# Search by phone
curl -X POST http://localhost:8000/people/search-by-phone \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+1-555-123-4567"}'

# Search by email
curl -X POST http://localhost:8000/people/search-by-email \
  -H "Content-Type: application/json" \
  -d '{"email": "john.doe@example.com"}'

# Comprehensive search
curl -X POST http://localhost:8000/people/search-comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone": "+1-555-123-4567",
    "email": "john.doe@example.com",
    "username": "johndoe123"
  }'
```

### Python Script

```python
import asyncio
from elite_people_intel import PeopleIntelligence

async def main():
    # Initialize with config
    intel = PeopleIntelligence()

    # Search by name
    profile = await intel.search_by_name("John Doe", city="New York")

    # Generate report
    report = intel.generate_report(profile, format='text')
    print(report)

    # Export to JSON
    json_report = intel.generate_report(profile, format='json')
    with open('person_report.json', 'w') as f:
        f.write(json_report)

    await intel.close_session()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔑 API Keys Configuration

Add to `config.yaml`:

```yaml
api_keys:
  # Phone number validation
  numverify_key: "your_numverify_api_key"
  truecaller_key: "your_truecaller_api_key"

  # Data breach checking
  hibp_key: "your_haveibeenpwned_api_key"

  # Additional sources
  pipl_key: "your_pipl_api_key"
  clearbit_key: "your_clearbit_api_key"
```

### Getting API Keys

1. **NumVerify** (Phone Validation)
   - URL: https://numverify.com/
   - Free tier: 250 requests/month

2. **HaveIBeenPwned** (Data Breaches)
   - URL: https://haveibeenpwned.com/API/Key
   - Cost: $3.50/month

3. **TrueCaller** (Phone Lookup)
   - URL: https://www.truecaller.com/
   - Requires business account

---

## 📊 Report Formats

### Text Report

```
======================================================================
PEOPLE INTELLIGENCE REPORT
======================================================================

Target: John Doe
Confidence Score: 87.5/100
Last Updated: 2025-11-29T10:30:00

----------------------------------------------------------------------

[BASIC INFORMATION]
  Age: 35
  Date of Birth: 1990-03-15

[LOCATION INFORMATION]
  Current Location: New York, NY
  Previous Addresses: 3 found

[CONTACT INFORMATION]
  Phone Numbers:
    - +1-555-123-4567
  Email Addresses:
    - john.doe@example.com
    - jdoe@company.com

[SOCIAL MEDIA PRESENCE]
  LinkedIn:
    - https://linkedin.com/in/johndoe
  Twitter:
    - https://twitter.com/johndoe123
  GitHub:
    - https://github.com/johndoe

[PROFESSIONAL INFORMATION]
  Employers: TechCorp, StartupXYZ
  Job Titles: Software Engineer, Senior Developer
  Education: MIT Computer Science

[SECURITY ALERTS]
  ⚠️  Found in 2 data breach(es):
    - LinkedIn (2021)
    - Adobe (2013)

[DATA SOURCES] (8)
  ✓ Google Search
  ✓ LinkedIn
  ✓ Whitepages
  ✓ NumVerify
  ✓ HaveIBeenPwned
  ...

======================================================================
```

### JSON Report

```json
{
  "full_name": "John Doe",
  "age": 35,
  "date_of_birth": "1990-03-15",
  "current_city": "New York",
  "current_state": "NY",
  "phone_numbers": ["+1-555-123-4567"],
  "email_addresses": ["john.doe@example.com"],
  "social_media": {
    "LinkedIn": ["https://linkedin.com/in/johndoe"],
    "Twitter": ["https://twitter.com/johndoe123"]
  },
  "data_breaches": ["LinkedIn", "Adobe"],
  "confidence_score": 87.5,
  "sources": ["Google Search", "LinkedIn", "HaveIBeenPwned"],
  "last_updated": "2025-11-29T10:30:00"
}
```

### HTML Report

Interactive HTML report with:
- Professional formatting
- Clickable links
- Security alerts highlighted
- Print-friendly layout

---

## 🎯 Best Practices

### 1. Start Broad, Then Narrow

```python
# Start with name only
profile = await intel.search_by_name("John Doe")

# Review results, then narrow with location
profile = await intel.search_by_name("John Doe", city="New York", state="NY")
```

### 2. Cross-Reference Multiple Sources

```python
# Use comprehensive search for best results
profile = await intel.search_comprehensive(
    name="John Doe",
    email="john@example.com",
    username="johndoe"
)
```

### 3. Verify Information

- Cross-check data across multiple sources
- Look for consistency in dates, locations
- Verify social media profiles manually
- Check confidence scores

### 4. Respect Privacy

- Only search for publicly available information
- Don't aggregate data for malicious purposes
- Follow platform terms of service
- Obtain proper authorization

### 5. Document Your Searches

```python
# Save reports with timestamps
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
filename = f"person_{name}_{timestamp}.json"

with open(filename, 'w') as f:
    f.write(intel.generate_report(profile, format='json'))
```

---

## 🔒 Privacy & Security

### What This Module Does NOT Do

❌ Does not hack or bypass security
❌ Does not access private/protected information
❌ Does not use illegal data sources
❌ Does not store personal data without consent
❌ Does not track real-time location

### What This Module DOES

✅ Searches publicly available information
✅ Aggregates data from legitimate sources
✅ Respects robots.txt and terms of service
✅ Provides attribution for all data sources
✅ Includes confidence scoring

---

## 📈 Confidence Scoring

The module calculates a confidence score (0-100) based on:

- **Basic Info** (20 points): Name, age, DOB, location
- **Contact Info** (20 points): Phone numbers, email addresses
- **Online Presence** (30 points): Social media, usernames
- **Professional** (15 points): Employment, education
- **Data Sources** (15 points): Number and quality of sources

**Score Interpretation:**
- 90-100: High confidence, multiple verified sources
- 70-89: Good confidence, cross-referenced data
- 50-69: Moderate confidence, limited sources
- 0-49: Low confidence, sparse data

---

## 🛠️ Advanced Features

### Custom Data Source Integration

```python
class CustomPeopleIntel(PeopleIntelligence):
    async def _search_custom_source(self, name, profile):
        # Add your custom data source
        pass
```

### Batch Processing

```python
names = ["John Doe", "Jane Smith", "Bob Johnson"]
profiles = []

for name in names:
    profile = await intel.search_by_name(name)
    profiles.append(profile)
```

### Automated Monitoring

```python
# Monitor for new data on a person
async def monitor_person(name, interval=3600):
    while True:
        profile = await intel.search_by_name(name)
        if profile.data_breaches:
            print(f"[!] New breach detected for {name}")
        await asyncio.sleep(interval)
```

---

## 🚨 Common Issues

### Issue: No results found

**Solutions:**
- Try alternate name spellings
- Remove middle name/initial
- Add location filter
- Try username search instead

### Issue: Too many results

**Solutions:**
- Add city and state filters
- Use additional identifiers (email, phone)
- Cross-reference with age/DOB

### Issue: API rate limits

**Solutions:**
- Implement request delays
- Use API keys for higher limits
- Cache results locally

---

## 📚 Additional Resources

### Legal Information
- [OSINT Framework](https://osintframework.com/)
- [GDPR Compliance](https://gdpr.eu/)
- [Privacy Laws by Country](https://www.dlapiperdataprotection.com/)

### Tools & Techniques
- [Bellingcat's Online Investigation Toolkit](https://www.bellingcat.com/)
- [OSINT Combine](https://www.osintcombine.com/)
- [IntelTechniques](https://inteltechniques.com/)

### Training
- [TryHackMe OSINT Room](https://tryhackme.com/room/ohsint)
- [SANS SEC487: Open-Source Intelligence Gathering](https://www.sans.org/cyber-security-courses/open-source-intelligence-gathering/)

---

## 📝 Example Use Cases

### 1. Security Assessment

```python
# Check if employee credentials are exposed
profile = await intel.search_by_email("employee@company.com")
if profile.data_breaches:
    print(f"[!] ALERT: Found in breaches: {profile.data_breaches}")
```

### 2. Background Verification

```python
# Verify job candidate information
profile = await intel.search_comprehensive(
    name="John Doe",
    email="john@email.com"
)

# Check professional history matches resume
if "TechCorp" in profile.employers:
    print("[+] Employment verified")
```

### 3. CTF Competition

```python
# Find flag hidden in public profiles
profile = await intel.search_by_username("ctf_target_user")
for platform, urls in profile.social_media.items():
    print(f"[*] Check {platform}: {urls}")
```

---

## 🤝 Contributing

To add new data sources:

1. Create method in `PeopleIntelligence` class
2. Add to appropriate search function
3. Update documentation
4. Add tests
5. Submit pull request

---

## ⚖️ Disclaimer

This tool is provided for **educational and authorized security assessment purposes only**. Users are responsible for:

- Obtaining proper authorization before use
- Compliance with local, state, and federal laws
- Respecting individual privacy rights
- Following ethical OSINT practices

The authors are not responsible for misuse of this tool.

---

**Last Updated**: 2025-11-29
**Version**: 1.0.0
**Module**: elite_people_intel.py
