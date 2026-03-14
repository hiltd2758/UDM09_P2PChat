# P2P Chat Application
**Project Code:** UDM_09

**Class:** 012012301305

**Group:** 09

## Tech Stack
- Language: Python 3.13
- UI: Tkinter (built-in)
- Network: socket + threading (built-in)
- IDE: VS Code

### 1. Clone repository (CMD)
```bash
git clone https://github.com/hiltd2758/UDM09_P2PChat.git
cd UDM09_P2PChat
code .
```

### 2. kiểm tra branch
```bash
git branch -a                # Xem tất cả branch (local + remote)
git branch                   # Chỉ branch local

# Pull code mới nhất từ main (default branch)
git checkout main
git pull origin main
```

### 3. Branch (ví dụ: feature/chat-ui)
```bash
git checkout -b feature/chat-ui
```

### 4. Code xong → add → commit → push
```bash
# Kiểm tra thay đổi
git status

# Add file 
git add .
# Hoặc add cụ thể:
# git add Code/P2PChat/views/ Code/P2PChat/main.py requirements.txt

# Commit với message rõ ràng
git commit -m "context"

# Push branch lên GitHub (lần đầu push branch mới cần -u)
git push -u origin feature/chat-ui
# Lần sau chỉ cần:
# git push
```

