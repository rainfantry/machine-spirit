# SSH Setup & Troubleshooting Guide
## Linux VPS / Parrot OS / Any Debian-Based System

---

## 1. Install & Start SSH Server

```bash
sudo apt update && sudo apt install openssh-server -y
sudo systemctl enable ssh --now
sudo systemctl status ssh
```

If status shows **failed**, check config first:
```bash
sudo sshd -t
```
This prints the exact error and line number. Fix it, then restart.

---

## 2. Check SSH is Actually Listening

```bash
ss -tlnp | grep 22
```

Should show something like:
```
LISTEN 0 128 0.0.0.0:22 0.0.0.0:*
```

If nothing — SSH isn't running. Go back to step 1.

---

## 3. Get Your IP

```bash
ip a | grep inet | grep -v 127.0.0.1
```

Use the `192.168.x.x` address for local network connections.

---

## 4. SSH Config File

Location: `/etc/ssh/sshd_config`

### Password Authentication (simplest)
```bash
sudo nano /etc/ssh/sshd_config
```

Set these:
```
PasswordAuthentication yes
PermitRootLogin no
PubkeyAuthentication yes
```

**IMPORTANT**: After ANY config change:
```bash
sudo sshd -t              # check for syntax errors FIRST
sudo systemctl restart ssh  # then restart
```

### If You Have No Password Set
```bash
sudo passwd YOUR_USERNAME
```

Type new password twice. Now password auth works.

---

## 5. Key-Based Authentication

### Generate Key (on the CLIENT machine)
```bash
ssh-keygen -t ed25519 -C "your@email.com"
```

- Default path: `~/.ssh/id_ed25519` (private) and `~/.ssh/id_ed25519.pub` (public)
- Passphrase: optional, adds extra security

### Copy Public Key to Server
**Method 1 — ssh-copy-id (easiest, needs password auth working first):**
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server-ip
```

**Method 2 — manual:**
```bash
# On the CLIENT, display the public key:
cat ~/.ssh/id_ed25519.pub

# On the SERVER, paste it:
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "PASTE_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Test Key Auth
```bash
ssh user@server-ip
```

Should connect without asking for password.

---

## 6. Key Auth for Mobile (Termius / JuiceSSH)

### Option A: Generate key in app, export public key to server
1. In Termius: Keychain → Generate Key → ed25519
2. Copy the **public key** from the app
3. Paste into server's `~/.ssh/authorized_keys`

### Option B: Use existing key from another machine
1. Copy your `~/.ssh/id_ed25519` (PRIVATE key) content
2. Import into Termius: Keychain → Add Key → paste
3. The matching public key must already be in server's `authorized_keys`

### Option C: Just use password (no keys)
1. Set password on server: `sudo passwd USERNAME`
2. Ensure `PasswordAuthentication yes` in sshd_config
3. In Termius: New Host → IP, port 22, username, password. Done.

---

## 7. Troubleshooting

### SSH Service Crash-Looping ("start request repeated too quickly")
```bash
sudo sshd -t
```
Fix whatever it reports. Common causes:
- Typo in `/etc/ssh/sshd_config`
- Duplicate directives
- Bad key file permissions
- Missing host keys

### Regenerate Host Keys (if missing/corrupted)
```bash
sudo rm /etc/ssh/ssh_host_*
sudo ssh-keygen -A
sudo systemctl restart ssh
```

### "Connection Refused"
- SSH not running: `sudo systemctl start ssh`
- Wrong port: check `Port` in sshd_config
- Firewall blocking: `sudo ufw allow 22`

### "Permission Denied (publickey)"
- Public key not in `authorized_keys`
- Wrong permissions:
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```
- Wrong owner: `chown -R $USER:$USER ~/.ssh`

### "Permission Denied (password)"
- Password auth disabled: set `PasswordAuthentication yes` in sshd_config
- No password set: `sudo passwd USERNAME`
- Wrong password: try again or reset it

### "Host Key Verification Failed"
Server changed or reinstalled. Fix on client:
```bash
ssh-keygen -R server-ip
```

### Check Auth Logs (on server)
```bash
sudo journalctl -u ssh --no-pager -n 30
```
or
```bash
sudo tail -30 /var/log/auth.log
```

---

## 8. Lock Down After Setup (Optional — Security Hardening)

Once key auth is working and tested:
```bash
sudo nano /etc/ssh/sshd_config
```

```
PasswordAuthentication no
PermitRootLogin no
MaxAuthTries 3
```

```bash
sudo sshd -t && sudo systemctl restart ssh
```

**WARNING**: Only disable password auth AFTER confirming key auth works. Otherwise you lock yourself out.

---

## 9. Quick Reference

| Task | Command |
|------|---------|
| Start SSH | `sudo systemctl start ssh` |
| Stop SSH | `sudo systemctl stop ssh` |
| Restart SSH | `sudo systemctl restart ssh` |
| Status | `sudo systemctl status ssh` |
| Check config | `sudo sshd -t` |
| Check port | `ss -tlnp \| grep 22` |
| Get IP | `ip a \| grep inet` |
| Auth logs | `sudo journalctl -u ssh -n 30` |
| Set password | `sudo passwd USERNAME` |
| Gen key | `ssh-keygen -t ed25519` |
| Copy key | `ssh-copy-id -i ~/.ssh/id_ed25519.pub user@ip` |
| Fix known hosts | `ssh-keygen -R server-ip` |
| Regen host keys | `sudo ssh-keygen -A` |
