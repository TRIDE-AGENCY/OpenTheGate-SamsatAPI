# 🚗 Indonesian Plate Checker API Documentation

## Overview

The Indonesian Plate Checker API provides comprehensive information about Indonesian vehicle license plates. It validates plate formats, queries the official Samsat database, and provides detailed analysis including vehicle type classification and regional information.

**Base URL:** `https://samsat-api.zeabur.app`

---

## 🎯 Features

- **Plate Validation**: Supports standard Indonesian plate format (XX-XXXX-XXX)
- **Vehicle Classification**: Automatic vehicle type detection based on police identity number
- **Institution Detection**: Identifies government/military institution plates
- **Regional Information**: Province, city, Samsat office, and address details
- **Format Recognition**: Detects and provides informative responses for non-standard formats

---

## 📋 Supported Formats

### ✅ **Supported by Database**
- **Standard Civil Plates**: `B-1234-ABC`, `D-5678-XYZ`
- **Institution Plates**: `B-1234-ZZP`, `A-9876-ZZT`

### ❌ **Recognized but Not in Database**
- **State Agency**: `RI-1`, `RI-12`
- **Diplomatic**: `CD-12-34`, `CC-56-78`
- **Old Military**: `1234-00`, `5678-V`

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
  "message": "Indonesian Plate Checker API",
  "database_support": "Hanya mendukung format plat standar Indonesia (XX-XXXX-XXX)",
  "supported_format": "XX-XXXX-XXX (e.g., B-1234-ABC, D-5678-ZZP)",
  "features": {
    "vehicle_classification": "Berdasarkan nomor identitas polisi (1-1999: Mobil, 2000-6999: Motor, 7000-7999: Bus, 8000-9999: Kendaraan Berat)",
    "plate_type": "Sipil atau Institusi (ZZT/ZZU/ZZD/ZZL/ZZP/ZZH)",
    "region_info": "Informasi provinsi, kota, kantor Samsat, dan alamat"
  },
  "endpoints": {
    "GET /check-plate?plate=B1234ABC": "Check plate via query parameter",
    "POST /check-plate": "Check plate via JSON body {'plate': 'B1234ABC'}"
  }
}
```

### 2. **GET /check-plate** - Check Plate (Query Parameter)
Checks a license plate using query parameter.

**Request:**
```http
GET /check-plate?plate=B1234ABC
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plate` | string | Yes | License plate number (with or without hyphens) |

**Example:**
```bash
curl "https://samsat-api.zeabur.app/check-plate?plate=B1234ABC"
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
curl -X POST https://samsat-api.zeabur.app/check-plate \
  -H "Content-Type: application/json" \
  -d '{"plate": "B1234ABC"}'
```

---

## 📤 Response Examples

### ✅ **Standard Civil Plate Found**
**Request:** `B2345ABC`

```json
{
  "status": "Plat sudah terdaftar di Samsat",
  "jenis_kendaraan": "Motor",
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
  "status": "Plat sudah terdaftar di Samsat",
  "jenis_kendaraan": "Mobil - Kendaraan Penumpang",
  "jenis_plat_nomor": "Institusi - POLRI",
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

### ❌ **Standard Plate Not Found**
**Request:** `X9999ZZZ`

```json
{
  "message": "Plat nomor tersebut tidak tersedia"
}
```

### 🚫 **Non-Standard Format (State Agency)**
**Request:** `RI-1`

```json
{
  "message": "Format plat dinas negara tidak didukung oleh database Samsat",
  "jenis_plat_nomor": "Dinas Negara",
  "note": "Database hanya mendukung format plat standar (XX-XXXX-XXX)"
}
```

### 🌐 **Non-Standard Format (Diplomatic)**
**Request:** `CD-12-34`

```json
{
  "message": "Format plat diplomatik tidak didukung oleh database Samsat",
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
| 1-1999 | Mobil - Kendaraan Penumpang |
| 2000-6999 | Motor |
| 7000-7999 | Bus |
| 8000-9999 | Kendaraan Berat |

### 🏛️ **Institution Codes**
Based on `kode_khusus` (suffix):

| Code | Institution |
|------|-------------|
| ZZT | Markas Besar TNI |
| ZZU | TNI AU |
| ZZD | TNI AD |
| ZZL | TNI AL |
| ZZP | POLRI |
| ZZH | Kementrian / Lembaga Negara |

### 🏷️ **Plate Type**
- **Sipil**: Regular civilian plates
- **Institusi**: Government/military institution plates

---

## 🔧 HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success - Plate found and analyzed |
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

#### **Success Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Registration status message |
| `jenis_kendaraan` | string | Vehicle type classification |
| `jenis_plat_nomor` | string | Plate type (Civil/Institution) |
| `plate_analysis` | object | Detailed plate breakdown |
| `plate_analysis.kode_wilayah` | string | Regional code |
| `plate_analysis.nomor_identitas_polisi` | number | Police identity number |
| `plate_analysis.kode_khusus` | string | Special/suffix code |
| `plate_region` | object | Regional information |
| `plate_region.province` | string | Province name |
| `plate_region.city` | string | City name |
| `plate_region.samsat_office` | string | Samsat office name |
| `plate_region.address` | string | Complete address |

#### **Error Response Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `error` | string | Error message |
| `message` | string | User-friendly message |

---

## 💡 Usage Examples

### **JavaScript/Node.js**
```javascript
// GET method
const response = await fetch('https://samsat-api.zeabur.app/check-plate?plate=B1234ABC');
const data = await response.json();
console.log(data);

// POST method
const response = await fetch('https://samsat-api.zeabur.app/check-plate', {
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

# GET method
response = requests.get('https://samsat-api.zeabur.app/check-plate?plate=B1234ABC')
data = response.json()
print(data)

# POST method
response = requests.post('https://samsat-api.zeabur.app/check-plate', 
                        json={'plate': 'B1234ABC'})
data = response.json()
print(data)
```

### **PHP**
```php
// GET method
$response = file_get_contents('https://samsat-api.zeabur.app/check-plate?plate=B1234ABC');
$data = json_decode($response, true);
print_r($data);

// POST method
$data = json_encode(['plate' => 'B1234ABC']);
$context = stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/json',
        'content' => $data
    ]
]);
$response = file_get_contents('https://samsat-api.zeabur.app/check-plate', false, $context);
$data = json_decode($response, true);
print_r($data);
```

### **cURL**
```bash
# GET method
curl "https://samsat-api.zeabur.app/check-plate?plate=B1234ABC"

# POST method
curl -X POST https://samsat-api.zeabur.app/check-plate \
  -H "Content-Type: application/json" \
  -d '{"plate": "B1234ABC"}'
```

---

## 🔒 Rate Limiting
Currently, there are no rate limits implemented. However, please use the API responsibly and avoid excessive requests.

---

## 🐛 Error Handling
The API returns appropriate HTTP status codes and error messages. Always check the status code and handle errors gracefully in your application.

**Common Error Patterns:**
```javascript
const response = await fetch('https://samsat-api.zeabur.app/check-plate?plate=B1234ABC');

if (response.status === 404) {
  // Plate not found
  const error = await response.json();
  console.log(error.message); // "Plat nomor tersebut tidak tersedia"
} else if (response.status === 400) {
  // Bad request
  const error = await response.json();
  console.log(error.error); // "Plate number is required"
} else if (response.status === 200) {
  // Success
  const data = await response.json();
  console.log(data);
}
```

---

## 📞 Support
For API support or questions, please refer to the API home endpoint for the most current information.

---

## 📄 License
This API is provided for educational and development purposes. Please ensure compliance with applicable laws and regulations when using vehicle registration data.
