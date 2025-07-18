# Infrastructure Configuration

This directory contains infrastructure and deployment configuration files for the Multi-Agent System.

## Files

- `docker-compose.yml` - Main Docker Compose configuration for production deployment
- `docker-compose.dev.yml` - Development-specific Docker Compose configuration
- `.env.example` - Example environment variables file

## Usage

### Docker Deployment

From the project root directory:

```bash
# Production deployment
docker compose -f infrastructure/docker-compose.yml up -d

# Development deployment  
docker compose -f infrastructure/docker-compose.dev.yml up -d
```

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp infrastructure/.env.example .env
   ```

2. Edit `.env` with your specific configuration values

3. The `.env` file should be placed at the project root (not in this directory) so Docker Compose can find it.

## Notes

- All infrastructure files have been moved to this directory to keep the project root clean
- The main application can still be run using `python run.py` from the project root
- Docker Compose files reference paths relative to the project root
