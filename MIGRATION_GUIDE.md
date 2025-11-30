# Hướng dẫn chuyển đổi sang Alembic

Nếu bạn đã có database với raw SQL migrations cũ, làm theo các bước sau:

## Option 1: Database mới (khuyến nghị cho development)

1. **Xóa database cũ và tạo lại:**
   ```bash
   # Stop containers
   docker-compose down -v
   
   # Start lại (migrations tự chạy)
   docker-compose up -d
   ```

## Option 2: Database đang chạy (production)

1. **Backup database hiện tại:**
   ```bash
   docker exec chatbot_postgres pg_dump -U chatbot_user chatbot_db > backup.sql
   ```

2. **Tạo bảng alembic_version và mark current state:**
   ```bash
   # Connect to database
   docker exec -it chatbot_postgres psql -U chatbot_user -d chatbot_db
   
   # Trong psql:
   CREATE TABLE IF NOT EXISTS alembic_version (
       version_num VARCHAR(32) NOT NULL, 
       CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
   );
   
   # Mark rằng đã có tất cả migrations
   INSERT INTO alembic_version VALUES ('002_triggers');
   
   \q
   ```

3. **Verify:**
   ```bash
   docker exec -it chatbot_backend alembic current
   # Should show: 002_triggers (head)
   ```

## Kiểm tra setup

Chạy các lệnh sau để verify:

```bash
# Check current version
./migrate.sh current

# Xem history
./migrate.sh history

# Test tạo migration mới
./migrate.sh autogenerate test_migration
```

## Lưu ý quan trọng

- ✅ Các migration files trong `database/*.sql` không còn được sử dụng
- ✅ Docker compose đã được update để chạy Alembic
- ✅ Backend container sẽ tự động chạy migrations khi start
- ✅ Sử dụng `migrate.sh` hoặc `migrate.bat` để quản lý migrations

## Rollback nếu có vấn đề

```bash
# Restore from backup
docker exec -i chatbot_postgres psql -U chatbot_user -d chatbot_db < backup.sql
```
