from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('salon', '0001_initial'),
    ]

    operations = [
        # Для каждой таблицы включаем RLS
        migrations.RunSQL(
            "ALTER TABLE salon_sale ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE salon_sale DISABLE ROW LEVEL SECURITY;"
        ),
        migrations.RunSQL(
            "ALTER TABLE salon_service ENABLE ROW LEVEL SECURITY;",
            reverse_sql="ALTER TABLE salon_service DISABLE ROW LEVEL SECURITY;"
        ),
        # Пример политики: сотрудники видят только свои продажи, менеджеры — все
        migrations.RunSQL(
            """
            CREATE POLICY sale_owner_policy
              ON salon_sale
              FOR SELECT USING (
                EXISTS (
                  SELECT 1 
                  FROM salon_employee e 
                  WHERE e.id = current_setting('jwt.claims.user_id')::int 
                    AND (e.is_superuser OR salon_sale.employee_id = e.id)
                )
              );
            """,
            reverse_sql="DROP POLICY IF EXISTS sale_owner_policy ON salon_sale;"
        ),
        # Аналогично для Service
        migrations.RunSQL(
            """
            CREATE POLICY service_owner_policy
              ON salon_service
              FOR SELECT USING (
                EXISTS (
                  SELECT 1 
                  FROM salon_employee e 
                  WHERE e.id = current_setting('jwt.claims.user_id')::int 
                    AND (e.is_superuser OR salon_service.customer_id = e.id)
                )
              );
            """,
            reverse_sql="DROP POLICY IF EXISTS service_owner_policy ON salon_service;"
        ),
    ]
