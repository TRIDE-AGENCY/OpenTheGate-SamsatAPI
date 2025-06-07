# Samsat API Security Guide

## Overview
The Samsat API has been upgraded to FastAPI with comprehensive security features including Bearer token authentication, rate limiting, input validation, security headers, request timeouts, and error sanitization. **Now includes Nginx reverse proxy for enhanced security and performance.**

## Architecture

```
Internet → Nginx (Port 80/443) → FastAPI (Port 5555)
```

## Security Features

### 1. Bearer Token Authentication
All endpoints require a valid JWT token in the Authorization header.

#### Zeabur Cloud Deployment
Set the bearer token as an environment variable:
```bash
ZEABUR_BEARER_TOKEN=your-secure-token-here
```

#### Development/Testing
For development, you can use a simple token:
```bash
export ENVIRONMENT=development
```
Then use `dev-token` as the bearer token.

#### Token Generation (Development Only)
```bash
curl -X POST "http://localhost:5555/auth/token?username=your_username"
```

**Note**: Tokens do not expire in development mode.

### 2. Nginx Security Layer
- **Reverse Proxy**: Hides the backend FastAPI server
- **Rate Limiting**: 100 requests/minute + burst protection
- **Request Filtering**: Blocks malicious requests and attack patterns
- **Security Headers**: Additional layer of security headers
- **SSL Termination**: Ready for HTTPS configuration
- **Request Size Limits**: Prevents large payload attacks
- **Timeout Protection**: Prevents slow attacks

### 3. Rate Limiting (Dual Layer)
- **Nginx Level**: 100 requests/minute + 10 requests/second burst
- **FastAPI Level**: 100 requests/minute per IP address
- **Response**: HTTP 429 when limit exceeded

### 4. Input Validation
- Plate numbers are validated and sanitized
- Invalid characters are removed
- Length limits enforced (1-20 characters)

### 5. Security Headers (Enhanced with Nginx)
The system automatically adds these security headers:
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Cache-Control: no-cache, no-store, must-revalidate`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-Permitted-Cross-Domain-Policies: none`

### 6. Request Timeouts
- **Nginx**: 30 seconds for all proxy requests
- **FastAPI**: 30 seconds for application requests
- **Response**: HTTP 408 on timeout

### 7. Error Sanitization
- Sensitive information hidden from error responses
- Generic error messages for security
- Detailed logging for debugging (server-side only)

### 8. Attack Protection
- **File Access Protection**: Blocks access to sensitive files (.env, .log, etc.)
- **Script Injection Protection**: Blocks PHP, ASP, JSP requests
- **Directory Traversal Protection**: Blocks access to hidden files
- **Documentation Hiding**: Blocks access to /docs and /redoc endpoints

## Deployment Options

### Option 1: Docker Compose (Recommended)

#### Quick Start:
```bash
# Make deployment script executable
chmod +x deploy.sh

# Start all services
./deploy.sh start

# Check status
./deploy.sh status

# Test API
./deploy.sh test your-bearer-token
```

#### Manual Docker Compose:
```bash
# Create environment file
cat > .env << EOF
SECRET_KEY=your-secret-key-here
ZEABUR_BEARER_TOKEN=your-bearer-token
ENVIRONMENT=production
PORT=5555
EOF

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Option 2: Traditional Setup

#### Install Nginx:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

#### Configure Nginx:
```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/nginx.conf

# Test configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### Start FastAPI:
```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI
uvicorn app:app --host 127.0.0.1 --port 5555
```

## API Usage Examples

### 1. Using Nginx Proxy (Recommended)
```bash
curl -X GET "http://localhost/check-plate?plate=B1234ABC" \
  -H "Authorization: Bearer your-bearer-token"
```

### 2. Direct FastAPI Access
```bash
curl -X GET "http://localhost:5555/check-plate?plate=B1234ABC" \
  -H "Authorization: Bearer your-bearer-token"
```

### 3. Health Check
```bash
# Through nginx
curl -X GET "http://localhost/health"

# Direct FastAPI
curl -X GET "http://localhost:5555/"
```

### 4. Check Plate via POST
```bash
curl -X POST "http://localhost/check-plate" \
  -H "Authorization: Bearer your-bearer-token" \
  -H "Content-Type: application/json" \
  -d '{"plate": "B1234ABC"}'
```

### 5. Check Military Plate
```bash
curl -X GET "http://localhost/check-plate?plate=12345-00" \
  -H "Authorization: Bearer your-bearer-token"
```

## Environment Variables

### Required for Production
```bash
ZEABUR_BEARER_TOKEN=your-secure-bearer-token
SECRET_KEY=your-secret-key-here
ENVIRONMENT=production
PORT=5555
```

### Optional
```bash
PORT=5555  # Default port (changed from 8000)
```

## Nginx Configuration Details

### Rate Limiting Zones:
- `api`: 100 requests/minute
- `burst`: 10 requests/second

### Blocked Patterns:
- Script files: `.php`, `.asp`, `.aspx`, `.jsp`
- Hidden files: Files starting with `.`
- Sensitive files: `.env`, `.log`, `.ini`, `.conf`, `.bak`, `.sql`, `.old`
- Documentation: `/docs`, `/redoc`, `/openapi.json`

### Security Features:
- Request size limits (1MB max)
- Connection timeouts (30s)
- Gzip compression for JSON responses
- Custom error pages
- Access logging

## SSL/HTTPS Configuration

### Enable HTTPS (Production):
1. Obtain SSL certificate (Let's Encrypt recommended)
2. Update nginx.conf to enable HTTPS block
3. Configure certificate paths
4. Enable HTTP to HTTPS redirect

```bash
# Example with Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Logging

### Log Locations:
- **Nginx Access**: `/var/log/nginx/access.log`
- **Nginx Error**: `/var/log/nginx/error.log`
- **FastAPI**: Docker logs or application logs

### Health Monitoring:
```bash
# Check service status
./deploy.sh status

# View logs
./deploy.sh logs nginx
./deploy.sh logs samsat-api

# Test endpoints
./deploy.sh test your-token
```

### Performance Monitoring:
- Monitor nginx access logs for rate limit violations
- Check FastAPI response times
- Monitor system resources (CPU, memory)
- Track error rates

## Security Best Practices

1. **Always use HTTPS in production**
2. **Set a strong SECRET_KEY**
3. **Use a secure ZEABUR_BEARER_TOKEN**
4. **Keep bearer tokens confidential**
5. **Monitor rate limit violations**
6. **Regularly update nginx and dependencies**
7. **Monitor logs for security events**
8. **Configure firewall rules**
9. **Use strong SSL/TLS configuration**
10. **Implement log rotation**

## Error Handling

### Client Errors
- **400**: Invalid input format
- **401**: Invalid/missing authentication
- **404**: Plate not found / Endpoint not found
- **408**: Request timeout
- **422**: Validation error
- **429**: Rate limit exceeded

### Server Errors
- **500**: Internal server error (sanitized)
- **502**: Bad Gateway (nginx cannot reach FastAPI)
- **503**: Service Unavailable
- **504**: Gateway Timeout

## Troubleshooting

### Common Issues:

1. **502 Bad Gateway**
   - Check if FastAPI is running on port 5555
   - Verify network connectivity between nginx and FastAPI

2. **Rate Limit Exceeded**
   - Check nginx rate limiting configuration
   - Monitor access logs for excessive requests

3. **SSL Certificate Issues**
   - Verify certificate paths in nginx.conf
   - Check certificate expiration

4. **Authentication Failures**
   - Verify ZEABUR_BEARER_TOKEN is set correctly
   - Check Authorization header format

### Debug Commands:
```bash
# Check nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# Check FastAPI logs
docker-compose logs samsat-api

# Check nginx logs
docker-compose logs nginx

# Test nginx upstream
curl -I http://localhost:5555/
```

## Migration from Previous Version

### Key Changes
1. **Added Nginx**: Reverse proxy layer for enhanced security
2. **Dual Rate Limiting**: Both nginx and FastAPI level protection
3. **Enhanced Security**: Additional attack protection and filtering
4. **Docker Compose**: Simplified deployment with containers
5. **Health Checks**: Automated service monitoring
6. **Deployment Script**: Easy management with `deploy.sh`

### Compatibility
- All existing endpoints maintained
- Same response formats
- Same business logic
- Same plate checking functionality
- **New**: Access through port 80 (nginx) or 5555 (direct)

## Support

For issues or questions:
1. Check deployment script: `./deploy.sh status`
2. View logs: `./deploy.sh logs`
3. Test connectivity: `./deploy.sh test`
4. Verify authentication token (JWT or Zeabur bearer token)
5. Ensure rate limits not exceeded
6. Validate input format
7. Check environment variables are set correctly
8. Verify nginx configuration: `sudo nginx -t` 