# Cursor Chat Backup System

This directory contains backups of your Cursor chat history to prevent loss of important conversations.

## Quick Start

### Create a Backup
```bash
./backup_cursor_chats.sh
```

### List All Backups
```bash
./backup_cursor_chats.sh --list
```

### Restore from Backup
```bash
./backup_cursor_chats.sh --restore cursor_chats_20251207_160004
```

## Automatic Backups

To set up daily automatic backups, add this to your crontab:

```bash
# Edit crontab
crontab -e

# Add this line for daily backups at 2 AM
0 2 * * * cd /Users/freedom/QUANTS && ./backup_cursor_chats.sh --auto
```

Or for weekly backups (every Sunday at 2 AM):
```bash
0 2 * * 0 cd /Users/freedom/QUANTS && ./backup_cursor_chats.sh --auto
```

## What Gets Backed Up

- **state.vscdb** - Main chat database (contains all your conversations)
- **state.vscdb.backup** - Backup database file
- **storage.json** - Settings and metadata
- **globalStorage_full.tar.gz** - Complete archive of all Cursor storage

## Backup Location

Backups are stored in: `/Users/freedom/QUANTS/.cursor/chat_backups/`

Each backup is stored in a timestamped directory:
- Format: `cursor_chats_YYYYMMDD_HHMMSS`
- Example: `cursor_chats_20251207_160004`

## Storage Management

The script keeps all backups by default. To manage storage:

1. **List backups** to see what you have:
   ```bash
   ./backup_cursor_chats.sh --list
   ```

2. **Manually delete old backups** if needed:
   ```bash
   rm -rf .cursor/chat_backups/cursor_chats_YYYYMMDD_HHMMSS
   ```

3. **Keep only recent backups** - The script will warn you if you have more than 10 backups.

## Restore Process

⚠️ **Warning**: Restoring will overwrite your current chat history!

1. List available backups:
   ```bash
   ./backup_cursor_chats.sh --list
   ```

2. Restore a specific backup:
   ```bash
   ./backup_cursor_chats.sh --restore cursor_chats_20251207_160004
   ```

3. Restart Cursor for changes to take effect.

## Troubleshooting

### "Cursor storage directory not found"
- Make sure Cursor has been installed and used at least once
- Check that the path exists: `~/Library/Application Support/Cursor/User/globalStorage`

### "File may be locked"
- Close Cursor before running the backup
- The database files are locked while Cursor is running

### Large backup sizes
- Chat databases can be large (hundreds of MB)
- Consider archiving old backups to external storage
- The full archive is compressed to save space

## Notes

- Backups are stored locally in your workspace
- The backup directory is excluded from git (see `.gitignore`)
- Each backup includes metadata in `backup_info.txt`
- Backups are timestamped for easy identification

