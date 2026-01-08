-- ================================================================
-- METALQUERY USERS AND ROLES QUERIES
-- ================================================================
-- Run these queries in your PostgreSQL client to identify users and roles

-- ================================================================
-- 1. GET ALL SUPERUSERS
-- ================================================================
SELECT 
    id,
    username,
    email,
    first_name,
    last_name,
    is_superuser,
    is_active,
    date_joined
FROM users_user
WHERE is_superuser = true 
  AND record_status = true
ORDER BY username;

-- ================================================================
-- 2. GET ALL USERS WITH THEIR ROLES
-- ================================================================
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    u.is_superuser,
    r.role_name,
    r.id as role_id,
    ur.date_assigned as role_assigned_date
FROM users_user u
LEFT JOIN users_userrole ur ON u.id = ur.user_id
LEFT JOIN users_role r ON ur.role_id = r.id
WHERE u.record_status = true
ORDER BY u.is_superuser DESC, u.username ASC;

-- ================================================================
-- 3. GET USERS WITHOUT ANY ROLES
-- ================================================================
SELECT 
    u.id,
    u.username,
    u.email,
    u.first_name,
    u.last_name
FROM users_user u
WHERE u.record_status = true
  AND u.is_superuser = false
  AND u.id NOT IN (SELECT DISTINCT user_id FROM users_userrole)
ORDER BY u.username;

-- ================================================================
-- 4. GET USERS WITH SUPERADMIN ROLE
-- ================================================================
SELECT 
    u.id,
    u.username,
    u.email,
    r.role_name,
    ur.date_assigned
FROM users_user u
JOIN users_userrole ur ON u.id = ur.user_id
JOIN users_role r ON ur.role_id = r.id
WHERE u.record_status = true
  AND r.role_name = 'SuperAdmin'
ORDER BY u.username;

-- ================================================================
-- 5. GET ALL ROLES WITH USER COUNT
-- ================================================================
SELECT 
    r.id as role_id,
    r.role_name,
    COUNT(DISTINCT ur.user_id) as user_count
FROM users_role r
LEFT JOIN users_userrole ur ON r.id = ur.role_id
WHERE r.record_status = true
GROUP BY r.id, r.role_name
ORDER BY user_count DESC, r.role_name;

-- ================================================================
-- 6. GET USER DETAILS WITH ALL ROLES (CONCATENATED)
-- ================================================================
SELECT 
    u.id,
    u.username,
    u.email,
    u.is_superuser,
    STRING_AGG(r.role_name, ', ' ORDER BY r.role_name) as roles
FROM users_user u
LEFT JOIN users_userrole ur ON u.id = ur.user_id
LEFT JOIN users_role r ON ur.role_id = r.id
WHERE u.record_status = true
GROUP BY u.id, u.username, u.email, u.is_superuser
ORDER BY u.is_superuser DESC, u.username;

-- ================================================================
-- 7. GET FUNCTION PERMISSIONS FOR A SPECIFIC ROLE
-- ================================================================
-- Replace <role_id> with actual role ID
SELECT 
    rp.role_id,
    r.role_name,
    rp.function_master_id,
    rp.plant_id,
    rp.view,
    rp.create,
    rp.edit,
    rp.delete
FROM users_rolepermission rp
JOIN users_role r ON rp.role_id = r.id
WHERE rp.role_id = <role_id>
  AND rp.record_status = true
ORDER BY rp.function_master_id;

-- ================================================================
-- 8. GET KPI PERMISSIONS FOR A SPECIFIC ROLE
-- ================================================================
-- Replace <role_id> with actual role ID
SELECT 
    rk.role_id,
    r.role_name,
    rk.kpi_metric_code
FROM users_role_kpis rk
JOIN users_role r ON rk.role_id = r.id
WHERE rk.role_id = <role_id>
  AND rk.record_status = true
ORDER BY rk.kpi_metric_code;

-- ================================================================
-- 9. GET USER'S TOKEN INFORMATION
-- ================================================================
-- Replace <username> with actual username
SELECT 
    u.id,
    u.username,
    ut.token,
    ut.plant_id,
    ut.created_at as token_created,
    u.is_superuser
FROM users_user u
JOIN users_usertoken ut ON u.id = ut.user_id
WHERE u.username = '<username>'
  AND u.record_status = true;

-- ================================================================
-- 10. GET COMPLETE USER RBAC INFORMATION
-- ================================================================
-- Replace <username> with actual username
SELECT 
    u.id as user_id,
    u.username,
    u.email,
    u.is_superuser,
    r.id as role_id,
    r.role_name,
    ur.date_assigned,
    rp.function_master_id,
    rp.plant_id,
    rp.view,
    rp.create,
    rp.edit,
    rp.delete
FROM users_user u
LEFT JOIN users_userrole ur ON u.id = ur.user_id
LEFT JOIN users_role r ON ur.role_id = r.id
LEFT JOIN users_rolepermission rp ON r.id = rp.role_id AND rp.record_status = true
WHERE u.username = '<username>'
  AND u.record_status = true
ORDER BY r.role_name, rp.function_master_id;

-- ================================================================
-- 11. COUNT STATISTICS
-- ================================================================
SELECT 
    'Total Active Users' as metric,
    COUNT(*) as count
FROM users_user
WHERE record_status = true

UNION ALL

SELECT 
    'Superusers' as metric,
    COUNT(*) as count
FROM users_user
WHERE record_status = true AND is_superuser = true

UNION ALL

SELECT 
    'Users with Roles' as metric,
    COUNT(DISTINCT user_id) as count
FROM users_userrole

UNION ALL

SELECT 
    'Users without Roles' as metric,
    COUNT(*) as count
FROM users_user u
WHERE record_status = true
  AND is_superuser = false
  AND id NOT IN (SELECT DISTINCT user_id FROM users_userrole)

UNION ALL

SELECT 
    'Total Roles' as metric,
    COUNT(*) as count
FROM users_role
WHERE record_status = true;





------------------------------******-------------------------------------
Here's a SQL query to get username, token, and KPI permissions:

sql
-- Get users with their tokens and KPI permissions
SELECT 
    u.username,
    u.is_superuser,
    STRING_AGG(DISTINCT r.role_name, ', ') as roles,
    ut.token,
    STRING_AGG(DISTINCT rk.kpi_metric_code, ', ') as kpi_permissions
FROM users_user u
JOIN users_usertoken ut ON u.id = ut.user_id
LEFT JOIN users_userrole ur ON u.id = ur.user_id
LEFT JOIN users_role r ON ur.role_id = r.id
LEFT JOIN users_role_kpis rk ON r.id = rk.role_id AND rk.record_status = true
WHERE u.record_status = true
GROUP BY u.id, u.username, u.is_superuser, ut.token
ORDER BY u.is_superuser DESC, u.username;
Detailed Version (Shows each KPI separately)
sql
-- Get detailed KPI permissions per user
SELECT 
    u.username,
    u.is_superuser,
    r.role_name,
    ut.token,
    rk.kpi_metric_code as kpi_permission
FROM users_user u
JOIN users_usertoken ut ON u.id = ut.user_id
LEFT JOIN users_userrole ur ON u.id = ur.user_id
LEFT JOIN users_role r ON ur.role_id = r.id
LEFT JOIN users_role_kpis rk ON r.id = rk.role_id AND rk.record_status = true
WHERE u.record_status = true
ORDER BY u.username, r.role_name, rk.kpi_metric_code;
Get Specific User's KPI Permissions
sql
-- Replace 'amogh' with username
SELECT 
    u.username,
    ut.token,
    r.role_name,
    rk.kpi_metric_code
FROM users_user u
JOIN users_usertoken ut ON u.id = ut.user_id
LEFT JOIN users_userrole ur ON u.id = ur.user_id
LEFT JOIN users_role r ON ur.role_id = r.id
LEFT JOIN users_role_kpis rk ON r.id = rk.role_id AND rk.record_status = true
WHERE u.username = 'amogh'
  AND u.record_status = true;


// Replace 'YOUR_TOKEN_HERE' with the actual token from your SQL query
localStorage.setItem('authToken', 'YOUR_TOKEN_HERE');