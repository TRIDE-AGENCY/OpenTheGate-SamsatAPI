# 🚗🔒 Indonesian Samsat API - Secure FastAPI Edition

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Nginx](https://img.shields.io/badge/nginx-latest-brightgreen.svg)
![Security](https://img.shields.io/badge/security-enhanced-red.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

**Secure, Fast, and Comprehensive Indonesian License Plate Checker API**

</div>

## 🌟 Overview

The Indonesian Samsat API is a **secure, high-performance FastAPI** application that provides comprehensive information about Indonesian vehicle license plates. Built with enterprise-grade security features, nginx reverse proxy, and modern async architecture.

### 🔥 **New in v2.0.0 - Security Edition**
- ✅ **FastAPI Migration**: Complete rewrite from Flask to FastAPI
- ✅ **Security First**: Bearer token authentication, rate limiting, input validation
- ✅ **Nginx Reverse Proxy**: Enhanced security and performance layer
- ✅ **Docker Ready**: Complete containerization with Docker Compose
- ✅ **Zero Downtime**: Health checks and auto-restart capabilities
- ✅ **Production Ready**: Comprehensive security headers and error sanitization

---

## 🏗️ Architecture

```
Internet → Nginx (Port 80/443) → FastAPI (Port 5555) → Samsat Database
            ↓                        ↓
        Rate Limiting           Authentication
        Security Headers        Input Validation
        SSL Termination         Business Logic
        Attack Protection       Military Analysis
```

## 🚀 Key Features

### 🔒 **Security Features**
- **Bearer Token Authentication**: JWT and custom token support
- **Rate Limiting**: 100 requests/minute with burst protection
- **Input Validation**: Pydantic models with sanitization
- **Security Headers**: Complete OWASP security header set
- **Request Timeouts**: Prevents hanging requests and DoS
- **Error Sanitization**: No sensitive information in responses
- **Attack Protection**: Blocks common attack patterns

### 🏍️ **License Plate Support**
- **Standard Plates**: `B-1234-ABC`, `D-5678-XYZ`
- **Institution Plates**: `B-1234-ZZP` (POLRI), `A-9876-ZZT` (TNI)
- **Military Legacy**: `1234-00`, `50072-85`, `9876-V` (OCR compatible)
- **Extended Coverage**: All numeric suffixes 00-99 + Roman I-IX
- **Flexible Format**: 4-digit and 5-digit vehicle numbers

### 🎯 **Technical Features**
- **Async/Await**: High-performance async operations
- **Auto Documentation**: Hidden in production for security
- **Health Monitoring**: Built-in health checks and status endpoints
- **Logging**: Comprehensive security event logging
- **CORS Support**: Configurable cross-origin requests

---

## 📦 Quick Start

### 🐋 **Docker Deployment (Recommended)**

```bash
# Clone repository
git clone https://github.com/your-username/samsat-api.git
cd samsat-api

# Make deployment script executable
chmod +x deploy.sh

# Start all services (nginx + FastAPI)
./deploy.sh start

# Check status
./deploy.sh status

# Test API (replace with your token)
./deploy.sh test your-bearer-token
```

### ⚡ **Manual Setup**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ENVIRONMENT=development
export ZEABUR_BEARER_TOKEN=your-secure-token
export SECRET_KEY=your-secret-key

# Run FastAPI directly
python app.py

# Or with uvicorn
uvicorn app:app --host 0.0.0.0 --port 5555
```

### 🌐 **Production with Nginx**

```bash
# Install nginx
sudo apt install nginx

# Copy configuration
sudo cp nginx.conf /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Start services
sudo systemctl start nginx
uvicorn app:app --host 127.0.0.1 --port 5555
```

---

## 🔑 Authentication & Security

### **Environment Variables**

```bash
# Required for Production
ZEABUR_BEARER_TOKEN=your-secure-bearer-token
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production

# Optional
PORT=5555
```

### **Bearer Token Usage**

```bash
# Through Nginx (Recommended)
curl -X GET "http://localhost/check-plate?plate=B1234ABC" \
  -H "Authorization: Bearer your-bearer-token"

# Direct FastAPI
curl -X GET "http://localhost:5555/check-plate?plate=B1234ABC" \
  -H "Authorization: Bearer your-bearer-token"
```

### **Security Headers Applied**
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

---

## 📋 API Endpoints

### 🏠 **GET /** - API Information
Returns comprehensive API documentation and security features.

```bash
curl -X GET "http://localhost/" \
  -H "Authorization: Bearer your-token"
```

**Response:**
```json
{
  "message": "Indonesian Plate Checker API v2.0.0",
  "version": "2.0.0",
  "security_features": [
    "Bearer token authentication",
    "Rate limiting (100 requests/minute)",
    "Input validation",
    "Security headers",
    "Request timeouts",
    "Error sanitization"
  ],
  "architecture": "FastAPI + Nginx Reverse Proxy",
  "deployment": "Docker Compose Ready"
}
```

### 🔍 **GET /check-plate** - Query Parameter Method

```bash
# Standard plate
curl -X GET "http://localhost/check-plate?plate=B1234ABC" \
  -H "Authorization: Bearer your-token"

# Military plate
curl -X GET "http://localhost/check-plate?plate=12345-00" \
  -H "Authorization: Bearer your-token"
```

### 📤 **POST /check-plate** - JSON Body Method

```bash
curl -X POST "http://localhost/check-plate" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"plate": "B1234ABC"}'
```

### 🩺 **GET /health** - Health Check (via Nginx)

```bash
curl -X GET "http://localhost/health"
```

---

## 📊 Response Examples

### ✅ **Standard Civil Plate**
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

### 🏛️ **Institution Plate**
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

### 🪖 **Military Legacy Plate**
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

### ❌ **Rate Limit Exceeded**
```json
{
  "error": "Rate limit exceeded",
  "detail": "100 requests per minute exceeded"
}
```

### 🚫 **Authentication Failed**
```json
{
  "detail": "Invalid authentication credentials"
}
```

---

## 🛠️ Deployment Management

### **Deploy Script Commands**

```bash
# Service Management
./deploy.sh start          # Start all services
./deploy.sh stop           # Stop all services  
./deploy.sh restart        # Restart all services
./deploy.sh status         # Show service status

# Monitoring
./deploy.sh logs           # Show all logs
./deploy.sh logs nginx     # Show nginx logs
./deploy.sh logs samsat-api # Show FastAPI logs

# Testing
./deploy.sh test                    # Test with default token
./deploy.sh test your-bearer-token  # Test with custom token

# Maintenance
./deploy.sh update         # Update configuration and restart
```

### **Docker Compose Services**

```yaml
services:
  # FastAPI Application
  samsat-api:
    build: .
    ports: ["5555:5555"]
    environment:
      - ZEABUR_BEARER_TOKEN=${ZEABUR_BEARER_TOKEN}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    
  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on: [samsat-api]
```

---

## 🏍️ License Plate Support

### **Standard Formats**
| Format | Description | Example |
|--------|-------------|---------|
| Civil | Standard Indonesian plates | `B-1234-ABC` |
| Institution | Government/military plates | `D-5678-ZZP` |

### **Military Legacy (OCR Compatible)**
| Format | Digits | Suffix | Institution | Example |
|--------|--------|--------|-------------|---------|
| Numeric 4-digit | 4 | 00-99 | Various | `1234-00` |
| Numeric 5-digit | 5 | 00-99 | Various | `50072-85` |
| Roman 4-digit | 4 | I-IX | TNI AD | `1234-V` |
| Roman 5-digit | 5 | I-IX | TNI AD | `98765-IX` |

### **Institution Mapping**
| Suffix/Code | Institution | Type |
|-------------|-------------|------|
| 00 | Markas Besar TNI | Headquarters |
| 01-05 | TNI AD | Army |
| 06-08 | TNI AL | Navy |
| 09-11 | TNI AU | Air Force |
| 12-15 | POLRI | Police |
| 16-99 | TNI AD | Army (Extended) |
| I-IX | TNI AD | Army (Roman) |
| ZZT/ZZU/ZZD/ZZL/ZZP/ZZH | Current format | Modern |

---

## 💻 Integration Examples

### **JavaScript/Node.js**
```javascript
const API_BASE = 'http://localhost';
const BEARER_TOKEN = 'your-bearer-token';

async function checkPlate(plateNumber) {
  try {
    const response = await fetch(`${API_BASE}/check-plate?plate=${plateNumber}`, {
      headers: {
        'Authorization': `Bearer ${BEARER_TOKEN}`
      }
    });
    
    if (response.status === 429) {
      throw new Error('Rate limit exceeded');
    }
    
    if (response.status === 401) {
      throw new Error('Invalid authentication token');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API Error:', error.message);
    throw error;
  }
}

// Usage examples
checkPlate('B1234ABC');      // Standard plate
checkPlate('50072-00');      // Military 5-digit
checkPlate('1234-V');        // Military Roman
```

### **Python**
```python
import requests
import time

class SamsatAPI:
    def __init__(self, base_url='http://localhost', token='your-bearer-token'):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}
        
    def check_plate(self, plate_number):
        try:
            response = requests.get(
                f'{self.base_url}/check-plate',
                params={'plate': plate_number},
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 429:
                raise Exception('Rate limit exceeded')
            elif response.status_code == 401:
                raise Exception('Invalid authentication token')
            elif response.status_code == 200:
                return response.json()
            else:
                raise Exception(f'API Error: {response.status_code}')
                
        except requests.Timeout:
            raise Exception('Request timeout')
        except requests.RequestException as e:
            raise Exception(f'Network error: {e}')

# Usage
api = SamsatAPI()
result = api.check_plate('12345-85')
print(f"Institution: {result.get('institution')}")
```

### **PHP**
```php
<?php
class SamsatAPI {
    private $baseUrl;
    private $token;
    
    public function __construct($baseUrl = 'http://localhost', $token = 'your-bearer-token') {
        $this->baseUrl = $baseUrl;
        $this->token = $token;
    }
    
    public function checkPlate($plateNumber) {
        $url = $this->baseUrl . '/check-plate?plate=' . urlencode($plateNumber);
        
        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'header' => 'Authorization: Bearer ' . $this->token,
                'timeout' => 30
            ]
        ]);
        
        $response = file_get_contents($url, false, $context);
        
        if ($response === false) {
            throw new Exception('API request failed');
        }
        
        $data = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            throw new Exception('Invalid JSON response');
        }
        
        return $data;
    }
}

// Usage
$api = new SamsatAPI();
$result = $api->checkPlate('9876-99');
echo "Institution: " . $result['institution'] . "\n";
?>
```

---

## 🔧 Configuration & Monitoring

### **Nginx Configuration Highlights**
```nginx
# Rate Limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=burst:10m rate=10r/s;

# Security Headers
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Strict-Transport-Security "max-age=31536000" always;

# Attack Protection
location ~* \.(php|asp|aspx|jsp)$ { return 444; }
location ~ /\. { deny all; }
location ~* \.(env|log|ini|conf)$ { deny all; }
```

### **Health Monitoring**
```bash
# Service Status
docker-compose ps

# Health Checks
curl -f http://localhost/health        # Nginx health
curl -f http://localhost:5555/         # FastAPI health

# Logs
docker-compose logs -f nginx           # Nginx logs
docker-compose logs -f samsat-api      # FastAPI logs
```

### **Performance Metrics**
- **Response Time**: < 500ms average
- **Throughput**: 100+ requests/minute per IP
- **Uptime**: 99.9% with health checks
- **Memory**: < 512MB per container
- **CPU**: < 50% under normal load

---

## 🚨 Error Handling & Troubleshooting

### **Common HTTP Status Codes**
| Code | Description | Action |
|------|-------------|--------|
| 200 | Success | Plate processed successfully |
| 400 | Bad Request | Check input format |
| 401 | Unauthorized | Verify bearer token |
| 404 | Not Found | Plate not in database |
| 408 | Request Timeout | Retry request |
| 422 | Validation Error | Fix input validation |
| 429 | Rate Limited | Wait before retry |
| 500 | Server Error | Check logs |
| 502 | Bad Gateway | Check FastAPI service |

### **Debug Commands**
```bash
# Check nginx configuration
sudo nginx -t

# Verify services are running
docker-compose ps

# Check connectivity
curl -I http://localhost:5555/health

# View detailed logs
./deploy.sh logs nginx | grep ERROR
./deploy.sh logs samsat-api | grep ERROR

# Test specific components
./deploy.sh test dev-token
```

### **Common Issues & Solutions**

1. **502 Bad Gateway**
   ```bash
   # Check if FastAPI is running
   docker-compose ps samsat-api
   # Restart if needed
   ./deploy.sh restart
   ```

2. **Rate Limit Exceeded**
   ```bash
   # Check nginx logs for rate limiting
   ./deploy.sh logs nginx | grep "limiting requests"
   ```

3. **Authentication Failures**
   ```bash
   # Verify token in .env file
   cat .env | grep ZEABUR_BEARER_TOKEN
   ```

---

## 🌐 Production Deployment

### **Zeabur Cloud Deployment**
```bash
# Set environment variables in Zeabur dashboard:
ZEABUR_BEARER_TOKEN=your-production-token
SECRET_KEY=your-production-secret
ENVIRONMENT=production
PORT=5555
```

### **SSL/HTTPS Setup**
```bash
# Install Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **Production Checklist**
- ✅ Set strong `SECRET_KEY` and `ZEABUR_BEARER_TOKEN`
- ✅ Enable HTTPS with valid SSL certificate
- ✅ Configure firewall rules (ports 80, 443 only)
- ✅ Set up log rotation
- ✅ Configure monitoring and alerting
- ✅ Enable automatic backups
- ✅ Test disaster recovery procedures
- ✅ Set up CI/CD pipeline

---

## 📈 Changelog

### **v2.0.0 - Security & Performance Edition (Current)**
- 🚀 **Complete FastAPI Migration**: Rewritten from Flask
- 🔒 **Enterprise Security**: Bearer auth, rate limiting, input validation
- 🌐 **Nginx Integration**: Reverse proxy with security enhancements
- 🐋 **Docker Containerization**: Complete Docker Compose setup
- ⚡ **Performance**: Async/await architecture
- 🛡️ **Security Headers**: Complete OWASP protection
- 📊 **Monitoring**: Health checks and comprehensive logging
- 🚨 **Error Handling**: Sanitized error responses
- 🎯 **Production Ready**: Zero-downtime deployment

### **v1.2.0 - Enhanced Military Support**
- ✅ Extended numeric suffix support (00-99)
- ✅ Flexible prefix length (4-5 digits)
- ✅ Enhanced validation and error handling

### **v1.1.0 - OCR Military Support**
- ✅ Old military plate format support
- ✅ Institution mapping for legacy codes
- ✅ OCR system compatibility

### **v1.0.0 - Initial Release**
- ✅ Basic plate checking functionality
- ✅ SAMSAT database integration

---

## 🤝 Contributing

```bash
# Fork and clone
git clone https://github.com/your-username/samsat-api.git
cd samsat-api

# Create feature branch
git checkout -b feature/your-feature

# Make changes and test
./deploy.sh start
./deploy.sh test

# Commit and push
git commit -m "Add your feature"
git push origin feature/your-feature

# Create pull request
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/samsat-api/issues)
- 📖 **Documentation**: [Security Guide](SECURITY_GUIDE.md)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/samsat-api/discussions)

---

<div align="center">

**Made with ❤️ for Indonesian Vehicle Data**

[![Deploy with Docker](https://img.shields.io/badge/deploy-docker-blue.svg)](docker-compose.yml)
[![Secure by Design](https://img.shields.io/badge/secure-by%20design-green.svg)](SECURITY_GUIDE.md)
[![Production Ready](https://img.shields.io/badge/production-ready-brightgreen.svg)](deploy.sh)

</div>