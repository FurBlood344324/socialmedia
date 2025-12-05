# Community role definitions for the Social Media application
# These roles are ONLY used within communities, not for user authentication

CommunityRoles = {
    "admin": {
        "can_delete_posts": True,
        "can_delete_comments": True,
        "can_remove_members": True,
        "can_edit_community": True,
        "can_manage_roles": True
    },
    "moderator": {
        "can_delete_posts": True,
        "can_delete_comments": True,
        "can_remove_members": True,
        "can_edit_community": False,
        "can_manage_roles": False
    },
    "member": {
        "can_delete_posts": False,
        "can_delete_comments": False,
        "can_remove_members": False,
        "can_edit_community": False,
        "can_manage_roles": False
    }
}


def has_community_permission(role: str, permission: str) -> bool:
    """Check if a community role has a specific permission"""
    if role not in CommunityRoles:
        return False
    return CommunityRoles[role].get(permission, False)
