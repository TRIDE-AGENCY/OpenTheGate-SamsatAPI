#!/bin/bash

# Samsat API Deployment Script with Nginx
# This script helps deploy and manage the Samsat API with nginx reverse proxy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Create environment file if it doesn't exist
create_env_file() {
    if [ ! -f .env ]; then
        log_info "Creating .env file..."
        cat > .env << EOF
# Samsat API Environment Variables
SECRET_KEY=$(openssl rand -hex 32)
ZEABUR_BEARER_TOKEN=$(openssl rand -hex 16)
ENVIRONMENT=production
PORT=5555
EOF
        log_success "Created .env file with random secrets"
        log_warning "Please update ZEABUR_BEARER_TOKEN in .env file with your preferred token"
    else
        log_info ".env file already exists"
    fi
}

# Start services
start() {
    log_info "Starting Samsat API with Nginx..."
    
    check_docker
    create_env_file
    
    # Build and start services
    docker-compose down 2>/dev/null || true
    docker-compose build --no-cache
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        log_success "Services started successfully!"
        log_info "API is available at: http://localhost"
        log_info "Direct FastAPI access: http://localhost:5555"
        show_status
    else
        log_error "Failed to start services"
        docker-compose logs
        exit 1
    fi
}

# Stop services
stop() {
    log_info "Stopping Samsat API services..."
    docker-compose down
    log_success "Services stopped"
}

# Restart services
restart() {
    log_info "Restarting Samsat API services..."
    stop
    start
}

# Show service status
show_status() {
    echo
    log_info "Service Status:"
    docker-compose ps
    echo
    log_info "Health Status:"
    
    # Check nginx health
    if curl -f -s http://localhost/health > /dev/null 2>&1; then
        log_success "✓ Nginx is healthy"
    else
        log_error "✗ Nginx is not responding"
    fi
    
    # Check FastAPI health
    if curl -f -s http://localhost:5555/ > /dev/null 2>&1; then
        log_success "✓ FastAPI is healthy"
    else
        log_error "✗ FastAPI is not responding"
    fi
}

# Show logs
show_logs() {
    local service=${1:-}
    if [ -n "$service" ]; then
        docker-compose logs -f "$service"
    else
        docker-compose logs -f
    fi
}

# Test API
test_api() {
    local token=${1:-"dev-token"}
    
    log_info "Testing API with token: $token"
    echo
    
    # Test through nginx (port 80)
    log_info "Testing through Nginx (port 80):"
    if curl -s -H "Authorization: Bearer $token" http://localhost/check-plate?plate=B1234ABC | jq .; then
        log_success "✓ Nginx proxy test passed"
    else
        log_error "✗ Nginx proxy test failed"
    fi
    
    echo
    
    # Test direct FastAPI (port 5555)
    log_info "Testing direct FastAPI (port 5555):"
    if curl -s -H "Authorization: Bearer $token" http://localhost:5555/check-plate?plate=B1234ABC | jq .; then
        log_success "✓ Direct FastAPI test passed"
    else
        log_error "✗ Direct FastAPI test failed"
    fi
}

# Update configuration
update_config() {
    log_info "Updating configuration..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    log_success "Configuration updated"
}

# Show usage
show_help() {
    echo "Samsat API Deployment Script"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start           Start all services (nginx + FastAPI)"
    echo "  stop            Stop all services"
    echo "  restart         Restart all services"
    echo "  status          Show service status and health"
    echo "  logs [service]  Show logs (optional: nginx or samsat-api)"
    echo "  test [token]    Test API endpoints (optional: bearer token)"
    echo "  update          Update configuration and restart"
    echo "  help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                    # Start all services"
    echo "  $0 logs nginx              # Show nginx logs"
    echo "  $0 test my-bearer-token    # Test with custom token"
    echo
}

# Main script logic
case "${1:-help}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    test)
        test_api "$2"
        ;;
    update)
        update_config
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 