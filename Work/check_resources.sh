#!/bin/bash
# Quick Resource Check Script
# Shows current system resource usage

echo "📊 System Resource Status"
echo "================================================================================
"
echo "🖥️  CPU Usage:"
top -l 1 | grep "CPU usage" | awk '{print "   " $0}'
echo ""

echo "💾 Memory Status:"
vm_stat | grep -E "Pages free|Pages active|Pages inactive|Pages wired|page size" | \
    awk '{
        if ($0 ~ /page size/) {page_size=$8}
        if ($0 ~ /Pages free/) {free=$3; gsub(/\./, "", free)}
        if ($0 ~ /Pages active/) {active=$3; gsub(/\./, "", active)}
        if ($0 ~ /Pages inactive/) {inactive=$3; gsub(/\./, "", inactive)}
        if ($0 ~ /Pages wired/) {wired=$4; gsub(/\./, "", wired)}
    }
    END {
        free_mb = (free * page_size) / 1024 / 1024
        active_mb = (active * page_size) / 1024 / 1024  
        inactive_mb = (inactive * page_size) / 1024 / 1024
        wired_mb = (wired * page_size) / 1024 / 1024
        total_mb = free_mb + active_mb + inactive_mb + wired_mb
        free_gb = free_mb / 1024
        total_gb = total_mb / 1024
        
        printf "   Free:      %.2f GB (%.1f%%)\n", free_gb, (free_mb/total_mb)*100
        printf "   Active:    %.2f GB\n", active_mb/1024
        printf "   Inactive:  %.2f GB (can be freed)\n", inactive_mb/1024
        printf "   Wired:     %.2f GB\n", wired_mb/1024
        printf "   Total:     %.2f GB\n", total_gb
    }'
echo ""

echo "💿 Disk Usage:"
df -h / | tail -1 | awk '{printf "   Used: %s / %s (%s)\n", $3, $2, $5}'
echo ""

echo "🔥 Top 5 Memory Consumers:"
ps aux | sort -rk 3,3 | head -6 | tail -5 | awk '{printf "   %6.1f MB  %s\n", $3/1024, $11}'
echo ""

echo "🐍 Python Processes:"
PYTHON_PROCS=$(ps aux | grep -i python | grep -v grep | wc -l | tr -d ' ')
if [ "$PYTHON_PROCS" -gt 0 ]; then
    ps aux | grep -i python | grep -v grep | awk '{printf "   PID %s: %s (%.1f MB)\n", $2, $11, $3/1024}'
else
    echo "   No Python processes running"
fi
echo ""

echo "📦 Node Processes:"
NODE_PROCS=$(ps aux | grep -i node | grep -v grep | wc -l | tr -d ' ')
if [ "$NODE_PROCS" -gt 0 ]; then
    ps aux | grep -i node | grep -v grep | awk '{printf "   PID %s: %s (%.1f MB)\n", $2, $11, $3/1024}'
else
    echo "   No Node processes running"
fi
echo ""

echo "💡 Quick Actions:"
echo "   • Free memory: ./free_memory.sh"
echo "   • Close apps: killall [AppName]"
echo "   • Full report: See RAM_USAGE_REPORT.txt"
echo ""

