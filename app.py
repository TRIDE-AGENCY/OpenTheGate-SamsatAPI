from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import asyncio
import httpx
import re
import json
import logging
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

# Configure logging to hide sensitive information
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = None  # No expiration for development

# Bearer token for Zeabur cloud deployment
ZEABUR_BEARER_TOKEN = os.getenv("ZEABUR_BEARER_TOKEN", "dev-token")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app - Documentation hidden completely
app = FastAPI(
    title="Indonesian Plate Checker API",
    description="Secure API for checking Indonesian license plates with institution support & OCR military compatibility",
    version="2.0.0",
    docs_url=None,  # Hide Swagger UI completely
    redoc_url=None  # Hide ReDoc completely
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure allowed hosts in production
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure specific origins in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# Request timeout middleware
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        # Set timeout for requests (30 seconds)
        return await asyncio.wait_for(call_next(request), timeout=30.0)
    except asyncio.TimeoutError:
        logger.warning(f"Request timeout for {request.url}")
        return JSONResponse(
            status_code=408,
            content={"error": "Request timeout"}
        )

# Pydantic models for input validation
class PlateRequest(BaseModel):
    plate: str = Field(..., min_length=1, max_length=20, description="License plate number")
    
    @validator('plate')
    def validate_plate(cls, v):
        if not v or not v.strip():
            raise ValueError('Plate number cannot be empty')
        # Remove potentially dangerous characters
        cleaned = re.sub(r'[^\w\-\s]', '', v.strip())
        if len(cleaned) == 0:
            raise ValueError('Invalid plate format')
        return cleaned

class TokenData(BaseModel):
    username: Optional[str] = None

# Security schemes
security = HTTPBearer()

print("=== FASTAPI APP STARTING WITH INSTITUTION SUPPORT & OCR MILITARY COMPATIBILITY ===")

class IndonesianPlateChecker:
    def __init__(self):
        self.base_url = "https://firestore.googleapis.com/v1/projects/informasisamsat/databases/(default)/documents"
        
        # Institution codes for suffix
        self.institution_codes = {
            'ZZT': 'Markas Besar TNI',
            'ZZU': 'TNI AU',
            'ZZD': 'TNI AD',
            'ZZL': 'TNI AL',
            'ZZP': 'POLRI',
            'ZZH': 'Kementrian / Lembaga Negara'
        }
        
        # Valid military suffixes - includes Roman numerals I-IX only
        self.VALID_NUMERIC_SUFFIXES = {'00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', 
                                     '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
                                     '21', '22', '23', '24', '25', '26', '27', '28', '29', '30',
                                     '31', '32', '33', '34', '35', '36', '37', '38', '39', '40',
                                     '41', '42', '43', '44', '45', '46', '47', '48', '49', '50',
                                     '51', '52', '53', '54', '55', '56', '57', '58', '59', '60',
                                     '61', '62', '63', '64', '65', '66', '67', '68', '69', '70',
                                     '71', '72', '73', '74', '75', '76', '77', '78', '79', '80',
                                     '81', '82', '83', '84', '85', '86', '87', '88', '89', '90',
                                     '91', '92', '93', '94', '95', '96', '97', '98', '99'}
        
        self.VALID_ROMAN_SUFFIXES = {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX'}
        
        # Enhanced military suffix mapping for old format conversion
        self.military_suffix_mapping = {}
        
        # Map numeric suffixes (00-99) to appropriate institutions
        for suffix in self.VALID_NUMERIC_SUFFIXES:
            if suffix == '00':
                self.military_suffix_mapping[suffix] = 'ZZT'  # TNI Headquarters
            elif suffix in ['01', '02', '03', '04', '05']:
                self.military_suffix_mapping[suffix] = 'ZZD'  # TNI Army
            elif suffix in ['06', '07', '08']:
                self.military_suffix_mapping[suffix] = 'ZZL'  # TNI Navy
            elif suffix in ['09', '10', '11']:
                self.military_suffix_mapping[suffix] = 'ZZU'  # TNI Air Force
            elif suffix in ['12', '13', '14', '15']:
                self.military_suffix_mapping[suffix] = 'ZZP'  # POLRI
            else:
                # Default other suffixes to TNI Army
                self.military_suffix_mapping[suffix] = 'ZZD'
        
        # Map Roman numerals to TNI Army (traditional usage)
        for roman in self.VALID_ROMAN_SUFFIXES:
            self.military_suffix_mapping[roman] = 'ZZD'
        
        logger.info(f"Institution codes loaded: {self.institution_codes}")
        logger.info(f"Valid numeric suffixes: {len(self.VALID_NUMERIC_SUFFIXES)} suffixes (00-99)")
        logger.info(f"Valid Roman suffixes: {self.VALID_ROMAN_SUFFIXES}")
        logger.info(f"Military suffix mapping loaded: {len(self.military_suffix_mapping)} mappings")
    
    async def check_plate(self, plate_number: str) -> Dict[str, Any]:
        logger.info(f"=== CHECKING PLATE: {plate_number} ===")
        # Clean the plate number
        plate_clean = plate_number.replace('-', '').replace(' ', '').upper()
        
        # Check if it's an old military format from OCR
        if self.is_old_military_format(plate_number):
            return self.handle_old_military_plate(plate_number)
        # Check if it's a standard plate format that the database supports
        elif self.is_standard_plate(plate_clean):
            return await self.check_standard_plate(plate_clean)
        else:
            return self.analyze_non_standard_plate(plate_number)
    
    def is_old_military_format(self, plate: str) -> bool:
        """Check if plate matches old military format from OCR: XXXXX-XX, XXXX-XX, XXXXX-X, or XXXX-X"""
        plate_clean = plate.replace(' ', '').upper()
        
        # Check for numeric suffixes (00-99)
        numeric_pattern = r'^(\d{4,5})-(\d{2})$'  # 4 or 5 digits + 2 digit suffix
        numeric_match = re.match(numeric_pattern, plate_clean)
        if numeric_match:
            suffix = numeric_match.group(2)
            if suffix in self.VALID_NUMERIC_SUFFIXES:
                logger.info(f"DETECTED OLD MILITARY FORMAT (NUMERIC): {plate_clean}")
                return True
        
        # Check for Roman numeral suffixes (I-IX)
        roman_pattern = r'^(\d{4,5})-(I|II|III|IV|V|VI|VII|VIII|IX)$'  # 4 or 5 digits + Roman numeral
        roman_match = re.match(roman_pattern, plate_clean)
        if roman_match:
            suffix = roman_match.group(2)
            if suffix in self.VALID_ROMAN_SUFFIXES:
                logger.info(f"DETECTED OLD MILITARY FORMAT (ROMAN): {plate_clean}")
                return True
        
        return False
    
    def handle_old_military_plate(self, plate: str) -> Dict[str, Any]:
        """Convert old military format to analyzable format and provide detailed info"""
        plate_clean = plate.replace(' ', '').upper()
        logger.info(f"PROCESSING OLD MILITARY PLATE: {plate_clean}")
        
        # Extract number and suffix
        if '-' in plate_clean:
            number_part, suffix_part = plate_clean.split('-', 1)
        else:
            return {"error": "Invalid military plate format"}
        
        # Validate number part (must be 4 or 5 digits)
        if not re.match(r'^\d{4,5}$', number_part):
            return {
                "error": f"Invalid number format: {number_part}",
                "note": "Nomor kendaraan harus 4 atau 5 digit"
            }
        
        # Validate suffix part
        if suffix_part not in self.VALID_NUMERIC_SUFFIXES and suffix_part not in self.VALID_ROMAN_SUFFIXES:
            return {
                "error": f"Invalid military suffix: {suffix_part}",
                "note": f"Suffix harus berupa angka 00-99 atau angka Romawi I-IX",
                "valid_suffixes": {
                    "numeric": "00-99",
                    "roman": "I, II, III, IV, V, VI, VII, VIII, IX"
                }
            }
        
        # Map suffix to institution
        institution_code = self.military_suffix_mapping.get(suffix_part)
        institution_name = self.institution_codes.get(institution_code) if institution_code else None
        
        if not institution_name:
            return {
                "error": f"Unknown military suffix mapping: {suffix_part}",
                "note": "Suffix tidak dapat dipetakan ke institusi yang dikenal"
            }
        
        # Determine vehicle type based on number (military classification)
        vehicle_type = self.get_military_vehicle_type(number_part)
        
        # Determine suffix type
        suffix_type = "Angka Romawi" if suffix_part in self.VALID_ROMAN_SUFFIXES else "Numerik"
        
        # Create comprehensive response for old military plates
        result = {
            "status": "Format plat militer lama terdeteksi",
            "original_plate": plate,
            "jenis_kendaraan": vehicle_type,
            "jenis_plat_nomor": "Dinas TNI dan POLRI",
            "institution": institution_name,
            "military_analysis": {
                "nomor_kendaraan": number_part,
                "kode_institusi": suffix_part,
                "tipe_suffix": suffix_type,
                "institution_code": institution_code,
                "digit_count": len(number_part)
            }
        }
        
        logger.info(f"OLD MILITARY RESULT: {result}")
        return result
    
    def get_military_vehicle_type(self, number_part: str) -> str:
        """Simple military vehicle classification - returns only 'Kendaraan Militer'"""
        return "Kendaraan Militer"
    
    def is_standard_plate(self, plate_clean: str) -> bool:
        # Check if it matches XX-XXXX-XXX format (without hyphens: XXXXXXXX)
        pattern = r'^[A-Z]+\d+[A-Z]+$'
        return bool(re.match(pattern, plate_clean))
    
    async def check_standard_plate(self, plate_clean: str) -> Dict[str, Any]:
        prefix, middle, suffix = self.parse_standard_plate(plate_clean)
        logger.info(f"PARSED: prefix={prefix}, middle={middle}, suffix={suffix}")
        
        if not prefix or middle is None or not suffix:
            return {"error": "Invalid standard plate format"}
        
        # Use only the last letter of suffix for API call (as per original logic)
        suffix_for_api = suffix[-1]
        url = f"{self.base_url}/nopol/{prefix}/belakang/{suffix_for_api}"
        logger.info(f"API URL: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    result = self.format_response(response.json())
                    if "error" not in result:
                        # Create plate_analysis with exact order as a regular dict
                        plate_analysis = {}
                        plate_analysis["kode_wilayah"] = prefix
                        plate_analysis["nomor_identitas_polisi"] = middle
                        plate_analysis["kode_khusus"] = suffix
                        
                        # Build final response as regular dict
                        ordered_result = {}
                        ordered_result["status"] = "Plat sudah terdaftar"
                        ordered_result["jenis_kendaraan"] = self.get_vehicle_type(middle)
                        ordered_result["jenis_plat_nomor"] = self.get_plate_type(suffix)
                        
                        # CRITICAL: Add institution field
                        institution_name = self.get_institution_name(suffix)
                        logger.info(f"INSTITUTION CHECK: suffix='{suffix}' -> institution='{institution_name}'")
                        
                        if institution_name:
                            ordered_result["institution"] = institution_name
                            logger.info(f"ADDED INSTITUTION FIELD: {institution_name}")
                        else:
                            logger.info("NO INSTITUTION FOUND")
                        
                        ordered_result["plate_analysis"] = plate_analysis
                        ordered_result["plate_region"] = result["plate_region"]
                        
                        logger.info(f"FINAL RESULT KEYS: {list(ordered_result.keys())}")
                        return ordered_result
                    return result
                else:
                    return {"error": f"Plate not found: {response.status_code}"}
        except httpx.TimeoutException:
            logger.error("External API timeout")
            return {"error": "Service temporarily unavailable"}
        except Exception as e:
            logger.error(f"External API error: {str(e)}")
            return {"error": "Service error"}
    
    def parse_standard_plate(self, plate_clean: str):
        # Parse XXXXXXXX format (e.g., B1234ABC -> B, 1234, ABC)
        pattern = r'^([A-Z]+)(\d+)([A-Z]+)$'
        match = re.match(pattern, plate_clean)
        if match:
            prefix = match.group(1)
            middle = int(match.group(2))
            suffix = match.group(3)
            return prefix, middle, suffix
        return None, None, None
    
    def get_vehicle_type(self, middle_number: int) -> str:
        if 1 <= middle_number <= 1999:
            return "Mobil Penumpang"
        elif 2000 <= middle_number <= 6999:
            return "Sepeda Motor"
        elif 7000 <= middle_number <= 7999:
            return "Mobil Bus"
        elif 8000 <= middle_number <= 8999:
            return "Mobil Barang"
        elif 9000 <= middle_number <= 9999:
            return "Kendaraan Khusus"
        else:
            return "Tidak Diketahui"
    
    def get_plate_type(self, suffix: str) -> str:
        if suffix in self.institution_codes:
            return "Dinas TNI dan POLRI" 
        else:
            return "Sipil"
    
    def get_institution_name(self, suffix: str) -> Optional[str]:
        result = self.institution_codes.get(suffix, None)
        logger.info(f"get_institution_name('{suffix}') = '{result}'")
        return result
    
    def analyze_non_standard_plate(self, plate: str) -> Dict[str, Any]:
        plate_upper = plate.upper().replace('-', '').replace(' ', '')
        
        # State agency: RI format
        if re.match(r'^RI\d*$', plate_upper):
            return {
                "message": "Format plat dinas negara tidak didukung oleh database",
                "jenis_plat_nomor": "Dinas Pemerintah", 
                "note": "Database hanya mendukung format plat standar (XX-XXXX-XXX)"
            }
        
        # Diplomatic: CC/CD/CN/CS format
        elif re.match(r'^(CC|CD|CN|CS)\d*$', plate_upper):
            return {
                "message": "Format plat diplomatik tidak didukung oleh database", 
                "jenis_plat_nomor": "Diplomatik",
                "note": "Database hanya mendukung format plat standar (XX-XXXX-XXX)"
            }
        
        else:
            return {"error": "Format plat nomor tidak valid atau tidak didukung"}
    
    def parse_plate(self, plate: str):
        # Legacy method for backward compatibility
        pattern = r'^([A-Z]+)\d+([A-Z]+)$'
        match = re.match(pattern, plate.upper())
        if match:
            return match.group(1), match.group(2)[-1]
        return None, None
    
    def format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if 'fields' not in data:
            return {"error": "Invalid response format"}
        
        fields = data['fields']
        return {
            'plate_region': {
                'province': fields.get('Provinsi', {}).get('stringValue', ''),
                'city': fields.get('Daerah', {}).get('stringValue', ''),
                'samsat_office': fields.get('Samsat', {}).get('stringValue', ''),
                'address': fields.get('Alamat', {}).get('stringValue', '')
            }
        }

# Initialize the checker
checker = IndonesianPlateChecker()

# Authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # No expiration for development
    if ACCESS_TOKEN_EXPIRE_MINUTES:
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header"""
    try:
        # Check if using Zeabur bearer token
        if credentials.credentials == ZEABUR_BEARER_TOKEN:
            return {"username": "zeabur_user"}
        
        # For development/testing, you can use a simple static token
        if os.getenv("ENVIRONMENT") == "development" and credentials.credentials == "dev-token":
            return {"username": "developer"}
            
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username}
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Error handler for validation errors
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    logger.warning(f"Validation error for {request.url}: {exc}")
    return JSONResponse(
        status_code=422,
        content={"error": "Invalid input format"}
    )

# Global exception handler for error sanitization
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error for {request.url}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# Routes
@app.get("/check-plate")
@limiter.limit("100/minute")
async def check_plate_get(
    request: Request,
    plate: str,
    current_user: dict = Depends(verify_token)
):
    """Check license plate via GET request with query parameter"""
    try:
        # Validate input
        plate_request = PlateRequest(plate=plate)
        
        result = await checker.check_plate(plate_request.plate)
        
        # Check if there's an error (plate not found) - but not for old military format
        if "error" in result and "Format plat militer lama terdeteksi" not in result.get("status", ""):
            raise HTTPException(
                status_code=404,
                detail="Plat tidak terdaftar"
            )
        
        return result
    except ValueError as e:
        logger.warning(f"Invalid plate format: {plate}")
        raise HTTPException(status_code=400, detail="Invalid plate format")

@app.post("/check-plate")
@limiter.limit("100/minute")
async def check_plate_post(
    request: Request,
    plate_request: PlateRequest,
    current_user: dict = Depends(verify_token)
):
    """Check license plate via POST request with JSON body"""
    try:
        result = await checker.check_plate(plate_request.plate)
        
        # Check if there's an error (plate not found) - but not for old military format
        if "error" in result and "Format plat militer lama terdeteksi" not in result.get("status", ""):
            raise HTTPException(
                status_code=404,
                detail="Plat nomor tidak terdaftar"
            )
        
        return result
    except Exception as e:
        logger.error(f"Error processing plate request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/")
@limiter.limit("100/minute")
async def home(request: Request):
    """API documentation and information"""
    response_data = {
        "message": "Indonesian Plate Checker API with Institution Support & OCR Military Compatibility",
        "version": "2.0.0",
        "security_features": [
            "Bearer token authentication",
            "Rate limiting (100 requests/minute)",
            "Input validation", 
            "Security headers",
            "Request timeouts",
            "Error sanitization"
        ],
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
        "authentication": {
            "type": "Bearer Token",
            "header": "Authorization: Bearer <token>",
            "note": "All endpoints require valid JWT token or configured bearer token",
            "zeabur_config": "Set ZEABUR_BEARER_TOKEN environment variable"
        },
        "endpoints": {
            "GET /check-plate?plate=B1234ABC": "Check standard plate via query parameter",
            "GET /check-plate?plate=12345-00": "Check old military plate via query parameter",
            "POST /check-plate": "Check plate via JSON body {'plate': 'B1234ABC' or '12345-00'}"
        }
    }
    return response_data

# Token generation endpoint for testing (only in development)
@app.post("/auth/token")
async def get_token(username: str = "test_user"):
    """Generate JWT token for testing purposes"""
    if os.getenv("ENVIRONMENT") != "development":
        raise HTTPException(status_code=404, detail="Not found")
    
    # No expiration for development
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer", "expires": "never"}

if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('PORT', 8080))  # Changed default port to 8080
    logger.info(f"Starting FastAPI app on port {port}")
    uvicorn.run(app, host='0.0.0.0', port=port)
