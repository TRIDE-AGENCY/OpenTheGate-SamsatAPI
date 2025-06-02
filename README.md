# 🚗 Indonesian Plate Checker API Documentation

## Overview

The Indonesian Plate Checker API provides comprehensive information about Indonesian vehicle license plates. It validates plate formats, queries the official Samsat database, and provides detailed analysis including vehicle type classification and institutional information. **Now with enhanced support for old military plate formats from OCR systems.**

**Base URL:** `https://samsat-api-v1.zeabur.app`

---

## 🎯 Features

- **Plate Validation**: Supports standard Indonesian plate format (XX-XXXX-XXX)
- **Military Plate Support**: Recognizes and analyzes old military format plates (XXXXX-XX)
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
- **Old Military Plates**: `12345-00`, `50072-00`, `1234-01`, `1234-V`
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
    "old_military": "XXXXX-XX atau XXXX-X (e.g., 12345-00, 1234-V)"
  },
  "features": {
    "vehicle_classification": "Berdasarkan nomor identitas polisi (1-1999: Mobil Penumpang, 2000-6999: Sepeda Motor, 7000-7999: Mobil Bus, 8000-8999: Mobil Barang, 9000-9999: Kendaraan Khusus)",
    "plate_type": "Sipil atau Institusi (ZZT/ZZU/ZZD/ZZL/ZZP/ZZH)",
    "region_info": "Informasi provinsi, kota, kantor Samsat, dan alamat",
    "military_support": "Deteksi dan analisis plat militer format lama dengan mapping institusi"
  },
  "military_suffix_codes": {
    "00": "Markas Besar TNI",
    "01": "TNI AD (Army)",
    "02": "TNI AL (Navy)", 
    "09": "TNI AU (Air Force)",
    "10": "POLRI (Police)",
    "I-IX": "TNI AD (Roman numerals)"
  },
  "endpoints": {
    "GET /check-plate?plate=B1234ABC": "Check standard plate via query parameter",
    "GET /check-plate?plate=12345-00": "Check old military plate via query parameter",
    "POST /check-plate": "Check plate via JSON body {'plate': 'B1234ABC' or '12345-00'}"
  }
}
```

### 2. **GET /check-plate** - Check Plate (Query Parameter)
Checks a license plate using query parameter.

**Request:**
```http
GET /check-plate?plate=B1234ABC
GET /check-plate?plate=50072-00
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | Yes | License plate number (standard or old military format) |

**Example:**
```bash
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=B1234ABC"
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=50072-00"
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
  -d '{"plate": "50072-00"}'
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

### 🪖 **Old Military Plate (OCR Compatible)**
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
    "format": "Sistem plat militer lama",
    "era": "Pre-2005 military numbering system"
  },
  "note": "Plat militer format lama, tidak dapat divalidasi dengan database SAMSAT standar",
  "validation_status": "Format recognized but not database-verifiable"
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
    "format": "Sistem plat militer lama",
    "era": "Pre-2005 military numbering system"
  },
  "note": "Plat militer format lama, tidak dapat divalidasi dengan database SAMSAT standar",
  "validation_status": "Format recognized but not database-verifiable"
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

### 🪖 **Military Suffix Mapping (Old Format)**
For old military plates from OCR systems:

| Old Code | Institution | Current Code |
|----------|-------------|--------------|
| 00 | Markas Besar TNI | ZZT |
| 01 | TNI AD (Army) | ZZD |
| 02 | TNI AL (Navy) | ZZL |
| 09 | TNI AU (Air Force) | ZZU |
| 10 | POLRI (Police) | ZZP |
| I-IX | TNI AD (Roman numerals) | ZZD |

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

#### **Success Response Fields (Old Military Plates):**
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Detection status message |
| `original_plate` | string | Original input plate number |
| `jenis_kendaraan` | string | Always "Kendaraan Militer" |
| `jenis_plat_nomor` | string | Always "Dinas TNI dan POLRI" |
| `institution` | string | Mapped institution name |
| `military_analysis` | object | Military plate breakdown |
| `military_analysis.nomor_kendaraan` | string | Vehicle number part |
| `military_analysis.kode_institusi` | string | Institution code part |
| `military_analysis.format` | string | Format description |
| `military_analysis.era` | string | Historical period |
| `note` | string | Additional information |
| `validation_status` | string | Database validation status |

#### **Error Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Error message |
| `message` | string | User-friendly message |
| `note` | string | Additional information (for non-standard formats) |

---

## 💡 Usage Examples

### **OCR Integration Workflow**
```javascript
// Example: Process OCR result through SAMSAT API
async function checkOCRResult(ocrPlateText) {
  const response = await fetch(`https://samsat-api-v1.zeabur.app/check-plate?plate=${ocrPlateText}`);
  const data = await response.json();
  
  if (data.status === "Format plat militer lama terdeteksi") {
    console.log(`Military plate detected: ${data.institution}`);
    console.log(`Vehicle number: ${data.military_analysis.nomor_kendaraan}`);
  } else if (data.status === "Plat sudah terdaftar") {
    console.log(`Standard plate found: ${data.jenis_kendaraan}`);
    console.log(`Region: ${data.plate_region.province}`);
  }
  
  return data;
}

// Process different OCR outputs
checkOCRResult("50072-00");  // Old military format
checkOCRResult("B 1234 ABC"); // Standard format
```

### **JavaScript/Node.js**
```javascript
// GET method for military plate
const response = await fetch('https://samsat-api-v1.zeabur.app/check-plate?plate=12345-00');
const data = await response.json();
console.log(data);

// POST method for standard plate
const response = await fetch('https://samsat-api-v1.zeabur.app/check-plate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ plate: 'B1234ABC' })
});
const data = await response.json();
console.log(data);
```

### **Python**
```python
import requests

# Check old military plate
response = requests.get('https://samsat-api-v1.zeabur.app/check-plate?plate=50072-00')
data = response.json()
print(f"Institution: {data.get('institution', 'N/A')}")

# Check standard plate
response = requests.post('https://samsat-api-v1.zeabur.app/check-plate', 
                        json={'plate': 'B1234ABC'})
data = response.json()
print(data)
```

### **PHP**
```php
// Check military plate
$response = file_get_contents('https://samsat-api-v1.zeabur.app/check-plate?plate=1234-V');
$data = json_decode($response, true);
if (isset($data['institution'])) {
    echo "Institution: " . $data['institution'];
}

// POST method for any plate
$plateData = json_encode(['plate' => 'D5678ZZU']);
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
# Check old military format
curl "https://samsat-api-v1.zeabur.app/check-plate?plate=50072-00"

# Check standard format with POST
curl -X POST https://samsat-api-v1.zeabur.app/check-plate \
  -H "Content-Type: application/json" \
  -d '{"plate": "B1234ZZP"}'
```

---

## 🔄 Integration with OCR Systems

### **Supported OCR Outputs**
The API now seamlessly handles license plate recognition outputs:

| OCR Output | API Response | Institution |
|------------|--------------|-------------|
| `"50072-00"` | Military plate analysis | Markas Besar TNI |
| `"1234-01"` | Military plate analysis | TNI AD |
| `"5678-V"` | Military plate analysis | TNI AD |
| `"B 1234 ABC"` | Standard validation | Database lookup |
| `"D5678ZZP"` | Institution validation | POLRI |

### **Error Handling for OCR Integration**
```javascript
async function processPlateFromOCR(plateText) {
  try {
    const response = await fetch(`https://samsat-api-v1.zeabur.app/check-plate?plate=${plateText}`);
    
    if (response.status === 200) {
      const data = await response.json();
      
      // Handle different response types
      if (data.status === "Format plat militer lama terdeteksi") {
        return {
          type: "military",
          institution: data.institution,
          valid: true,
          era: "old_format"
        };
      } else if (data.status === "Plat sudah terdaftar") {
        return {
          type: "standard",
          region: data.plate_region.province,
          valid: true,
          era: "current"
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
    return {
      type: "error",
      valid: false,
      message: error.message
    };
  }
}
```

---

## 🔒 Rate Limiting
Currently, there are no rate limits implemented. However, please use the API responsibly and avoid excessive requests.

---

## 🐛 Error Handling
The API returns appropriate HTTP status codes and error messages. Always check the status code and handle errors gracefully in your application.

**Common Error Patterns:**
```javascript
const response = await fetch('https://samsat-api-v1.zeabur.app/check-plate?plate=50072-00');

if (response.status === 404) {
  // Plate not found (for standard plates only)
  const error = await response.json();
  console.log(error.message); // "Plat tidak terdaftar"
} else if (response.status === 400) {
  // Bad request
  const error = await response.json();
  console.log(error.error); // "Plate number is required"
} else if (response.status === 200) {
  // Success (including old military format)
  const data = await response.json();
  
  if (data.status === "Format plat militer lama terdeteksi") {
    console.log("Old military format detected:", data.institution);
  } else {
    console.log("Standard plate found:", data.jenis_kendaraan);
  }
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
