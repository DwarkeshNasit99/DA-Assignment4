#!/bin/bash

echo "🚀 Starting Assignment 4 - Database Migration with Flyway"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
print_status "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Step 1: Set up the environment using Ansible
print_status "Step 1: Setting up MySQL environment with Ansible..."
if command -v ansible-playbook > /dev/null 2>&1; then
    ansible-playbook up.yml
    if [ $? -eq 0 ]; then
        print_success "Environment setup completed"
    else
        print_error "Environment setup failed"
        exit 1
    fi
else
    print_warning "Ansible not found, using Docker Compose directly..."
    docker-compose up -d
    if [ $? -eq 0 ]; then
        print_success "Docker environment started"
    else
        print_error "Failed to start Docker environment"
        exit 1
    fi
fi

# Wait for MySQL to be ready
print_status "Waiting for MySQL to be ready..."
sleep 10

# Step 2: Run Flyway migrations
print_status "Step 2: Running Flyway migrations..."
if command -v flyway > /dev/null 2>&1; then
    flyway -configFiles=flyway.conf migrate
    if [ $? -eq 0 ]; then
        print_success "Flyway migrations completed"
    else
        print_error "Flyway migrations failed"
        exit 1
    fi
else
    print_warning "Flyway CLI not found, using Docker..."
    docker run --rm \
        -v "$(pwd)/migrations:/flyway/sql" \
        -v "$(pwd)/flyway.conf:/flyway/conf/flyway.conf" \
        --network assignment4_default \
        flyway/flyway:9-alpine \
        -configFiles=/flyway/conf/flyway.conf migrate
    if [ $? -eq 0 ]; then
        print_success "Flyway migrations completed via Docker"
    else
        print_error "Flyway migrations failed"
        exit 1
    fi
fi

# Step 3: Install Python dependencies
print_status "Step 3: Installing Python dependencies..."
if command -v pip > /dev/null 2>&1; then
    pip install mysql-connector-python
    if [ $? -eq 0 ]; then
        print_success "Python dependencies installed"
    else
        print_warning "Failed to install Python dependencies"
    fi
else
    print_warning "pip not found, skipping Python dependency installation"
fi

# Step 4: Run automated tests
print_status "Step 4: Running automated CRUD tests..."
python tests/test_subscriber_crud.py
if [ $? -eq 0 ]; then
    print_success "All tests passed"
else
    print_warning "Some tests failed, but continuing..."
fi

# Step 5: Run demonstration
print_status "Step 5: Running demonstration..."
python demo_system.py
if [ $? -eq 0 ]; then
    print_success "Demonstration completed"
else
    print_warning "Demonstration had issues"
fi

# Step 6: Show project status
print_status "Step 6: Checking project status..."
echo ""
echo "📊 PROJECT STATUS:"
echo "=================="

# Check if containers are running
if docker ps | grep -q "mysql"; then
    print_success "MySQL container is running"
else
    print_error "MySQL container is not running"
fi

if docker ps | grep -q "adminer"; then
    print_success "Adminer container is running"
else
    print_error "Adminer container is not running"
fi

# Check database connection
if mysql -h 127.0.0.1 -P 3307 -u subscriber_user -pSubscriberPass123 subscriber_db -e "SELECT COUNT(*) FROM subscribers;" > /dev/null 2>&1; then
    print_success "Database connection working"
else
    print_error "Database connection failed"
fi

# Show access information
echo ""
echo "🌐 ACCESS INFORMATION:"
echo "====================="
echo "Adminer (Database UI): http://localhost:8081"
echo "  - System: MySQL"
echo "  - Server: mysql"
echo "  - Username: subscriber_user"
echo "  - Password: SubscriberPass123"
echo "  - Database: subscriber_db"
echo ""
echo "MySQL Direct Access:"
echo "  - Host: 127.0.0.1"
echo "  - Port: 3307"
echo "  - Username: subscriber_user"
echo "  - Password: SubscriberPass123"
echo "  - Database: subscriber_db"
echo ""

# Show available commands
echo "🔧 AVAILABLE COMMANDS:"
echo "====================="
echo "• View logs: docker-compose logs"
echo "• Stop environment: docker-compose down"
echo "• Run tests: python tests/test_subscriber_crud.py"
echo "• Check Flyway: python test_flyway.py"
echo "• Access MySQL: mysql -h 127.0.0.1 -P 3307 -u subscriber_user -pSubscriberPass123 subscriber_db"
echo ""

print_success "🎉 Project is now running! Open http://localhost:8081 to access Adminer"
print_status "Press Ctrl+C to stop the environment when done" 