# Pleasanter Docker Compose

Simple Docker Compose setup for Pleasanter with PostgreSQL.

## Quick Start

1. **Setup environment**
   ```bash
   cp .env.local .env
   # Edit .env and change POSTGRES_PASSWORD
   ```

2. **Start services**
   ```bash
   docker compose up -d
   ```

3. **Initialize database** (first time only)
   ```bash
   docker compose --profile init run --rm codedefiner _rds
   ```

4. **Access Pleasanter**
   - URL: http://localhost:8080
   - Username: Administrator
   - Password: pleasanter

## Services

- **postgres**: PostgreSQL database
- **pleasanter**: Pleasanter web application  
- **codedefiner**: Database initialization (profile: init)

## Configuration

Edit `.env` file to customize:
- `POSTGRES_PASSWORD`: Database password (required)
- `PLEASANTER_PORT`: Web port (default: 8080)
- `POSTGRES_PORT`: Database port (default: 5432)

## Commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# View logs
docker compose logs -f

# Database shell
docker compose exec postgres psql -U pleasanter
```
