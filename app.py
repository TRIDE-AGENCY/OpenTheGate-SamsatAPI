from flask import Flask, request
import requests
import re
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

print("=== APP STARTING WITH INSTITUTION SUPPORT & OCR MILITARY COMPATIBILITY ===")

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
        # You can customize this mapping based on actual military organization
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
                # Default other suffixes to TNI Army (you can adjust this logic)
                self.military_suffix_mapping[suffix] = 'ZZD'
        
        # Map Roman numerals to TNI Army (traditional usage)
        for roman in self.VALID_ROMAN_SUFFIXES:
            self.military_suffix_mapping[roman] = 'ZZD'
        
        print(f"Institution codes loaded: {self.institution_codes}")
        print(f"Valid numeric suffixes: {len(self.VALID_NUMERIC_SUFFIXES)} suffixes (00-99)")
        print(f"Valid Roman suffixes: {self.VALID_ROMAN_SUFFIXES}")
        print(f"Military suffix mapping loaded: {len(self.military_suffix_mapping)} mappings")
    
    
    def check_plate(self, plate_number):
        print(f"=== CHECKING PLATE: {plate_number} ===")
        # Clean the plate number
        plate_clean = plate_number.replace('-', '').replace(' ', '').upper()
        
        # Check if it's an old military format from OCR
        if self.is_old_military_format(plate_number):
            return self.handle_old_military_plate(plate_number)
        # Check if it's a standard plate format that the database supports
        elif self.is_standard_plate(plate_clean):
            return self.check_standard_plate(plate_clean)
        else:
            return self.analyze_non_standard_plate(plate_number)
    
    def is_old_military_format(self, plate):
        """Check if plate matches old military format from OCR: XXXXX-XX, XXXX-XX, XXXXX-X, or XXXX-X"""
        plate_clean = plate.replace(' ', '').upper()
        
        # Check for numeric suffixes (00-99)
        numeric_pattern = r'^(\d{4,5})-(\d{2})$'  # 4 or 5 digits + 2 digit suffix
        numeric_match = re.match(numeric_pattern, plate_clean)
        if numeric_match:
            suffix = numeric_match.group(2)
            if suffix in self.VALID_NUMERIC_SUFFIXES:
                print(f"DETECTED OLD MILITARY FORMAT (NUMERIC): {plate_clean}")
                return True
        
        # Check for Roman numeral suffixes (I-IX)
        roman_pattern = r'^(\d{4,5})-(I|II|III|IV|V|VI|VII|VIII|IX)$'  # 4 or 5 digits + Roman numeral
        roman_match = re.match(roman_pattern, plate_clean)
        if roman_match:
            suffix = roman_match.group(2)
            if suffix in self.VALID_ROMAN_SUFFIXES:
                print(f"DETECTED OLD MILITARY FORMAT (ROMAN): {plate_clean}")
                return True
        
        return False
    
    def handle_old_military_plate(self, plate):
        """Convert old military format to analyzable format and provide detailed info"""
        plate_clean = plate.replace(' ', '').upper()
        print(f"PROCESSING OLD MILITARY PLATE: {plate_clean}")
        
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
        
        print(f"OLD MILITARY RESULT: {result}")
        return result
    
    def get_military_vehicle_type(self, number_part):
        """Simple military vehicle classification - returns only 'Kendaraan Militer'"""
        return "Kendaraan Militer"
    
    def is_standard_plate(self, plate_clean):
        # Check if it matches XX-XXXX-XXX format (without hyphens: XXXXXXXX)
        pattern = r'^[A-Z]+\d+[A-Z]+$'
        return bool(re.match(pattern, plate_clean))
    
    def check_standard_plate(self, plate_clean):
        prefix, middle, suffix = self.parse_standard_plate(plate_clean)
        print(f"PARSED: prefix={prefix}, middle={middle}, suffix={suffix}")
        
        if not prefix or middle is None or not suffix:
            return {"error": "Invalid standard plate format"}
        
        # Use only the last letter of suffix for API call (as per original logic)
        suffix_for_api = suffix[-1]
        url = f"{self.base_url}/nopol/{prefix}/belakang/{suffix_for_api}"
        print(f"API URL: {url}")
        
        try:
            response = requests.get(url)
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
                    print(f"INSTITUTION CHECK: suffix='{suffix}' -> institution='{institution_name}'")
                    
                    if institution_name:
                        ordered_result["institution"] = institution_name
                        print(f"ADDED INSTITUTION FIELD: {institution_name}")
                    else:
                        print("NO INSTITUTION FOUND")
                    
                    ordered_result["plate_analysis"] = plate_analysis
                    ordered_result["plate_region"] = result["plate_region"]
                    
                    print(f"FINAL RESULT KEYS: {list(ordered_result.keys())}")
                    return ordered_result
                return result
            else:
                return {"error": f"Plate not found: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def parse_standard_plate(self, plate_clean):
        # Parse XXXXXXXX format (e.g., B1234ABC -> B, 1234, ABC)
        pattern = r'^([A-Z]+)(\d+)([A-Z]+)$'
        match = re.match(pattern, plate_clean)
        if match:
            prefix = match.group(1)
            middle = int(match.group(2))
            suffix = match.group(3)
            return prefix, middle, suffix
        return None, None, None
    
    def get_vehicle_type(self, middle_number):
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
    
    def get_plate_type(self, suffix):
        if suffix in self.institution_codes:
            return "Dinas TNI dan POLRI" 
        else:
            return "Sipil"
    
    def get_institution_name(self, suffix):
        result = self.institution_codes.get(suffix, None)
        print(f"get_institution_name('{suffix}') = '{result}'")
        return result
    
    def analyze_non_standard_plate(self, plate):
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
    
    def parse_plate(self, plate):
        # Legacy method for backward compatibility
        pattern = r'^([A-Z]+)\d+([A-Z]+)$'
        match = re.match(pattern, plate.upper())
        if match:
            return match.group(1), match.group(2)[-1]
        return None, None
    
    def format_response(self, data):
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

@app.route('/check-plate', methods=['GET'])
def check_plate():
    plate_number = request.args.get('plate')
    
    if not plate_number:
        return app.response_class(
            response=json.dumps({"error": "Plate number is required"}),
            status=400,
            mimetype='application/json'
        )
    
    result = checker.check_plate(plate_number)
    
    # Check if there's an error (plate not found) - but not for old military format
    if "error" in result and "Format plat militer lama terdeteksi" not in result.get("status", ""):
        return app.response_class(
            response=json.dumps({"message": "Plat tidak terdaftar"}),
            status=404,
            mimetype='application/json'
        )
    
    return app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )

@app.route('/check-plate', methods=['POST'])
def check_plate_post():
    data = request.get_json()
    
    if not data or 'plate' not in data:
        return app.response_class(
            response=json.dumps({"error": "Plate number is required"}),
            status=400,
            mimetype='application/json'
        )
    
    plate_number = data['plate']
    result = checker.check_plate(plate_number)
    
    # Check if there's an error (plate not found) - but not for old military format
    if "error" in result and "Format plat militer lama terdeteksi" not in result.get("status", ""):
        return app.response_class(
            response=json.dumps({"message": "Plat nomor tidak terdaftar"}),
            status=404,
            mimetype='application/json'
        )
    
    return app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )

@app.route('/', methods=['GET'])
def home():
    response_data = {
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
    return app.response_class(
        response=json.dumps(response_data),
        status=200,
        mimetype='application/json'
    )

if __name__ == '__main__':
    # Get port from environment variable (cloud platforms often set this)
    import os
    port = int(os.environ.get('PORT', 5555))
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', debug=False, port=port)
