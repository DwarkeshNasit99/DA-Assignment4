Assignment 4 - Database Migration with Flyway

**Repository:** https://github.com/DwarkeshNasit99/DA-Assignment4  
**GitHub Actions:** [![CI/CD Pipeline](https://github.com/DwarkeshNasit99/DA-Assignment4/actions/workflows/mysql_action.yml/badge.svg)](https://github.com/DwarkeshNasit99/DA-Assignment4/actions/workflows/mysql_action.yml)


## Project Explanation

### Automated Setup
```bash
# Clone and run the complete project
git clone https://github.com/DwarkeshNasit99/DA-Assignment4.git
cd DA-Assignment4
./run_project.sh
```

### Manual Setup
```bash
 1. Start database environment

docker-compose up -d

2. Run Flyway migrations

docker run --rm -v $(pwd)/migrations:/flyway/sql flyway/flyway:9-alpine -url=jdbc:mysql://host.docker.internal:3306/subscriber_db -user=root -password=rootpassword migrate

3. Run tests

python -m pytest tests/ -v

4. Access Adminer (Database UI)

- **URL:** http://localhost:8081
- **System:** MySQL
- **Server:** mysql
- **Username:** subscriber_user
- **Password:** SubscriberPass123
- **Database:** subscriber_db
```

---

## System Components

### Database Schema
- **subscribers**: Core subscriber information
- **subscription_preferences**: User preferences and settings
- **subscription_history**: Historical subscription changes
- **audit_log**: System audit trail

### Migration Files
- `V1__Create_subscribers_table.sql` - Initial schema
- `V2__Add_subscription_preferences.sql` - Preferences table
- `V3__Add_subscription_history.sql` - History tracking

### CI/CD Pipeline
- **GitHub Actions**: Automated testing and deployment
- **Docker**: Containerized environment
- **Ansible**: Infrastructure automation
- **Flyway**: Database migration management

---

## Testing

**Test Suite:** 8 comprehensive test cases
- Subscriber CRUD operations
- Preference management
- History tracking
- Data validation

**Run Tests:**
```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
Assignment 4/
├── migrations/           # Flyway migration scripts
├── tests/               # Automated test suite
├── .github/workflows/   # CI/CD pipeline
├── docker-compose.yml   # Environment setup
├── up.yml              # Ansible automation
├── Question1_Analysis.md # Tool comparison analysis
└── README.md           # This file
```

---

## Verification

1. **Database Access:** http://localhost:8081 (Adminer)
2. **Migration Status:** `docker run --rm -v $(pwd)/migrations:/flyway/sql flyway/flyway:9-alpine -url=jdbc:mysql://host.docker.internal:3306/subscriber_db -user=root -password=rootpassword info`
3. **Test Results:** All 8 tests passing
4. **CI/CD Status:** GitHub Actions workflow successful

---

## Submission Information

- **Repository:** https://github.com/DwarkeshNasit99/DA-Assignment4
- **Analysis Document:** Question1_Analysis.md
- **CI/CD Proof:** GitHub Actions workflow badge above
- **Working Demo:** Available via Adminer interface

**All assignment requirements have been successfully implemented and tested.**