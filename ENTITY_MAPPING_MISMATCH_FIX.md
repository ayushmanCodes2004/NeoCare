# 🔍 Entity Mapping Mismatch Analysis

## ❌ Critical Mismatches Found!

The 422 error is caused by field mismatches between Backend DTOs and RAG Pipeline models.

---

## 🔴 CRITICAL ISSUES

### Issue 1: Missing Required Fields in Backend DTOs

#### VitalsDTO - MISSING FIELDS
**Backend has:**
- heightCm ✅
- bmi ✅
- bpSystolic ✅
- bpDiastolic ✅

**RAG Pipeline requires:**
- weightKg ❌ MISSING
- heightCm ✅
- bmi ✅
- bpSystolic ✅ (required, no default)
- bpDiastolic ✅ (required, no default)
- pulseRate ❌ MISSING
- respiratoryRate ❌ MISSING
- temperatureCelsius ❌ MISSING
- pallor ❌ MISSING (required, default: false)
- pedalEdema ❌ MISSING (required, default: false)

#### PatientInfoDTO - MISSING FIELDS
**Backend has:**
- age ✅
- gestationalWeeks ✅

**RAG Pipeline requires:**
- patientId ❌ MISSING
- name ❌ MISSING
- age ✅ (required, no default)
- gravida ❌ MISSING
- para ❌ MISSING
- livingChildren ❌ MISSING
- gestationalWeeks ✅
- lmpDate ❌ MISSING
- estimatedDueDate ❌ MISSING

---

## 📊 Complete Field Mapping

### 1. PatientInfo / PatientInfoDTO

| RAG Pipeline | Backend DTO | Status | Fix Required |
|--------------|-------------|--------|--------------|
| `patientId` (Optional[str]) | ❌ Missing | 🔴 MISSING | Add field |
| `name` (Optional[str]) | ❌ Missing | 🔴 MISSING | Add field |
| `age` (int, required) | `age` (Integer, required) | ✅ MATCH | None |
| `gravida` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |
| `para` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |
| `livingChildren` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |
| `gestationalWeeks` (Optional[int]) | `gestationalWeeks` (Integer, required) | ⚠️ PARTIAL | Make optional |
| `lmpDate` (Optional[str]) | ❌ Missing | 🔴 MISSING | Add field |
| `estimatedDueDate` (Optional[str]) | ❌ Missing | 🔴 MISSING | Add field |

### 2. MedicalHistory / MedicalHistoryDTO

| RAG Pipeline | Backend DTO | Status | Fix Required |
|--------------|-------------|--------|--------------|
| `previousLSCS` (bool, default: false) | `previousLscs` (Boolean) | ⚠️ CASE | Fix casing |
| `badObstetricHistory` (bool, default: false) | `badObstetricHistory` (Boolean) | ✅ MATCH | Add default |
| `previousStillbirth` (bool, default: false) | `previousStillbirth` (Boolean) | ✅ MATCH | Add default |
| `previousPretermDelivery` (bool, default: false) | `previousPretermDelivery` (Boolean) | ✅ MATCH | Add default |
| `previousAbortion` (bool, default: false) | `previousAbortion` (Boolean) | ✅ MATCH | Add default |
| `systemicIllness` (Optional[str], default: "None") | `systemicIllness` (String) | ✅ MATCH | Add default |
| `chronicHypertension` (bool, default: false) | `chronicHypertension` (Boolean) | ✅ MATCH | Add default |
| `diabetes` (bool, default: false) | `diabetes` (Boolean) | ✅ MATCH | Add default |
| `thyroidDisorder` (bool, default: false) | `thyroidDisorder` (Boolean) | ✅ MATCH | Add default |
| `smoking` (bool, default: false) | `smoking` (Boolean) | ✅ MATCH | Add default |
| `tobaccoUse` (bool, default: false) | `tobaccoUse` (Boolean) | ✅ MATCH | Add default |
| `alcoholUse` (bool, default: false) | `alcoholUse` (Boolean) | ✅ MATCH | Add default |

### 3. Vitals / VitalsDTO

| RAG Pipeline | Backend DTO | Status | Fix Required |
|--------------|-------------|--------|--------------|
| `weightKg` (Optional[float]) | ❌ Missing | 🔴 MISSING | Add field |
| `heightCm` (Optional[float]) | `heightCm` (Double) | ✅ MATCH | None |
| `bmi` (Optional[float]) | `bmi` (Double) | ✅ MATCH | None |
| `bpSystolic` (int, required) | `bpSystolic` (Integer) | ✅ MATCH | None |
| `bpDiastolic` (int, required) | `bpDiastolic` (Integer) | ✅ MATCH | None |
| `pulseRate` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |
| `respiratoryRate` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |
| `temperatureCelsius` (Optional[float]) | ❌ Missing | 🔴 MISSING | Add field |
| `pallor` (bool, default: false) | ❌ Missing | 🔴 MISSING | Add field |
| `pedalEdema` (bool, default: false) | ❌ Missing | 🔴 MISSING | Add field |

### 4. LabReports / LabReportsDTO

| RAG Pipeline | Backend DTO | Status | Fix Required |
|--------------|-------------|--------|--------------|
| `hemoglobin` (float, required) | `hemoglobin` (Double) | ✅ MATCH | None |
| `plateletCount` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |
| `bloodGroup` (Optional[str]) | ❌ Missing | 🔴 MISSING | Add field |
| `rhNegative` (bool, default: false) | `rhNegative` (Boolean) | ✅ MATCH | Add default |
| `urineProtein` (bool, default: false) | `urineProtein` (Boolean) | ✅ MATCH | Add default |
| `urineSugar` (bool, default: false) | `urineSugar` (Boolean) | ✅ MATCH | Add default |
| `fastingBloodSugar` (Optional[float]) | ❌ Missing | 🔴 MISSING | Add field |
| `ogtt2hrPG` (Optional[float]) | ❌ Missing | 🔴 MISSING | Add field |
| `hivPositive` (bool, default: false) | `hivPositive` (Boolean) | ✅ MATCH | Add default |
| `syphilisPositive` (bool, default: false) | `syphilisPositive` (Boolean) | ✅ MATCH | Add default |
| `serumCreatinine` (Optional[float]) | ❌ Missing | 🔴 MISSING | Add field |
| `ast` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |
| `alt` (Optional[int]) | ❌ Missing | 🔴 MISSING | Add field |

### 5. ObstetricHistory / ObstetricHistoryDTO

| RAG Pipeline | Backend DTO | Status | Fix Required |
|--------------|-------------|--------|--------------|
| `birthOrder` (Optional[int]) | `birthOrder` (Integer) | ✅ MATCH | None |
| `interPregnancyInterval` (Optional[int]) | `interPregnancyInterval` (Integer) | ✅ MATCH | None |
| `stillbirthCount` (int, default: 0) | `stillbirthCount` (Integer) | ✅ MATCH | Add default |
| `abortionCount` (int, default: 0) | `abortionCount` (Integer) | ✅ MATCH | Add default |
| `pretermHistory` (bool, default: false) | `pretermHistory` (Boolean) | ✅ MATCH | Add default |

### 6. PregnancyDetails / PregnancyDetailsDTO

| RAG Pipeline | Backend DTO | Status | Fix Required |
|--------------|-------------|--------|--------------|
| `twinPregnancy` (bool, default: false) | `twinPregnancy` (Boolean) | ✅ MATCH | Add default |
| `malpresentation` (bool, default: false) | `malpresentation` (Boolean) | ✅ MATCH | Add default |
| `placentaPrevia` (bool, default: false) | `placentaPrevia` (Boolean) | ✅ MATCH | Add default |
| `reducedFetalMovement` (bool, default: false) | `reducedFetalMovement` (Boolean) | ✅ MATCH | Add default |
| `amnioticFluidNormal` (bool, default: true) | `amnioticFluidNormal` (Boolean) | ✅ MATCH | Add default |
| `umbilicalDopplerAbnormal` (bool, default: false) | `umbilicalDopplerAbnormal` (Boolean) | ✅ MATCH | Add default |

### 7. CurrentSymptoms / CurrentSymptomsDTO

| RAG Pipeline | Backend DTO | Status | Fix Required |
|--------------|-------------|--------|--------------|
| `headache` (bool, default: false) | `headache` (Boolean) | ✅ MATCH | Add default |
| `visualDisturbance` (bool, default: false) | `visualDisturbance` (Boolean) | ✅ MATCH | Add default |
| `epigastricPain` (bool, default: false) | `epigastricPain` (Boolean) | ✅ MATCH | Add default |
| `decreasedUrineOutput` (bool, default: false) | `decreasedUrineOutput` (Boolean) | ✅ MATCH | Add default |
| `bleedingPerVagina` (bool, default: false) | `bleedingPerVagina` (Boolean) | ✅ MATCH | Add default |
| `convulsions` (bool, default: false) | `convulsions` (Boolean) | ✅ MATCH | Add default |

---

## 🔧 Required Fixes

### Priority 1: Add Missing Required Fields

#### Fix VitalsDTO
```java
@Data
public class VitalsDTO {
    @JsonProperty("weightKg")
    private Double weightKg;  // ADD THIS
    
    @JsonProperty("heightCm")
    private Double heightCm;
    
    @JsonProperty("bmi")
    private Double bmi;
    
    @JsonProperty("bpSystolic")
    private Integer bpSystolic;
    
    @JsonProperty("bpDiastolic")
    private Integer bpDiastolic;
    
    @JsonProperty("pulseRate")
    private Integer pulseRate;  // ADD THIS
    
    @JsonProperty("respiratoryRate")
    private Integer respiratoryRate;  // ADD THIS
    
    @JsonProperty("temperatureCelsius")
    private Double temperatureCelsius;  // ADD THIS
    
    @JsonProperty("pallor")
    private Boolean pallor = false;  // ADD THIS with default
    
    @JsonProperty("pedalEdema")
    private Boolean pedalEdema = false;  // ADD THIS with default
}
```

#### Fix PatientInfoDTO
```java
@Data
public class PatientInfoDTO {
    @JsonProperty("patientId")
    private String patientId;  // ADD THIS
    
    @JsonProperty("name")
    private String name;  // ADD THIS
    
    @NotNull
    @Min(value = 15)
    @Max(value = 55)
    @JsonProperty("age")
    private Integer age;
    
    @JsonProperty("gravida")
    private Integer gravida;  // ADD THIS
    
    @JsonProperty("para")
    private Integer para;  // ADD THIS
    
    @JsonProperty("livingChildren")
    private Integer livingChildren;  // ADD THIS
    
    @JsonProperty("gestationalWeeks")
    private Integer gestationalWeeks;  // Make optional (remove @NotNull)
    
    @JsonProperty("lmpDate")
    private String lmpDate;  // ADD THIS
    
    @JsonProperty("estimatedDueDate")
    private String estimatedDueDate;  // ADD THIS
}
```

#### Fix LabReportsDTO
```java
@Data
public class LabReportsDTO {
    @JsonProperty("hemoglobin")
    private Double hemoglobin;
    
    @JsonProperty("plateletCount")
    private Integer plateletCount;  // ADD THIS
    
    @JsonProperty("bloodGroup")
    private String bloodGroup;  // ADD THIS
    
    @JsonProperty("rhNegative")
    private Boolean rhNegative = false;
    
    @JsonProperty("urineProtein")
    private Boolean urineProtein = false;
    
    @JsonProperty("urineSugar")
    private Boolean urineSugar = false;
    
    @JsonProperty("fastingBloodSugar")
    private Double fastingBloodSugar;  // ADD THIS
    
    @JsonProperty("ogtt2hrPG")
    private Double ogtt2hrPG;  // ADD THIS
    
    @JsonProperty("hivPositive")
    private Boolean hivPositive = false;
    
    @JsonProperty("syphilisPositive")
    private Boolean syphilisPositive = false;
    
    @JsonProperty("serumCreatinine")
    private Double serumCreatinine;  // ADD THIS
    
    @JsonProperty("ast")
    private Integer ast;  // ADD THIS
    
    @JsonProperty("alt")
    private Integer alt;  // ADD THIS
}
```

### Priority 2: Add Default Values to All Boolean Fields

All Boolean fields in DTOs should have default values of `false` (or `true` for `amnioticFluidNormal`).

Example:
```java
@JsonProperty("previousLSCS")
private Boolean previousLscs = false;  // Add = false
```

### Priority 3: Fix Field Name Casing

**MedicalHistoryDTO:**
- Change `previousLscs` to `previousLSCS` (or update @JsonProperty)

---

## 🎯 Quick Fix Solution

### Option 1: Update All Backend DTOs (Recommended)
Add all missing fields to match RAG Pipeline exactly.

### Option 2: Make RAG Pipeline More Flexible
Make all fields optional in RAG Pipeline (not recommended - loses validation).

### Option 3: Use Mapper in Backend
Create a mapper that fills in missing fields with defaults before sending to RAG.

---

## 📝 Implementation Steps

1. **Update VitalsDTO** - Add 6 missing fields
2. **Update PatientInfoDTO** - Add 7 missing fields
3. **Update LabReportsDTO** - Add 6 missing fields
4. **Add defaults to all Boolean fields** - Across all DTOs
5. **Test with API Tester** - Verify 200 response
6. **Update Frontend forms** - Add new fields to visit form

---

## ✅ Verification

After fixes, test with:
```bash
curl -X POST http://localhost:8000/assess-structured \
  -H "Content-Type: application/json" \
  -d @complete-visit-data.json
```

Should return 200 with risk assessment instead of 422.

---

## 🚨 Critical Fields Summary

**Must have values (no defaults):**
- `patient_info.age` - Required integer
- `vitals.bpSystolic` - Required integer
- `vitals.bpDiastolic` - Required integer
- `lab_reports.hemoglobin` - Required float

**All other fields can be null/optional or have defaults.**

---

This mapping document shows exactly what needs to be fixed to resolve the 422 error!
