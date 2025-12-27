# How to Grant yabai Accessibility Permissions

## Step-by-Step Instructions

### For macOS Ventura and later (including macOS 26):

1. **Open System Settings**
   - Click the Apple menu (🍎) in the top-left corner
   - Select **System Settings**
   - Or press `Cmd + Space` and type "System Settings"

2. **Navigate to Privacy & Security**
   - In the left sidebar, click **Privacy & Security**
   - Or search for "Privacy" in the search bar

3. **Open Accessibility**
   - Scroll down to find **Accessibility** in the list
   - Click on it

4. **Add yabai**
   - Click the **+** (plus) button at the bottom left of the list
   - A file browser will open
   - Press `Cmd + Shift + G` to open "Go to folder"
   - Type or paste: `/Users/freedom/.local/bin`
   - Press Enter
   - Select **yabai** from the list
   - Click **Open**

5. **Enable the Permission**
   - Make sure the checkbox next to **yabai** is **checked/enabled**
   - If it's not checked, click it to enable

6. **Verify**
   - You should see **yabai** in the list with a checkmark
   - Close System Settings

## Alternative: Quick Path Method

If the above doesn't work, you can also:

1. Open System Settings > Privacy & Security > Accessibility
2. Click the **+** button
3. Navigate directly to: `/Users/freedom/.local/bin/yabai`
4. Select it and enable the checkbox

## After Granting Permissions

Once permissions are granted:

```bash
# Restart yabai service
yabai --restart-service

# Verify it's working
yabai --check-service
```

## Troubleshooting

**If yabai doesn't appear in the list:**
- Make sure you're adding the file at `/Users/freedom/.local/bin/yabai`
- Check that yabai exists: `ls -la ~/.local/bin/yabai`

**If permissions are granted but yabai still doesn't work:**
- Try restarting yabai: `yabai --restart-service`
- Check logs: `tail -f /tmp/yabai_freedom.out.log`
- Make sure SIP is enabled (for basic features) or properly configured (for advanced features)

## Visual Guide

The Accessibility settings should look like this:
```
Privacy & Security
  └── Accessibility
      ├── [✓] yabai  ← Should be checked
      ├── [ ] Other apps...
      └── [+] button at bottom
```


