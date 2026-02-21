# V2 JSON Complete Guide - Quick Start

## 🎯 TL;DR

**V2 adds 16 new HPR conditions** while maintaining full backward compatibility with V1.

**New Input Fields:** 16 optional fields (height, BMI, smoking, birth order, etc.)  
**New Output Fields:** 3 new fields (is_hpr, borderline_flags, enhanced rule_output)  
**Breaking Changes:** None - all V1 queries work unchanged

---

## 📥 INPUT: How to Send Data

### Option 1: Simple Text Query (Recommended for Testing)

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "28-year-old at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5, birth order 6, previous pregnancy 10 months ago"
  }'
```

### Option 2: Structured JSON (Recommended for Production)

```bash
curl -X POST http://localhost:8000/assess-structured \
  -H "Content-Type: application/json" \
  -d @patient_data.json
```

**patient_data.json:**
```json
{
  "clinical_summary": "28-year-old G6P5 at 20 weeks with multiple risk factors",
  "structured_data": {
    "patient_info": {
      "age": 28,
      "gestationalWeeks": 20
    },
    "vitals": {
      "heightCm": 135,
      "bmi": 32.0,
      "bpSystolic": 110,
      "bpDiastolic": 70
    },
    "lab_reports": {
      "hemoglobin": 10.5
    },
    "medical_history": {
      "smoking": true
    }
  }
}
```

---

## 📤 OUTPUT: What You Get Back

### Key Fields to Check

```json
{
  "success": true,
  "blocked": false,
  
  // 🆕 V2: Check this first
  "rule_output": {
    "overall_risk": "HIGH",
    "total_score": 10,
    "is_hpr": true,  // 🆕 Composite HPR flag
    
    "triggered_rules": [
      "mild_anaemia",
      "short_stature",      // 🆕 V2
      "high_bmi",           // 🆕 V2
      "smoking",            // 🆕 V2
      "high_birth_order",   // 🆕 V2
      "short_birth_spacing" // 🆕 V2
    ],
    
    // 🆕 V2: Monitor these values
    "borderline_flags": [
      {
        "condition": "Borderline Anaemia",
        "value": "Hb 10.5 g/dL",
        "action": "IFA twice daily, monitor monthly"
      }
    ],
    
    // 🆕 V2: Enhanced guidance
    "referral_facility": "CHC/PHC",
    "immediate_referral": false
  },
  
  "confidence": {
    "score": 0.85,
    "level": "HIGH"
  }
}
```

---

## 🆕 V2 New Conditions (16 Total)

### Quick Reference Table

| Condition | Input Field | Threshold | Score | Example |
|-----------|-------------|-----------|-------|---------|
| Short Stature | `height` | <140 cm | 2 | `"height": 135` |
| High BMI | `bmi` | ≥30 kg/m² | 2 | `"bmi": 32` |
| Smoking | `smoking` | true | 2 | `"smoking": true` |
| Tobacco Use | `tobacco_use` | true | 2 | `"tobacco_use": true` |
| Alcohol Use | `alcohol_use` | true | 2 | `"alcohol_use": true` |
| High Birth Order | `birth_order` | ≥5 | 2 | `"birth_order": 6` |
| Short Birth Spacing | `inter_pregnancy_interval` | <18 months | 2 | `"inter_pregnancy_interval": 10` |
| Long Birth Spacing | `inter_pregnancy_interval` | >59 months | 1 | `"inter_pregnancy_interval": 72` |
| Previous Preterm | `preterm_history` | true | 2 | `"preterm_history": true` |
| Previous Stillbirth | `stillbirth_count` | >0 | 2 | `"stillbirth_count": 1` |
| Previous Abortion | `abortion_count` | >0 | 2 | `"abortion_count": 2` |
| Rh Negative | `rh_negative` | true | 1 | `"rh_negative": true` |
| HIV Positive | `hiv_positive` | true | 3 | `"hiv_positive": true` |
| Syphilis Positive | `syphilis_positive` | true | 3 | `"syphilis_positive": true` |
| Malpresentation | `malpresentation` | true | 2 | `"malpresentation": true` |
| Systemic Illness | `systemic_illness` | true | 2 | `"systemic_illness": true` |

---

## 💻 Code Examples

### Python
```python
import requests

# V2 query with new fields
response = requests.post(
    "http://localhost:8000/query",
    json={
        "query": "28-year-old at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5"
    }
)

data = response.json()

# Check V2 fields
if data['success'] and not data['blocked']:
    # V2 composite HPR flag
    is_hpr = data['rule_output']['is_hpr']
    
    # V2 borderline monitoring
    borderline = data['rule_output'].get('borderline_flags', [])
    
    # V2 triggered rules
    v2_rules = [r for r in data['rule_output']['triggered_rules'] 
                if r in ['short_stature', 'high_bmi', 'smoking', 
                        'high_birth_order', 'short_birth_spacing']]
    
    print(f"Is HPR: {is_hpr}")
    print(f"V2 Rules Triggered: {v2_rules}")
    print(f"Borderline Values: {len(borderline)}")
```

### JavaScript
```javascript
fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: '28-year-old at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5'
  })
})
.then(res => res.json())
.then(data => {
  if (data.success && !data.blocked) {
    // V2 fields
    const isHPR = data.rule_output.is_hpr;
    const borderline = data.rule_output.borderline_flags || [];
    const v2Rules = data.rule_output.triggered_rules.filter(r => 
      ['short_stature', 'high_bmi', 'smoking'].includes(r)
    );
    
    console.log('Is HPR:', isHPR);
    console.log('V2 Rules:', v2Rules);
    console.log('Borderline:', borderline.length);
  }
});
```

### cURL
```bash
# V2 query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "28-year-old at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5, birth order 6"
  }' | jq '.rule_output.is_hpr, .rule_output.triggered_rules'
```

---

## 🔄 Migration Checklist

### For Existing V1 Users

- [ ] **No code changes required** - V1 queries work unchanged
- [ ] **Optional:** Add new V2 fields to input data
- [ ] **Optional:** Check `is_hpr` flag in output
- [ ] **Optional:** Display `borderline_flags` to users
- [ ] **Optional:** Use `referral_facility` for guidance

### For New V2 Users

- [ ] Use structured JSON input for production
- [ ] Include all available V2 fields (height, BMI, smoking, etc.)
- [ ] Check `is_hpr` flag for HPR classification
- [ ] Monitor `borderline_flags` for early intervention
- [ ] Use `referral_facility` for care coordination

---

## 📊 Real-World Examples

### Example 1: Low Risk (V1 and V2 Same)
```json
// Input
{"query": "25-year-old at 16 weeks, Hb 12.0, BP 110/70"}

// Output
{
  "rule_output": {
    "overall_risk": "LOW",
    "total_score": 0,
    "is_hpr": false,
    "triggered_rules": [],
    "borderline_flags": []
  }
}
```

### Example 2: V2 Detects More Risks
```json
// Input
{"query": "28-year-old at 20 weeks, height 135 cm, BMI 32, smoker, Hb 10.5, birth order 6"}

// V1 Output (if it existed)
{
  "overall_risk": "LOW",
  "total_score": 1,
  "triggered_rules": ["mild_anaemia"]
}

// V2 Output
{
  "overall_risk": "HIGH",
  "total_score": 10,
  "is_hpr": true,
  "triggered_rules": [
    "mild_anaemia",
    "short_stature",
    "high_bmi",
    "smoking",
    "high_birth_order",
    "short_birth_spacing"
  ],
  "borderline_flags": [
    {
      "condition": "Borderline Anaemia",
      "value": "Hb 10.5 g/dL",
      "action": "IFA twice daily, monitor monthly"
    }
  ]
}
```

### Example 3: Critical Risk with V2
```json
// Input
{
  "query": "38-year-old at 30 weeks, height 135 cm, HIV positive, Hb 6.5, BP 165/110, twin pregnancy, previous stillbirth"
}

// Output
{
  "rule_output": {
    "overall_risk": "CRITICAL",
    "total_score": 18,
    "is_hpr": true,
    "triggered_rules": [
      "severe_anaemia",
      "hypertension",
      "advanced_maternal_age",
      "twin_pregnancy",
      "short_stature",
      "hiv_positive",
      "previous_stillbirth"
    ],
    "referral_facility": "CEmOC/District Hospital",
    "immediate_referral": true
  }
}
```

---

## 🎓 Best Practices

### Input Data Quality
1. **Include all available fields** - More data = better risk detection
2. **Use structured JSON** for production systems
3. **Validate data** before sending (age 10-60, BP 70-250, etc.)
4. **Include gestational age** for GDM screening checks

### Output Handling
1. **Always check `success` and `blocked` first**
2. **Use `is_hpr` flag** for HPR classification
3. **Display `borderline_flags`** for early intervention
4. **Follow `referral_facility` guidance**
5. **Show `confidence.level`** to users

### Error Handling
```python
response = requests.post(url, json=data)
result = response.json()

if not result['success']:
    # Handle error
    print(f"Error: {result['error']}")
elif result['blocked']:
    # Low confidence - ask for more details
    print("Insufficient data - please provide more clinical details")
else:
    # Process result
    process_hpr_result(result)
```

---

## 📚 Documentation Links

- **Full V2 API Docs:** `API_JSON_FORMATS_V2.md`
- **V1 vs V2 Comparison:** `V2_COMPARISON_TABLE.md`
- **Quick Summary:** `V2_INPUT_OUTPUT_SUMMARY.md`
- **Implementation Status:** `V2_SYSTEM_PROMPT_UPDATE.md`
- **Thresholds Reference:** `COMPLETE_HPR_THRESHOLDS.md`

---

## ❓ FAQ

**Q: Do I need to update my V1 code?**  
A: No, all V1 queries work unchanged.

**Q: What if I don't provide V2 fields?**  
A: They're optional - V2 rules won't trigger without the data.

**Q: Will risk scores be higher in V2?**  
A: Yes, if V2 conditions are present. Same patient may go from LOW to HIGH.

**Q: Is `is_hpr` the same as `overall_risk`?**  
A: No. `is_hpr` is a boolean flag based on Section 19 logic. `overall_risk` is the risk level (LOW/MODERATE/HIGH/CRITICAL).

**Q: What are borderline flags?**  
A: Values approaching thresholds that need monitoring (e.g., Hb 10.5 is borderline anaemia).

**Q: Can I mix V1 and V2 fields?**  
A: Yes, provide any combination. V2 rules trigger only if V2 data is present.

---

**Version:** 2.0.0  
**Date:** 2025-02-21  
**Status:** ✅ Ready for Testing  
**Backward Compatible:** Yes
