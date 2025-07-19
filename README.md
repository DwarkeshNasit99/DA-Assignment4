# Database Migration Assignment - Flyway Implementation

This repository contains a complete implementation of database migration using Flyway for a subscriber management system. The project demonstrates automated database deployment, migration management, and testing in a CI/CD environment.

## Project Structure

```
├── migrations/
│   ├── initial/                    # Initial database setup migrations
│   │   └── V1__Create_subscribers_table.sql
│   └── incremental/                # Incremental schema changes
│       ├── V2__Add_subscription_preferences.sql
│       └── V3__Add_subscription_history.sql
├── tests/
│   ├── __init__.py
│   └── test_subscriber_crud.py     # CRUD operation tests
├── .github/workflows/
│   └── mysql_action.yml           # GitHub Actions workflow
├── up.yml                         # Ansible playbook for environment setup
├── down.yml                       # Ansible playbook for environment cleanup
├── flyway.conf                    # Flyway configuration
└── README.md                      # This file
```

## Database Schema

The subscriber database includes three main tables:

1. **subscribers** - Core subscriber information
   - id (Primary Key)
   - email (Unique)
   - first_name, last_name
   - is_active (Boolean)
   - created_at, updated_at (Timestamps)

2. **subscription_preferences** - User preferences
   - id (Primary Key)
   - subscriber_id (Foreign Key)
   - newsletter_enabled, marketing_enabled (Boolean)
   - frequency (ENUM: daily, weekly, monthly)

3. **subscription_history** - Audit trail
   - id (Primary Key)
   - subscriber_id (Foreign Key)
   - action (ENUM: subscribed, unsubscribed, updated, reactivated)
   - action_date, notes

## Prerequisites

- Docker and Docker Compose
- Ansible
- Python 3.9+
- Git

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/PROG8850flyway.git
cd PROG8850flyway
```

### 2. Start the Environment

```bash
ansible-playbook up.yml
```

This will:
- Start MySQL database using Docker Compose
- Install required dependencies
- Create subscriber database and user
- Run initial Flyway migrations using nektos/act

### 3. Verify Setup

Connect to the database:
```bash
mysql -u subscriber_user -h 127.0.0.1 -p
# Password: SubscriberPass123
```

Check the database:
```sql
USE subscriber_db;
SHOW TABLES;
SELECT * FROM subscribers;
```

## Running Migrations

### Manual Migration Execution

Run initial migrations:
```bash
docker run --rm -v "$(pwd)/migrations/initial:/flyway/sql" \
  redgate/flyway \
  -user=subscriber_user \
  -password=SubscriberPass123 \
  -url=jdbc:mysql://127.0.0.1:3306/subscriber_db \
  migrate
```

Run incremental migrations:
```bash
docker run --rm -v "$(pwd)/migrations/incremental:/flyway/sql" \
  redgate/flyway \
  -user=subscriber_user \
  -password=SubscriberPass123 \
  -url=jdbc:mysql://127.0.0.1:3306/subscriber_db \
  migrate
```

### Using Flyway Configuration

```bash
flyway -configFiles=flyway.conf migrate
```

## Testing

### Run Tests Locally

```bash
# Install dependencies
pip install mysql-connector-python pytest

# Set environment variables
export DB_HOST=127.0.0.1
export DB_USER=subscriber_user
export DB_PASSWORD=SubscriberPass123
export DB_NAME=subscriber_db

# Run tests
python -m pytest tests/test_subscriber_crud.py -v
```

### Test Coverage

The test suite covers:
- ✅ Create subscriber (INSERT)
- ✅ Read subscriber (SELECT)
- ✅ Update subscriber (UPDATE)
- ✅ Delete subscriber (DELETE)
- ✅ Subscription preferences CRUD
- ✅ Subscription history tracking
- ✅ Email uniqueness constraints
- ✅ Foreign key constraints

Each test manages its own data and cleans up after execution.

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/mysql_action.yml`) automatically:

1. **Sets up the environment** - Creates database and user
2. **Runs initial migrations** - Applies V1__Create_subscribers_table.sql
3. **Runs incremental migrations** - Applies V2 and V3 migrations
4. **Executes tests** - Runs all CRUD operation tests
5. **Reports deployment status** - Outputs success message

### Triggering the Pipeline

The workflow runs on:
- Push to any branch
- Pull request creation/update

### Local Testing with nektos/act

```bash
# Run the workflow locally
bin/act push -W .github/workflows/mysql_action.yml

# If the above doesn't work, try:
bin/act -P ubuntu-latest=-self-hosted
```

## Database Management

### Adding New Migrations

1. Create a new SQL file in `migrations/incremental/`
2. Use the naming convention: `V{version}__{description}.sql`
3. Example: `V4__Add_subscription_categories.sql`

### Migration Best Practices

- Use descriptive names for migration files
- Include both schema changes and data migrations
- Test migrations locally before committing
- Keep migrations atomic and focused
- Document complex migrations in comments

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DB_HOST | 127.0.0.1 | Database host address |
| DB_USER | subscriber_user | Database username |
| DB_PASSWORD | SubscriberPass123 | Database password |
| DB_NAME | subscriber_db | Database name |

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Ensure MySQL is running: `docker ps`
   - Check credentials in flyway.conf
   - Verify network connectivity

2. **Migration conflicts**
   - Check Flyway schema history: `flyway info`
   - Resolve version conflicts manually
   - Use `flyway repair` if needed

3. **Test failures**
   - Ensure database is accessible
   - Check environment variables
   - Verify test data cleanup

### Useful Commands

```bash
# Check Flyway status
flyway -configFiles=flyway.conf info

# Clean database (WARNING: Destructive)
flyway -configFiles=flyway.conf clean

# Validate migrations
flyway -configFiles=flyway.conf validate

# Repair Flyway metadata
flyway -configFiles=flyway.conf repair
```

## Cleanup

To remove the entire environment:

```bash
ansible-playbook down.yml
```

This will:
- Stop and remove Docker containers
- Remove subscriber database and user
- Clean up installed packages

## Assignment Requirements Checklist

- ✅ **Up and down .yml files** - Environment scaffolding with nektos/act
- ✅ **Initial Setup** - Subscriber database with restricted user
- ✅ **Incremental migrations** - Separate folder for schema changes
- ✅ **GitHub Actions workflow** - Automated migration execution
- ✅ **Automated Tests** - Comprehensive CRUD operation tests
- ✅ **Deployment indication** - Console output in workflow
- ✅ **README.md** - Complete documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
