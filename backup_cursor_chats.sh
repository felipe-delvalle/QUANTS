#!/bin/bash

# ============================================================
# Backup Cursor Chat History
# ============================================================
# This script backs up your Cursor chat history and settings
# to prevent loss of important conversations.
#
# Usage:
#   ./backup_cursor_chats.sh           # Create a backup
#   ./backup_cursor_chats.sh --auto    # Auto-backup (for cron)
#   ./backup_cursor_chats.sh --list    # List all backups
#   ./backup_cursor_chats.sh --restore # Restore from backup
# ============================================================

WORKSPACE_ROOT="/Users/freedom/QUANTS"
CURSOR_STORAGE="$HOME/Library/Application Support/Cursor/User/globalStorage"
BACKUP_DIR="$WORKSPACE_ROOT/.cursor/chat_backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="cursor_chats_${TIMESTAMP}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Function to create a backup
create_backup() {
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Cursor Chat Backup                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check if Cursor storage exists
    if [ ! -d "$CURSOR_STORAGE" ]; then
        echo -e "${RED}✗${NC} Cursor storage directory not found:"
        echo -e "   ${YELLOW}$CURSOR_STORAGE${NC}"
        echo ""
        echo "Make sure Cursor is installed and has been used at least once."
        exit 1
    fi
    
    # Create backup directory for this timestamp
    CURRENT_BACKUP="$BACKUP_DIR/$BACKUP_NAME"
    mkdir -p "$CURRENT_BACKUP"
    
    echo -e "${GREEN}✓${NC} Creating backup: ${BLUE}$BACKUP_NAME${NC}"
    echo ""
    
    # Backup key files
    echo -e "${BLUE}📦 Backing up files...${NC}"
    
    # Main database file (contains chat history)
    if [ -f "$CURSOR_STORAGE/state.vscdb" ]; then
        cp "$CURSOR_STORAGE/state.vscdb" "$CURRENT_BACKUP/state.vscdb" 2>/dev/null
        if [ $? -eq 0 ]; then
            SIZE=$(du -h "$CURRENT_BACKUP/state.vscdb" | cut -f1)
            echo -e "  ${GREEN}✓${NC} state.vscdb (${SIZE})"
        else
            echo -e "  ${YELLOW}⚠${NC} Could not backup state.vscdb (file may be locked)"
        fi
    fi
    
    # Backup database file
    if [ -f "$CURSOR_STORAGE/state.vscdb.backup" ]; then
        cp "$CURSOR_STORAGE/state.vscdb.backup" "$CURRENT_BACKUP/state.vscdb.backup" 2>/dev/null
        if [ $? -eq 0 ]; then
            SIZE=$(du -h "$CURRENT_BACKUP/state.vscdb.backup" | cut -f1)
            echo -e "  ${GREEN}✓${NC} state.vscdb.backup (${SIZE})"
        fi
    fi
    
    # Storage JSON file
    if [ -f "$CURSOR_STORAGE/storage.json" ]; then
        cp "$CURSOR_STORAGE/storage.json" "$CURRENT_BACKUP/storage.json" 2>/dev/null
        if [ $? -eq 0 ]; then
            SIZE=$(du -h "$CURRENT_BACKUP/storage.json" | cut -f1)
            echo -e "  ${GREEN}✓${NC} storage.json (${SIZE})"
        fi
    fi
    
    # Backup entire globalStorage directory structure (optional, for complete backup)
    echo -e "${BLUE}📁 Backing up directory structure...${NC}"
    tar -czf "$CURRENT_BACKUP/globalStorage_full.tar.gz" -C "$HOME/Library/Application Support/Cursor/User" globalStorage 2>/dev/null
    if [ $? -eq 0 ]; then
        SIZE=$(du -h "$CURRENT_BACKUP/globalStorage_full.tar.gz" | cut -f1)
        echo -e "  ${GREEN}✓${NC} Full globalStorage archive (${SIZE})"
    else
        echo -e "  ${YELLOW}⚠${NC} Could not create full archive"
    fi
    
    # Create metadata file
    cat > "$CURRENT_BACKUP/backup_info.txt" << EOF
Cursor Chat Backup
==================
Created: $(date)
Timestamp: $TIMESTAMP
Source: $CURSOR_STORAGE
Backup Location: $CURRENT_BACKUP

Files Backed Up:
- state.vscdb (main chat database)
- state.vscdb.backup (backup database)
- storage.json (settings and metadata)
- globalStorage_full.tar.gz (complete archive)

To restore:
  ./backup_cursor_chats.sh --restore $BACKUP_NAME
EOF
    
    echo ""
    echo -e "${GREEN}✓${NC} Backup completed: ${BLUE}$CURRENT_BACKUP${NC}"
    
    # Calculate total backup size
    TOTAL_SIZE=$(du -sh "$CURRENT_BACKUP" | cut -f1)
    echo -e "${GREEN}✓${NC} Total backup size: ${BLUE}$TOTAL_SIZE${NC}"
    echo ""
    
    # Clean up old backups (keep last 10)
    if [ "$1" != "--auto" ]; then
        list_backups_quiet
        BACKUP_COUNT=$(ls -1d "$BACKUP_DIR"/cursor_chats_* 2>/dev/null | wc -l | tr -d ' ')
        if [ "$BACKUP_COUNT" -gt 10 ]; then
            echo -e "${YELLOW}⚠${NC} You have $BACKUP_COUNT backups. Consider cleaning up old ones."
            echo -e "   Run ${BLUE}./backup_cursor_chats.sh --list${NC} to see all backups"
        fi
    fi
}

# Function to list all backups
list_backups() {
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Cursor Chat Backups                          ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A "$BACKUP_DIR" 2>/dev/null)" ]; then
        echo -e "${YELLOW}No backups found.${NC}"
        echo "Run ${BLUE}./backup_cursor_chats.sh${NC} to create your first backup."
        exit 0
    fi
    
    echo -e "${GREEN}Available backups:${NC}"
    echo ""
    
    for backup in "$BACKUP_DIR"/cursor_chats_*; do
        if [ -d "$backup" ]; then
            BACKUP_NAME=$(basename "$backup")
            BACKUP_DATE=$(echo "$BACKUP_NAME" | sed 's/cursor_chats_//' | sed 's/_/ /' | sed 's/_/:/')
            BACKUP_SIZE=$(du -sh "$backup" | cut -f1)
            
            # Try to get creation date from backup_info.txt
            if [ -f "$backup/backup_info.txt" ]; then
                CREATED=$(grep "Created:" "$backup/backup_info.txt" | cut -d: -f2- | xargs)
                echo -e "  ${BLUE}$BACKUP_NAME${NC}"
                echo -e "    Created: ${GREEN}$CREATED${NC}"
            else
                echo -e "  ${BLUE}$BACKUP_NAME${NC}"
                echo -e "    Date: ${GREEN}$BACKUP_DATE${NC}"
            fi
            echo -e "    Size: ${GREEN}$BACKUP_SIZE${NC}"
            echo ""
        fi
    done
}

# Quiet version for auto-backup
list_backups_quiet() {
    ls -1d "$BACKUP_DIR"/cursor_chats_* 2>/dev/null | wc -l | tr -d ' '
}

# Function to restore from backup
restore_backup() {
    if [ -z "$1" ]; then
        echo -e "${RED}✗${NC} Please specify a backup to restore"
        echo ""
        echo "Usage: $0 --restore <backup_name>"
        echo ""
        echo "Available backups:"
        list_backups_quiet
        list_backups
        exit 1
    fi
    
    RESTORE_BACKUP="$BACKUP_DIR/$1"
    
    if [ ! -d "$RESTORE_BACKUP" ]; then
        echo -e "${RED}✗${NC} Backup not found: $1"
        echo ""
        echo "Available backups:"
        list_backups
        exit 1
    fi
    
    echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  Restore Cursor Chat Backup                   ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}⚠ WARNING:${NC} This will overwrite your current Cursor chat history!"
    echo ""
    echo -e "Backup to restore: ${BLUE}$1${NC}"
    echo -e "Source: ${BLUE}$RESTORE_BACKUP${NC}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        echo -e "${YELLOW}Restore cancelled.${NC}"
        exit 0
    fi
    
    # Make sure Cursor storage exists
    mkdir -p "$CURSOR_STORAGE"
    
    # Restore files
    echo -e "${BLUE}📦 Restoring files...${NC}"
    
    if [ -f "$RESTORE_BACKUP/state.vscdb" ]; then
        cp "$RESTORE_BACKUP/state.vscdb" "$CURSOR_STORAGE/state.vscdb"
        echo -e "  ${GREEN}✓${NC} Restored state.vscdb"
    fi
    
    if [ -f "$RESTORE_BACKUP/state.vscdb.backup" ]; then
        cp "$RESTORE_BACKUP/state.vscdb.backup" "$CURSOR_STORAGE/state.vscdb.backup"
        echo -e "  ${GREEN}✓${NC} Restored state.vscdb.backup"
    fi
    
    if [ -f "$RESTORE_BACKUP/storage.json" ]; then
        cp "$RESTORE_BACKUP/storage.json" "$CURSOR_STORAGE/storage.json"
        echo -e "  ${GREEN}✓${NC} Restored storage.json"
    fi
    
    echo ""
    echo -e "${GREEN}✓${NC} Restore completed!"
    echo -e "${YELLOW}⚠${NC} You may need to restart Cursor for changes to take effect."
}

# Function to show help
show_help() {
    echo "Cursor Chat Backup Script"
    echo ""
    echo "Usage:"
    echo "  $0              Create a new backup"
    echo "  $0 --auto       Create backup (quiet mode for cron)"
    echo "  $0 --list       List all available backups"
    echo "  $0 --restore <name>  Restore from a specific backup"
    echo "  $0 --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Create backup now"
    echo "  $0 --list                             # See all backups"
    echo "  $0 --restore cursor_chats_20241207_153000  # Restore specific backup"
    echo ""
    echo "Backup Location: $BACKUP_DIR"
    echo ""
    echo "To set up automatic backups, add to crontab:"
    echo "  # Backup Cursor chats daily at 2 AM"
    echo "  0 2 * * * cd $WORKSPACE_ROOT && ./backup_cursor_chats.sh --auto"
}

# Main logic
case "$1" in
    --list|-l)
        list_backups
        ;;
    --restore|-r)
        restore_backup "$2"
        ;;
    --help|-h)
        show_help
        ;;
    --auto)
        create_backup --auto
        ;;
    "")
        create_backup
        ;;
    *)
        echo -e "${YELLOW}Unknown option: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

