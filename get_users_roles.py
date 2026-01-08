"""
Script to identify superusers and all other users with their roles.
This script queries the PostgreSQL database to display user information.
"""

import os
import sys
import django

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection


def get_all_users_with_roles():
    """
    Fetch all users with their roles and superuser status.
    Returns a list of users with their information.
    """
    query = """
        SELECT 
            u.id,
            u.username,
            u.email,
            u.is_superuser,
            u.record_status,
            r.role_name,
            ur.date_assigned as role_assigned_date
        FROM users_user u
        LEFT JOIN users_userrole ur ON u.id = ur.user_id
        LEFT JOIN users_role r ON ur.role_id = r.id
        WHERE u.record_status = true
        ORDER BY u.is_superuser DESC, u.username ASC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            user_data = dict(zip(columns, row))
            results.append(user_data)
    
    return results


def get_superusers():
    """
    Fetch only superusers.
    """
    query = """
        SELECT 
            u.id,
            u.username,
            u.email,
            u.is_superuser,
            u.record_status,
            u.first_name,
            u.last_name
        FROM users_user u
        WHERE u.is_superuser = true 
          AND u.record_status = true
        ORDER BY u.username ASC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            user_data = dict(zip(columns, row))
            results.append(user_data)
    
    return results


def get_role_permissions(role_id):
    """
    Get function permissions for a specific role.
    """
    query = """
        SELECT 
            rp.function_master_id,
            rp.view,
            rp.create,
            rp.edit,
            rp.delete,
            rp.plant_id
        FROM users_rolepermission rp
        WHERE rp.role_id = %s 
          AND rp.record_status = true
        ORDER BY rp.function_master_id
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [role_id])
        columns = [col[0] for col in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            perm_data = dict(zip(columns, row))
            results.append(perm_data)
    
    return results


def get_role_kpis(role_id):
    """
    Get KPI permissions for a specific role.
    """
    query = """
        SELECT 
            rk.kpi_metric_code
        FROM users_role_kpis rk
        WHERE rk.role_id = %s 
          AND rk.record_status = true
        ORDER BY rk.kpi_metric_code
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query, [role_id])
        results = [row[0] for row in cursor.fetchall()]
    
    return results


def print_users_summary():
    """
    Print a formatted summary of all users and their roles.
    """
    print("\n" + "="*80)
    print("METALQUERY USER SUMMARY")
    print("="*80 + "\n")
    
    # Get superusers
    print("SUPERUSERS:")
    print("-" * 80)
    superusers = get_superusers()
    
    if superusers:
        for user in superusers:
            print(f"\nID: {user['id']}")
            print(f"Username: {user['username']}")
            print(f"Email: {user['email']}")
            print(f"Name: {user['first_name']} {user['last_name']}")
            print(f"Status: Active" if user['record_status'] else "Status: Inactive")
    else:
        print("No superusers found.")
    
    print("\n" + "="*80 + "\n")
    
    # Get all users with roles
    print("ALL USERS WITH ROLES:")
    print("-" * 80)
    all_users = get_all_users_with_roles()
    
    # Group by user to handle multiple roles
    users_dict = {}
    for user_data in all_users:
        user_id = user_data['id']
        if user_id not in users_dict:
            users_dict[user_id] = {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'is_superuser': user_data['is_superuser'],
                'record_status': user_data['record_status'],
                'roles': []
            }
        
        if user_data['role_name']:
            users_dict[user_id]['roles'].append({
                'name': user_data['role_name'],
                'assigned_date': user_data['role_assigned_date']
            })
    
    # Print users
    for user_id, user in users_dict.items():
        print(f"\nUser ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Superuser: {'Yes' if user['is_superuser'] else 'No'}")
        print(f"Status: {'Active' if user['record_status'] else 'Inactive'}")
        
        if user['roles']:
            print(f"Roles:")
            for role in user['roles']:
                print(f"  - {role['name']} (assigned: {role['assigned_date']})")
        else:
            print(f"Roles: No roles assigned")
        
        print("-" * 40)
    
    print("\n" + "="*80 + "\n")


def print_detailed_role_info():
    """
    Print detailed information about each role including permissions.
    """
    query = """
        SELECT id, role_name, role_description
        FROM users_role
        WHERE record_status = true
        ORDER BY role_name
    """
    
    print("ROLE DETAILS WITH PERMISSIONS:")
    print("="*80 + "\n")
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        roles = cursor.fetchall()
        
        for role in roles:
            role_id, role_name, role_desc = role
            print(f"Role: {role_name}")
            print(f"Description: {role_desc or 'N/A'}")
            print(f"Role ID: {role_id}")
            
            # Get function permissions
            permissions = get_role_permissions(role_id)
            if permissions:
                print(f"\nFunction Permissions ({len(permissions)}):")
                for perm in permissions:
                    perms_str = []
                    if perm['view']: perms_str.append('View')
                    if perm['create']: perms_str.append('Create')
                    if perm['edit']: perms_str.append('Edit')
                    if perm['delete']: perms_str.append('Delete')
                    
                    print(f"  - {perm['function_master_id']} (Plant: {perm['plant_id']})")
                    print(f"    Permissions: {', '.join(perms_str) if perms_str else 'None'}")
            else:
                print(f"\nFunction Permissions: None")
            
            # Get KPI permissions
            kpis = get_role_kpis(role_id)
            if kpis:
                print(f"\nKPI Access ({len(kpis)}):")
                for kpi in kpis:
                    print(f"  - {kpi}")
            else:
                print(f"\nKPI Access: None")
            
            print("\n" + "-"*80 + "\n")


if __name__ == "__main__":
    try:
        print_users_summary()
        print_detailed_role_info()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
