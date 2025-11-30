# Database Migrations với Alembic

Dự án này sử dụng **Alembic** để quản lý database migrations thay vì raw SQL scripts.

## Cấu trúc

```
backend/
├── alembic/
│   ├── versions/          # Các migration files
│   │   ├── 001_initial.py
│   │   └── 002_triggers.py
│   ├── env.py            # Alembic environment configuration
│   └── script.py.mako    # Template cho migration files
├── alembic.ini           # Alembic configuration
└── app/
    ├── models/           # SQLAlchemy models
    └── database.py       # Database connection
```

## Sử dụng Migrations

### 1. Áp dụng tất cả migrations (upgrade)

**Windows:**
```bash
migrate.bat upgrade
```

**Linux/Mac:**
```bash
./migrate.sh upgrade
```

**Hoặc trực tiếp với Alembic:**
```bash
cd backend
alembic upgrade head
```

### 2. Rollback migration (downgrade)

```bash
# Windows
migrate.bat downgrade

# Linux/Mac
./migrate.sh downgrade

# Hoặc
cd backend
alembic downgrade -1
```

### 3. Xem current migration version

```bash
migrate.bat current
# hoặc
./migrate.sh current
```

### 4. Xem lịch sử migrations

```bash
migrate.bat history
# hoặc
./migrate.sh history
```

### 5. Tạo migration mới (manual)

```bash
migrate.bat create add_user_avatar_field
# hoặc
./migrate.sh create add_user_avatar_field
```

### 6. Auto-generate migration từ models

```bash
migrate.bat autogenerate add_new_user_fields
# hoặc
./migrate.sh autogenerate add_new_user_fields
```

**⚠️ Lưu ý:** Luôn kiểm tra lại migration file được auto-generate trước khi apply!

## Workflow khi phát triển

### Khi thêm/sửa models:

1. **Cập nhật SQLAlchemy models** trong `backend/app/models/`
2. **Auto-generate migration:**
   ```bash
   ./migrate.sh autogenerate describe_your_changes
   ```
3. **Review migration file** trong `backend/alembic/versions/`
4. **Test migration:**
   ```bash
   ./migrate.sh upgrade    # Apply
   ./migrate.sh downgrade  # Rollback to test
   ./migrate.sh upgrade    # Apply again
   ```
5. **Commit** migration file vào Git

### Khi làm việc với Docker:

Migrations tự động chạy khi start container backend:

```yaml
command: >
  bash -c "alembic upgrade head &&
           uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

## Cấu trúc Migration Files

Mỗi migration file có 2 hàm chính:

```python
def upgrade() -> None:
    """Apply changes"""
    # Thêm tables, columns, indexes, etc.
    pass

def downgrade() -> None:
    """Rollback changes"""
    # Xóa những gì đã thêm trong upgrade()
    pass
```

## Migration History hiện tại

1. **001_initial** - Tạo tất cả tables ban đầu (users, bots, training_data, conversations, etc.)
2. **002_triggers** - Thêm database triggers và functions

## Lợi ích của Alembic

✅ **Version control cho database schema** - Track changes như code  
✅ **Rollback support** - Dễ dàng quay lại version cũ  
✅ **Auto-generate migrations** - Tự động phát hiện thay đổi từ models  
✅ **Team collaboration** - Mọi người dùng chung migration history  
✅ **Environment-specific** - Khác nhau cho dev, staging, production  
✅ **Type-safe** - Sử dụng Python thay vì raw SQL  

## Migration Files cũ (deprecated)

Các files sau đây không còn được sử dụng:
- `database/init.sql` ❌
- `database/migration_002_conversation_messages.sql` ❌
- `database/migration_003_cleanup_conversations.sql` ❌
- `database/migration_004_training_jobs.sql` ❌

Tất cả đã được chuyển sang Alembic migrations.

## Troubleshooting

### Migration conflict
```bash
# Xem current version
alembic current

# Xem history
alembic history

# Stamp to specific version (nếu cần)
alembic stamp head
```

### Reset database hoàn toàn
```bash
# Downgrade tất cả
alembic downgrade base

# Upgrade lại
alembic upgrade head
```

### Database URL configuration

Alembic tự động lấy DATABASE_URL từ environment variable hoặc sử dụng default trong `alembic.ini`.

**Environment variable (ưu tiên):**
```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

**Default trong alembic.ini:**
```ini
sqlalchemy.url = postgresql://chatbot_user:chatbot_pass@localhost:5432/chatbot_db
```
