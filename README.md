# 🚗 Indonesian Plate Checker API Documentation

## Overview

The Indonesian Plate Checker API provides comprehensive information about Indonesian vehicle license plates. It validates plate formats, queries the official Samsat database, and provides detailed analysis including vehicle type classification and institutional information. **Now with enhanced support for old military plate formats from OCR systems with extended suffix coverage.**

**Base URL:** `https://samsat-api-v1.zeabur.app`

---

## 🎯 Features

- **Plate Validation**: Supports standard Indonesian plate format (XX-XXXX-XXX)
- **Enhanced Military Plate Support**: Recognizes old military format plates with extended coverage (XXXX/XXXXX-XX)
- **Extended Suffix Support**: All numeric suffixes 00-99 and Roman numerals I-IX
- **Flexible Prefix Length**: Supports both 4-digit and 5-digit vehicle numbers
- **Vehicle Classification**: Automatic vehicle type detection based on police identity number
- **Institution Detection**: Identifies government/military institution plates with detailed mapping
- **Regional Information**: Province, city, Samsat office, and address details
- **Format Recognition**: Detects and provides informative responses for non-standard formats
- **OCR Compatibility**: Direct integration with license plate recognition systems

---

## 📋 Supported Formats

### ✅ **Supported by Database**
- **Standard Civil Plates**: `B-1234-ABC`, `D-5678-XYZ`
- **Institution Plates**: `B-1234-ZZP`, `A-9876-ZZT`

### 🎯 **OCR Military Format Support (Enhanced)**
- **Old Military Plates (4-digit)**: `1234-00`, `1234-01`, `1234-99`, `1234-V`
- **Old Military Plates (5-digit)**: `12345-00`, `50072-15`, `98765-IX`
- **Numeric Suffixes**: All codes from `00` to `99` (100 total combinations)
- **Roman Numeral Suffixes**: `I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `VIII`, `IX`
- **Recognition**: Provides detailed institutional analysis
- **Mapping**: Converts old codes to current institution names

### ❌ **Recognized but Not in Database**
- **State Agency**: `RI-1`, `RI-12`
- **Diplomatic**: `CD-12-34`, `CC-56-78`, `CN-12-34`, `CS-56-78`

---

## 🛠️ Endpoints

### 1. **GET /** - API Information
Returns API information and available endpoints.

**Request:**
```http
GET /
```

**Response:**
```json
{
  "message": "Indonesian Plate Checker API with Institution Support & OCR Military Compatibility",
  "database_support": "Mendukung format plat standar Indonesia (XX-XXXX-XXX) dan format militer lama dari OCR",
  "supported_formats": {
    "standard": "XX-XXXX-XXX (e.g., B-1234-ABC, D-5678-ZZP)",
    "old_military": "XXXX-XX atau XXXXX-XX (e.g., 1234-00, 12345-99, 1234-V)"
  },
  "features": {
    "vehicle_classification": "Berdasarkan nomor identitas polisi (1-1999: Mobil Penumpang, 2000-6999: Sepeda Motor, 7000-7999: Mobil Bus, 8000-8999: Mobil Barang, 9000-9999: Kendaraan Khusus)",
    "plate_type": "Sipil atau Institusi (ZZT/ZZU/ZZD/ZZL/ZZP/ZZH)",
    "region_info": "Informasi provinsi, kota, kantor Samsat, dan alamat",
    "military_support": "Deteksi dan analisis plat militer format lama dengan mapping institusi yang diperluas"
  },
  "military_suffix_codes": {
    "numeric": "00-99 (100 kombinasi)",
    "roman": "I, II, III, IV, V, VI, VII, VIII, IX",
    "examples": {
      "00": "Markas Besar TNI",
      "01-05": "TNI AD (Army)",
      "06-08": "TNI AL (Navy)", 
      "09-11": "TNI AU (Air Force)",
      "12-15": "POLRI (Police)",
      "I-IX": "TNI AD (Roman numerals)"
    }
  },
  "endpoints": {
    "GET /check-plate?plate=B1234ABC": "Check standard plate via query parameter",
    "GET /check-plate?plate=12345-00": "Check old military plate via query parameter",
    "POST /check-plate": "Check plate via JSON body {'plate': 'B1234ABC' or '12345-55'}"
  }
}
```

### 2. **GET /check-plate** - Check Plate (Query Parameter)
Checks a license plate using query parameter.

**Request:**
```http
GET /check-plate?plate=B1234ABC
GET /check-plate?plate=50072-00
GET /check-plate?plate=1234-55
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | Yes | License plate number (standard or old military format) |

**Example:**
```bash
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=B1234ABC"
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=50072-00"
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=1234-75"
```

### 3. **POST /check-plate** - Check Plate (JSON Body)
Checks a license plate using JSON request body.

**Request:**
```http
POST /check-plate
Content-Type: application/json

{
  "plate": "B1234ABC"
}
```

**Example:**
```bash
curl -X POST https://samsat-api-v1.zeabur.app/check-plate \
  -H "Content-Type: application/json" \
  -d '{"plate": "12345-85"}'
```

---

## 📤 Response Examples

### ✅ **Standard Civil Plate Found**
**Request:** `B2345ABC`

```json
{
  "status": "Plat sudah terdaftar",
  "jenis_kendaraan": "Sepeda Motor",
  "jenis_plat_nomor": "Sipil",
  "plate_analysis": {
    "kode_wilayah": "B",
    "nomor_identitas_polisi": 2345,
    "kode_khusus": "ABC"
  },
  "plate_region": {
    "province": "DKI Jakarta",
    "city": "Jakarta",
    "samsat_office": "Jakarta Pusat",
    "address": "Jl. Kebon Sirih No. 35"
  }
}
```

### 🏛️ **Institution Plate Found**
**Request:** `B1234ZZP`

```json
{
  "status": "Plat sudah terdaftar",
  "jenis_kendaraan": "Mobil Penumpang",
  "jenis_plat_nomor": "Dinas TNI dan POLRI",
  "institution": "POLRI",
  "plate_analysis": {
    "kode_wilayah": "B",
    "nomor_identitas_polisi": 1234,
    "kode_khusus": "ZZP"
  },
  "plate_region": {
    "province": "DKI Jakarta",
    "city": "Jakarta",
    "samsat_office": "Jakarta Pusat",
    "address": "Jl. Kebon Sirih No. 35"
  }
}
```

### 🪖 **Old Military Plate - TNI Headquarters (5-digit)**
**Request:** `50072-00`

```json
{
  "status": "Format plat militer lama terdeteksi",
  "original_plate": "50072-00",
  "jenis_kendaraan": "Kendaraan Militer",
  "jenis_plat_nomor": "Dinas TNI dan POLRI",
  "institution": "Markas Besar TNI",
  "military_analysis": {
    "nomor_kendaraan": "50072",
    "kode_institusi": "00",
    "tipe_suffix": "Numerik",
    "institution_code": "ZZT",
    "digit_count": 5
  }
}
```

### 🪖 **Old Military Plate - TNI Army (4-digit)**
**Request:** `1234-03`

```json
{
  "status": "Format plat militer lama terdeteksi",
  "original_plate": "1234-03",
  "jenis_kendaraan": "Kendaraan Militer",
  "jenis_plat_nomor": "Dinas TNI dan POLRI",
  "institution": "TNI AD",
  "military_analysis": {
    "nomor_kendaraan": "1234",
    "kode_institusi": "03",
    "tipe_suffix": "Numerik",
    "institution_code": "ZZD",
    "digit_count": 4
  }
}
```

### 🪖 **Old Military Plate - Extended Range**
**Request:** `9876-75`

```json
{
  "status": "Format plat militer lama terdeteksi",
  "original_plate": "9876-75",
  "jenis_kendaraan": "Kendaraan Militer",
  "jenis_plat_nomor": "Dinas TNI dan POLRI",
  "institution": "TNI AD",
  "military_analysis": {
    "nomor_kendaraan": "9876",
    "kode_institusi": "75",
    "tipe_suffix": "Numerik",
    "institution_code": "ZZD",
    "digit_count": 4
  }
}
```

### 🪖 **Old Military Plate with Roman Numerals**
**Request:** `1234-V`

```json
{
  "status": "Format plat militer lama terdeteksi",
  "original_plate": "1234-V",
  "jenis_kendaraan": "Kendaraan Militer",
  "jenis_plat_nomor": "Dinas TNI dan POLRI",
  "institution": "TNI AD",
  "military_analysis": {
    "nomor_kendaraan": "1234",
    "kode_institusi": "V",
    "tipe_suffix": "Angka Romawi",
    "institution_code": "ZZD",
    "digit_count": 4
  }
}
```

### ⚠️ **Invalid Military Suffix**
**Request:** `1234-100`

```json
{
  "error": "Invalid military suffix: 100",
  "note": "Suffix harus berupa angka 00-99 atau angka Romawi I-IX",
  "valid_suffixes": {
    "numeric": "00-99",
    "roman": "I, II, III, IV, V, VI, VII, VIII, IX"
  }
}
```

### ❌ **Standard Plate Not Found**
**Request:** `X9999ZZZ`

```json
{
  "message": "Plat tidak terdaftar"
}
```

### 🚫 **Non-Standard Format (State Agency)**
**Request:** `RI-1`

```json
{
  "message": "Format plat dinas negara tidak didukung oleh database",
  "jenis_plat_nomor": "Dinas Pemerintah",
  "note": "Database hanya mendukung format plat standar (XX-XXXX-XXX)"
}
```

### 🌐 **Non-Standard Format (Diplomatic)**
**Request:** `CD-12-34`

```json
{
  "message": "Format plat diplomatik tidak didukung oleh database",
  "jenis_plat_nomor": "Diplomatik",
  "note": "Database hanya mendukung format plat standar (XX-XXXX-XXX)"
}
```

### ⚠️ **Invalid Format**
**Request:** `INVALID123`

```json
{
  "error": "Format plat nomor tidak valid atau tidak didukung"
}
```

---

## 📊 Classification Rules

### 🚗 **Vehicle Type Classification**
Based on `nomor_identitas_polisi` (middle number):

| Range | Vehicle Type |
|-------|--------------|
| 1-1999 | Mobil Penumpang |
| 2000-6999 | Sepeda Motor |
| 7000-7999 | Mobil Bus |
| 8000-8999 | Mobil Barang |
| 9000-9999 | Kendaraan Khusus |

### 🏛️ **Institution Codes (Current Format)**
Based on `kode_khusus` (suffix):

| Code | Institution |
|------|-------------|
| ZZT | Markas Besar TNI |
| ZZU | TNI AU |
| ZZD | TNI AD |
| ZZL | TNI AL |
| ZZP | POLRI |
| ZZH | Kementrian / Lembaga Negara |

### 🪖 **Military Suffix Mapping (Old Format) - Enhanced**
For old military plates from OCR systems with extended coverage:

#### **Numeric Suffixes (00-99)**
| Range | Institution | Current Code | Examples |
|-------|-------------|--------------|----------|
| 00 | Markas Besar TNI | ZZT | `12345-00` |
| 01-05 | TNI AD (Army) | ZZD | `1234-01`, `5678-03` |
| 06-08 | TNI AL (Navy) | ZZL | `9876-06`, `4567-07` |
| 09-11 | TNI AU (Air Force) | ZZU | `1111-09`, `2222-10` |
| 12-15 | POLRI (Police) | ZZP | `3333-12`, `4444-14` |
| 16-99 | TNI AD (Default) | ZZD | `5555-25`, `6666-99` |

#### **Roman Numeral Suffixes (I-IX)**
| Roman | Institution | Current Code | Examples |
|-------|-------------|--------------|----------|
| I-IX | TNI AD (Traditional) | ZZD | `1234-V`, `5678-IX` |

#### **Prefix Length Support**
| Format | Description | Examples |
|--------|-------------|----------|
| XXXX-XX | 4-digit vehicle number | `1234-00`, `9876-V` |
| XXXXX-XX | 5-digit vehicle number | `12345-00`, `98765-IX` |

### 🏷️ **Plate Type**
- **Sipil**: Regular civilian plates
- **Dinas TNI dan POLRI**: Government/military institution plates

---

## 🔧 HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success - Plate found and analyzed (including old military format) |
| `400` | Bad Request - Missing or invalid parameters |
| `404` | Not Found - Plate not found in database |
| `500` | Internal Server Error |

---

## 📝 Request/Response Details

### **Content Type**
- **Request**: `application/json` (for POST requests)
- **Response**: `application/json`

### **Required Headers**
```http
Content-Type: application/json
```

### **Response Fields**

#### **Success Response Fields (Standard Plates):**
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Registration status message |
| `jenis_kendaraan` | string | Vehicle type classification |
| `jenis_plat_nomor` | string | Plate type (Sipil/Dinas TNI dan POLRI) |
| `institution` | string | Institution name (only for institution plates) |
| `plate_analysis` | object | Detailed plate breakdown |
| `plate_analysis.kode_wilayah` | string | Regional code |
| `plate_analysis.nomor_identitas_polisi` | number | Police identity number |
| `plate_analysis.kode_khusus` | string | Special/suffix code |
| `plate_region` | object | Regional information |
| `plate_region.province` | string | Province name |
| `plate_region.city` | string | City name |
| `plate_region.samsat_office` | string | Samsat office name |
| `plate_region.address` | string | Complete address |

#### **Success Response Fields (Old Military Plates - Enhanced):**
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Detection status message |
| `original_plate` | string | Original input plate number |
| `jenis_kendaraan` | string | Always "Kendaraan Militer" |
| `jenis_plat_nomor` | string | Always "Dinas TNI dan POLRI" |
| `institution` | string | Mapped institution name |
| `military_analysis` | object | Enhanced military plate breakdown |
| `military_analysis.nomor_kendaraan` | string | Vehicle number part (4 or 5 digits) |
| `military_analysis.kode_institusi` | string | Institution code part (00-99 or I-IX) |
| `military_analysis.tipe_suffix` | string | Suffix type ("Numerik" or "Angka Romawi") |
| `military_analysis.institution_code` | string | Current format institution code |
| `military_analysis.digit_count` | number | Length of vehicle number (4 or 5) |

#### **Error Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Error message |
| `message` | string | User-friendly message |
| `note` | string | Additional information (for non-standard formats) |
| `valid_suffixes` | object | Valid suffix ranges (for invalid military suffixes) |

---

## 💡 Usage Examples

### **OCR Integration Workflow - Enhanced**
```javascript
// Example: Process enhanced OCR results through SAMSAT API
async function checkOCRResult(ocrPlateText) {
  const response = await fetch(`https://samsat-api-v1.zeabur.app/check-plate?plate=${ocrPlateText}`);
  const data = await response.json();
  
  if (data.status === "Format plat militer lama terdeteksi") {
    console.log(`Military plate detected: ${data.institution}`);
    console.log(`Vehicle number: ${data.military_analysis.nomor_kendaraan}`);
    console.log(`Suffix type: ${data.military_analysis.tipe_suffix}`);
    console.log(`Digit count: ${data.military_analysis.digit_count}`);
  } else if (data.status === "Plat sudah terdaftar") {
    console.log(`Standard plate found: ${data.jenis_kendaraan}`);
    console.log(`Region: ${data.plate_region.province}`);
  }
  
  return data;
}

// Process different OCR outputs - Enhanced coverage
checkOCRResult("50072-00");   // 5-digit TNI HQ
checkOCRResult("1234-75");    // 4-digit extended range
checkOCRResult("9876-IX");    // Roman numeral
checkOCRResult("B 1234 ABC"); // Standard format
```

### **Military Plate Classification Helper**
```javascript
function classifyMilitaryPlate(plateData) {
  if (plateData.status === "Format plat militer lama terdeteksi") {
    const analysis = plateData.military_analysis;
    
    return {
      era: "pre_2005",
      format: `${analysis.digit_count}_digit_${analysis.tipe_suffix.toLowerCase()}`,
      institution: plateData.institution,
      vehicleNumber: analysis.nomor_kendaraan,
      suffixCode: analysis.kode_institusi,
      modernEquivalent: analysis.institution_code
    };
  }
  return null;
}

// Example usage
const result = await checkOCRResult("12345-85");
const classification = classifyMilitaryPlate(result);
console.log(classification);
// Output: {
//   era: "pre_2005",
//   format: "5_digit_numerik", 
//   institution: "TNI AD",
//   vehicleNumber: "12345",
//   suffixCode: "85",
//   modernEquivalent: "ZZD"
// }
```

### **JavaScript/Node.js**
```javascript
// GET method for extended military plate range
const response = await fetch('https://samsat-api-v1.zeabur.app/check-plate?plate=1234-85');
const data = await response.json();
console.log(`Institution: ${data.institution}`);
console.log(`Suffix Type: ${data.military_analysis.tipe_suffix}`);

// POST method for Roman numeral
const response = await fetch('https://samsat-api-v1.zeabur.app/check-plate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ plate: '9876-VII' })
});
const data = await response.json();
console.log(data);
```

### **Python**
```python
import requests

# Check extended numeric range military plate
response = requests.get('https://samsat-api-v1.zeabur.app/check-plate?plate=50072-95')
data = response.json()
if 'military_analysis' in data:
    print(f"Institution: {data['institution']}")
    print(f"Digits: {data['military_analysis']['digit_count']}")
    print(f"Suffix Type: {data['military_analysis']['tipe_suffix']}")

# Check Roman numeral military plate
response = requests.post('https://samsat-api-v1.zeabur.app/check-plate', 
                        json={'plate': '1234-IX'})
data = response.json()
print(data)
```

### **PHP**
```php
// Check extended range military plate
$response = file_get_contents('https://samsat-api-v1.zeabur.app/check-plate?plate=7890-55');
$data = json_decode($response, true);
if (isset($data['military_analysis'])) {
    echo "Institution: " . $data['institution'] . "\n";
    echo "Vehicle Number: " . $data['military_analysis']['nomor_kendaraan'] . "\n";
    echo "Suffix Code: " . $data['military_analysis']['kode_institusi'] . "\n";
}

// POST method for any military plate format
$plateData = json_encode(['plate' => '12345-99']);
$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/json',
        'content' => $plateData
    ]
]);
$response = file_get_contents('https://samsat-api-v1.zeabur.app/check-plate', false, $context);
$data = json_decode($response, true);
print_r($data);
```

### **cURL**
```bash
# Check 5-digit extended range
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=98765-67"

# Check 4-digit Roman numeral
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=1234-VIII"

# Check standard format with POST
curl -X POST https://samsat-api-v1.zeabur.app/check-plate \
  -H "Content-Type: application/json" \
  -d '{"plate": "B1234ZZP"}'
```

---

## 🔄 Integration with OCR Systems - Enhanced

### **Supported OCR Outputs - Extended Coverage**
The API now handles comprehensive license plate recognition outputs:

| OCR Output | Format | Institution | Suffix Type |
|------------|--------|-------------|-------------|
| `"50072-00"` | 5-digit numeric | Markas Besar TNI | Numerik |
| `"1234-01"` | 4-digit numeric | TNI AD | Numerik |
| `"9876-85"` | 4-digit numeric | TNI AD | Numerik |
| `"5678-V"` | 4-digit Roman | TNI AD | Angka Romawi |
| `"12345-IX"` | 5-digit Roman | TNI AD | Angka Romawi |
| `"B 1234 ABC"` | Standard civil | Database lookup | - |
| `"D5678ZZP"` | Standard institution | POLRI | - |

### **Advanced Error Handling for OCR Integration**
```javascript
async function processAdvancedPlateFromOCR(plateText) {
  try {
    const response = await fetch(`https://samsat-api-v1.zeabur.app/check-plate?plate=${plateText}`);
    
    if (response.status === 200) {
      const data = await response.json();
      
      // Handle different response types
      if (data.status === "Format plat militer lama terdeteksi") {
        return {
          type: "military",
          era: "old_format",
          institution: data.institution,
          analysis: {
            vehicleNumber: data.military_analysis.nomor_kendaraan,
            suffixCode: data.military_analysis.kode_institusi,
            suffixType: data.military_analysis.tipe_suffix,
            digitCount: data.military_analysis.digit_count,
            modernCode: data.military_analysis.institution_code
          },
          valid: true
        };
      } else if (data.status === "Plat sudah terdaftar") {
        return {
          type: "standard",
          era: "current",
          region: data.plate_region.province,
          institution: data.institution || null,
          valid: true
        };
      }
    } else if (response.status === 404) {
      return {
        type: "unknown",
        valid: false,
        message: "Plate not found in database"
      };
    }
  } catch (error) {
    // Handle specific military format errors
    if (error.message.includes("Invalid military suffix")) {
      return {
        type: "invalid_military",
        valid: false,
        message: "Invalid military suffix format",
        supportedSuffixes: {
          numeric: "00-99",
          roman: "I-IX"
        }
      };
    }
    
    return {
      type: "error",
      valid: false,
      message: error.message
    };
  }
}
```

### **Batch Processing for OCR Results**
```javascript
async function processBatchOCRResults(plateTexts) {
  const results = await Promise.all(
    plateTexts.map(async (plate) => {
      const result = await processAdvancedPlateFromOCR(plate);
      return { input: plate, ...result };
    })
  );
  
  // Categorize results
  const categorized = {
    military: results.filter(r => r.type === "military"),
    standard: results.filter(r => r.type === "standard"), 
    invalid: results.filter(r => !r.valid),
    unknown: results.filter(r => r.type === "unknown")
  };
  
  return categorized;
}

// Example usage
const ocrResults = ["50072-00", "1234-75", "B1234ABC", "9876-X", "5555-99"];
const processed = await processBatchOCRResults(ocrResults);
console.log(`Military plates: ${processed.military.length}`);
console.log(`Standard plates: ${processed.standard.length}`);
console.log(`Invalid plates: ${processed.invalid.length}`);
```

---

## 🔒 Rate Limiting
Currently, there are no rate limits implemented. However, please use the API responsibly and avoid excessive requests.

---

## 🐛 Error Handling - Enhanced
The API returns appropriate HTTP status codes and detailed error messages for military format validation.

**Enhanced Error Patterns:**
```javascript
const response = await fetch('https://samsat-api-v1.zeabur.app/check-plate?plate=1234-100');

if (response.status === 200) {
  const data = await response.json();
  
  // Check for military format errors in successful responses
  if (data.error && data.error.includes("Invalid military suffix")) {
    console.log("Invalid military suffix:", data.error);
    console.log("Valid suffixes:", data.valid_suffixes);
    // Handle invalid suffix (e.g., numbers > 99, invalid Roman numerals)
  } else if (data.status === "Format plat militer lama terdeteksi") {
    console.log("Valid military format:", data.military_analysis);
  }
} else if (response.status === 404) {
  // Plate not found (for standard plates only)
  const error = await response.json();
  console.log(error.message); // "Plat tidak terdaftar"
}
```

---

## 📞 Support
For API support or questions, please refer to the API home endpoint for the most current information.

---

## 📄 License
This API is provided for educational and development purposes. Please ensure compliance with applicable laws and regulations when using vehicle registration data.

---

## 🔄 Changelog

### Version 1.2.0 - Enhanced Military Support
- ✅ **Extended numeric suffix support**: All codes from 00-99 (100 combinations)
- ✅ **Flexible prefix length**: Support for both 4-digit and 5-digit vehicle numbers
- ✅ **Enhanced validation**: Comprehensive error handling for invalid suffixes
- ✅ **Detailed analysis**: Extended military_analysis object with suffix type and digit count
- ✅ **Improved mapping**: Logical institution assignment for extended suffix ranges
- ✅ **Better error messages**: Specific validation feedback for military format errors

### Version 1.1.0 - OCR Military Support
- ✅ Added support for old military plate formats from OCR systems
- ✅ Enhanced military suffix mapping (00, 01, 02, 09, 10, I-IX)
- ✅ Detailed military plate analysis responses
- ✅ Institution name mapping for old military codes
- ✅ Historical context for pre-2005 military numbering
- ✅ Direct compatibility with license plate recognition APIs

### Version 1.0.0 - Initial Release
- ✅ Standard Indonesian plate format support
- ✅ Institution plate recognition
- ✅ SAMSAT database integration
- ✅ Vehicle type classification
- ✅ Regional information lookup