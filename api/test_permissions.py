#!/usr/bin/env python
"""Test script for Role-Based Access Control (RBAC) system."""

import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.permissions import (
    Role, Permission, ROLE_PERMISSIONS, ROLE_QUOTAS,
    has_permission, get_role_permissions, get_role_quota,
    can_access_resource, get_role_info
)


def test_role_definitions():
    """Test that all roles are properly defined."""
    print("Testing role definitions...")

    # Test all roles exist
    assert Role.ADMIN == 'admin'
    assert Role.MODERATOR == 'moderator'
    assert Role.PREMIUM == 'premium'
    assert Role.USER == 'user'
    assert Role.GUEST == 'guest'

    # Test all roles have permissions mapping
    for role in Role:
        assert role in ROLE_PERMISSIONS
        assert role in ROLE_QUOTAS

    print("✅ Role definitions passed")


def test_admin_permissions():
    """Test Admin role permissions - should only manage system, NOT create content."""
    print("\nTesting Admin permissions...")

    admin_perms = ROLE_PERMISSIONS[Role.ADMIN]

    # Admin SHOULD have these permissions
    assert Permission.MANAGE_USERS in admin_perms
    assert Permission.VIEW_USERS in admin_perms
    assert Permission.BAN_USERS in admin_perms
    assert Permission.MANAGE_ALL_CONTENT in admin_perms
    assert Permission.DELETE_ANY_CONTENT in admin_perms
    assert Permission.VIEW_ALL_CONTENT in admin_perms

    # Admin should NOT have content creation permissions
    assert Permission.CREATE_WORLD not in admin_perms
    assert Permission.CREATE_STORY not in admin_perms
    assert Permission.CREATE_EVENT not in admin_perms
    assert Permission.EDIT_OWN_WORLD not in admin_perms
    assert Permission.EDIT_OWN_STORY not in admin_perms
    assert Permission.EDIT_OWN_EVENT not in admin_perms
    assert Permission.DELETE_OWN_WORLD not in admin_perms
    assert Permission.DELETE_OWN_STORY not in admin_perms
    assert Permission.DELETE_OWN_EVENT not in admin_perms
    assert Permission.SHARE_WORLD not in admin_perms
    assert Permission.SHARE_STORY not in admin_perms

    # Admin should NOT have GPT permissions
    assert Permission.USE_GPT not in admin_perms
    assert Permission.USE_GPT_UNLIMITED not in admin_perms

    print("✅ Admin permissions passed")


def test_admin_quotas():
    """Test Admin quotas - should be 0 for content creation."""
    print("\nTesting Admin quotas...")

    admin_quotas = ROLE_QUOTAS[Role.ADMIN]

    # Admin should have 0 quota for content
    assert admin_quotas['public_worlds_limit'] == 0
    assert admin_quotas['public_stories_limit'] == 0
    assert admin_quotas['gpt_requests_per_day'] == 0

    print("✅ Admin quotas passed")


def test_moderator_permissions():
    """Test Moderator role - can create content AND manage others' content."""
    print("\nTesting Moderator permissions...")

    mod_perms = ROLE_PERMISSIONS[Role.MODERATOR]

    # Moderator should have content creation permissions
    assert Permission.CREATE_WORLD in mod_perms
    assert Permission.CREATE_STORY in mod_perms
    assert Permission.CREATE_EVENT in mod_perms
    assert Permission.EDIT_OWN_WORLD in mod_perms
    assert Permission.EDIT_OWN_STORY in mod_perms
    assert Permission.EDIT_OWN_EVENT in mod_perms
    assert Permission.DELETE_OWN_WORLD in mod_perms
    assert Permission.DELETE_OWN_STORY in mod_perms
    assert Permission.DELETE_OWN_EVENT in mod_perms

    # Moderator should have content management permissions
    assert Permission.VIEW_ALL_CONTENT in mod_perms
    assert Permission.DELETE_ANY_CONTENT in mod_perms
    assert Permission.VIEW_USERS in mod_perms

    # Moderator should have GPT
    assert Permission.USE_GPT in mod_perms

    # Moderator should NOT have user management
    assert Permission.MANAGE_USERS not in mod_perms

    print("✅ Moderator permissions passed")


def test_user_permissions():
    """Test regular User role - basic content creation."""
    print("\nTesting User permissions...")

    user_perms = ROLE_PERMISSIONS[Role.USER]

    # User should have basic content permissions
    assert Permission.CREATE_WORLD in user_perms
    assert Permission.CREATE_STORY in user_perms
    assert Permission.CREATE_EVENT in user_perms
    assert Permission.EDIT_OWN_WORLD in user_perms
    assert Permission.EDIT_OWN_STORY in user_perms
    assert Permission.EDIT_OWN_EVENT in user_perms
    assert Permission.DELETE_OWN_WORLD in user_perms
    assert Permission.DELETE_OWN_STORY in user_perms
    assert Permission.DELETE_OWN_EVENT in user_perms
    assert Permission.SHARE_WORLD in user_perms
    assert Permission.SHARE_STORY in user_perms
    assert Permission.USE_GPT in user_perms

    # User should NOT have management permissions
    assert Permission.MANAGE_USERS not in user_perms
    assert Permission.VIEW_USERS not in user_perms
    assert Permission.BAN_USERS not in user_perms
    assert Permission.DELETE_ANY_CONTENT not in user_perms
    assert Permission.MANAGE_ALL_CONTENT not in user_perms

    print("✅ User permissions passed")


def test_premium_permissions():
    """Test Premium user role - enhanced content creation."""
    print("\nTesting Premium permissions...")

    premium_perms = ROLE_PERMISSIONS[Role.PREMIUM]

    # Premium should have all basic content permissions
    assert Permission.CREATE_WORLD in premium_perms
    assert Permission.CREATE_STORY in premium_perms
    assert Permission.CREATE_EVENT in premium_perms
    assert Permission.USE_GPT in premium_perms

    # Premium should have unlimited GPT
    assert Permission.USE_GPT_UNLIMITED in premium_perms

    # Premium should have increased quota
    assert Permission.INCREASED_QUOTA in premium_perms

    print("✅ Premium permissions passed")


def test_guest_permissions():
    """Test Guest role - read-only."""
    print("\nTesting Guest permissions...")

    guest_perms = ROLE_PERMISSIONS[Role.GUEST]

    # Guest should have no permissions
    assert len(guest_perms) == 0

    # Verify guest quotas are 0
    guest_quotas = ROLE_QUOTAS[Role.GUEST]
    assert guest_quotas['public_worlds_limit'] == 0
    assert guest_quotas['public_stories_limit'] == 0
    assert guest_quotas['gpt_requests_per_day'] == 0

    print("✅ Guest permissions passed")


def test_has_permission_function():
    """Test has_permission helper function."""
    print("\nTesting has_permission function...")

    # Admin should NOT have CREATE_WORLD
    assert has_permission('admin', Permission.CREATE_WORLD) == False
    assert has_permission('admin', Permission.MANAGE_USERS) == True

    # User should have CREATE_WORLD
    assert has_permission('user', Permission.CREATE_WORLD) == True
    assert has_permission('user', Permission.MANAGE_USERS) == False

    # Moderator should have both content and management
    assert has_permission('moderator', Permission.CREATE_WORLD) == True
    assert has_permission('moderator', Permission.DELETE_ANY_CONTENT) == True

    # Invalid role should return False
    assert has_permission('invalid_role', Permission.CREATE_WORLD) == False

    print("✅ has_permission function passed")


def test_get_role_quota_function():
    """Test get_role_quota helper function."""
    print("\nTesting get_role_quota function...")

    # Test admin quotas (should be 0)
    assert get_role_quota('admin', 'public_worlds_limit') == 0
    assert get_role_quota('admin', 'public_stories_limit') == 0
    assert get_role_quota('admin', 'gpt_requests_per_day') == 0

    # Test user quotas
    assert get_role_quota('user', 'public_worlds_limit') == 1
    assert get_role_quota('user', 'public_stories_limit') == 20
    assert get_role_quota('user', 'gpt_requests_per_day') == 50

    # Test moderator quotas
    assert get_role_quota('moderator', 'public_worlds_limit') == 20
    assert get_role_quota('moderator', 'public_stories_limit') == 100
    assert get_role_quota('moderator', 'gpt_requests_per_day') == 500

    # Test premium quotas
    assert get_role_quota('premium', 'public_worlds_limit') == 10
    assert get_role_quota('premium', 'public_stories_limit') == 50
    assert get_role_quota('premium', 'gpt_requests_per_day') == 200

    # Invalid role should default to USER quota
    assert get_role_quota('invalid_role', 'public_worlds_limit') == 1
    assert get_role_quota('invalid_role', 'public_stories_limit') == 20

    print("✅ get_role_quota function passed")


def test_can_access_resource_function():
    """Test can_access_resource helper function."""
    print("\nTesting can_access_resource function...")

    # Admin can access everything
    assert can_access_resource('admin', 'user') == True
    assert can_access_resource('admin', 'admin') == True
    assert can_access_resource('admin', 'moderator') == True

    # Moderator can access user/premium/moderator content
    assert can_access_resource('moderator', 'user') == True
    assert can_access_resource('moderator', 'premium') == True
    assert can_access_resource('moderator', 'moderator') == True
    assert can_access_resource('moderator', 'admin') == False

    # Users can only access their own content
    assert can_access_resource('user', 'user') == True
    assert can_access_resource('user', 'admin') == False
    assert can_access_resource('user', 'moderator') == False

    print("✅ can_access_resource function passed")


def test_role_info():
    """Test role display information."""
    print("\nTesting role display info...")

    # Test admin role info
    admin_info = get_role_info('admin')
    assert admin_info['label'] == 'Quản trị viên'
    assert admin_info['icon'] == '👑'
    assert admin_info['badge_color'] == 'badge-error'
    assert 'không tạo nội dung' in admin_info['description'].lower()

    # Test moderator role info
    mod_info = get_role_info('moderator')
    assert mod_info['label'] == 'Kiểm duyệt viên'
    assert mod_info['icon'] == '🛡️'
    assert mod_info['badge_color'] == 'badge-warning'

    # Test user role info
    user_info = get_role_info('user')
    assert user_info['label'] == 'Người dùng'
    assert user_info['icon'] == '👤'
    assert user_info['badge_color'] == 'badge-info'

    print("✅ Role display info passed")


def test_quota_hierarchy():
    """Test that quota increases with role tier."""
    print("\nTesting quota hierarchy...")

    # Guest < User < Premium < Moderator for content quotas
    assert get_role_quota('guest', 'public_worlds_limit') < get_role_quota('user', 'public_worlds_limit')
    assert get_role_quota('user', 'public_worlds_limit') < get_role_quota('premium', 'public_worlds_limit')
    assert get_role_quota('premium', 'public_worlds_limit') < get_role_quota('moderator', 'public_worlds_limit')

    # Admin has 0 (special case - not for content creation)
    assert get_role_quota('admin', 'public_worlds_limit') == 0

    print("✅ Quota hierarchy passed")


def main():
    """Run all permission tests."""
    print("="*70)
    print("  RBAC PERMISSIONS - TEST SUITE")
    print("="*70 + "\n")

    try:
        test_role_definitions()
        test_admin_permissions()
        test_admin_quotas()
        test_moderator_permissions()
        test_user_permissions()
        test_premium_permissions()
        test_guest_permissions()
        test_has_permission_function()
        test_get_role_quota_function()
        test_can_access_resource_function()
        test_role_info()
        test_quota_hierarchy()

        print("\n" + "="*70)
        print("  ✅ ALL PERMISSION TESTS PASSED")
        print("="*70)
        print("\nKey Findings:")
        print("  • Admin: System management ONLY (0 content quota)")
        print("  • Moderator: Content creation + moderation (20/100 quota)")
        print("  • Premium: Enhanced content creation (10/50 quota)")
        print("  • User: Basic content creation (1/20 quota)")
        print("  • Guest: Read-only access (0/0/0 quota)")
        return 0

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
