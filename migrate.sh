#!/bin/bash
# Script để chạy Alembic migrations

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Alembic Migration Manager ===${NC}"

# Check if we're in Docker or local environment
if [ -f "/.dockerenv" ]; then
    echo -e "${YELLOW}Running in Docker container${NC}"
else
    echo -e "${YELLOW}Running in local environment${NC}"
    # Make sure we're in the backend directory
    cd "$(dirname "$0")/backend"
fi

# Function to display help
show_help() {
    echo "Usage: ./migrate.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  upgrade         - Apply all pending migrations (alembic upgrade head)"
    echo "  downgrade       - Rollback one migration (alembic downgrade -1)"
    echo "  current         - Show current migration version"
    echo "  history         - Show migration history"
    echo "  create [name]   - Create a new migration file"
    echo "  autogenerate [name] - Auto-generate migration from models"
    echo "  help            - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./migrate.sh upgrade"
    echo "  ./migrate.sh create add_user_avatar"
    echo "  ./migrate.sh autogenerate add_new_fields"
}

# Main command handler
case "$1" in
    upgrade)
        echo -e "${GREEN}Applying all pending migrations...${NC}"
        alembic upgrade head
        echo -e "${GREEN}✓ Migrations applied successfully${NC}"
        ;;
    
    downgrade)
        echo -e "${YELLOW}Rolling back one migration...${NC}"
        alembic downgrade -1
        echo -e "${GREEN}✓ Rollback completed${NC}"
        ;;
    
    current)
        echo -e "${GREEN}Current migration version:${NC}"
        alembic current
        ;;
    
    history)
        echo -e "${GREEN}Migration history:${NC}"
        alembic history --verbose
        ;;
    
    create)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Migration name required${NC}"
            echo "Usage: ./migrate.sh create <migration_name>"
            exit 1
        fi
        echo -e "${GREEN}Creating new migration: $2${NC}"
        alembic revision -m "$2"
        echo -e "${GREEN}✓ Migration file created${NC}"
        ;;
    
    autogenerate)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Migration name required${NC}"
            echo "Usage: ./migrate.sh autogenerate <migration_name>"
            exit 1
        fi
        echo -e "${GREEN}Auto-generating migration: $2${NC}"
        alembic revision --autogenerate -m "$2"
        echo -e "${GREEN}✓ Migration file auto-generated${NC}"
        echo -e "${YELLOW}⚠ Please review the generated migration file before applying${NC}"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
