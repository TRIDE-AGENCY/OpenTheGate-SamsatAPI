from flask import Flask, request
import requests
import re
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

print("=== APP STARTING WITH INSTITUTION SUPPORT ===")

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
        print(f"Institution codes loaded: {self.institution_codes}")
    
    def check_plate(self, plate_number):
        print(f"=== CHECKING PLATE: {plate_number} ===")
        # Clean the plate number
        plate_clean = plate_number.replace('-', '').replace(' ', '').upper()
        
        # Check if it's a standard plate format that the database supports
        if self.is_standard_plate(plate_clean):
            return self.check_standard_plate(plate_clean)
        else:
            return self.analyze_non_standard_plate(plate_number)
    
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
        
        # Old military: XXXX-XX format
        elif re.match(r'^\d{4}(00|01|02|09|10|V)$', plate_upper):
            return {
                "message": "Format plat militer lama tidak didukung oleh database",
                "jenis_plat_nomor": "Dinas TNI dan POLRI",
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
    
    # Check if there's an error (plate not found)
    if "error" in result:
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
    
    # Check if there's an error (plate not found)
    if "error" in result:
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
        "message": "Indonesian Plate Checker API with Institution Support",
        "database_support": "Hanya mendukung format plat standar Indonesia (XX-XXXX-XXX)",
        "supported_format": "XX-XXXX-XXX (e.g., B-1234-ABC, D-5678-ZZP)",
        "features": {
            "vehicle_classification": "Berdasarkan nomor identitas polisi (1-1999: Mobil Penumpang, 2000-6999: Sepeda Motor, 7000-7999: Mobil Bus, 8000-8999: Mobil Barang, 9000-9999: Kendaraan Khusus)",
            "plate_type": "Sipil atau Institusi (ZZT/ZZU/ZZD/ZZL/ZZP/ZZH)",
            "region_info": "Informasi provinsi, kota, kantor Samsat, dan alamat"
        },
        "endpoints": {
            "GET /check-plate?plate=B1234ABC": "Check plate via query parameter",
            "POST /check-plate": "Check plate via JSON body {'plate': 'B1234ABC'}"
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