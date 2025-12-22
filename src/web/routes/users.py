from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..auth_decorators import any_admin_required, super_admin_required
from ...utils.apiClient import api_client
from ...utils import Helpers

users_bp = Blueprint('users', __name__)

@users_bp.route('/users')
@any_admin_required
def list_users():
    """List all users - now calls API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')
    
    # 🔄 Call API for users list
    params = {
        'page': page,
        'per_page': per_page,
        'search': search,
        'sort': sort
    }
    
    response = api_client.get('/api/v1/users', params)
    
    # 🔄 Call API for user statistics
    stats_response = api_client.get('/api/v1/users/stats')
    
    # Handle API responses
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading users: {response.get('message', 'Unknown error')}", 'error')
        users = []
        pagination_data = {}
    else:
        users = response.get('data', [])
        pagination_data = response.get('pagination', {})
    
    # Handle stats response
    if not stats_response.get('success'):
        # Fallback stats if API fails
        stats = {
            'total_users': len(users),
            'active_today': 0,
            'premium_users': 0,
            'new_users_today': 0
        }
    else:
        stats = stats_response.get('data', {})
    
    return render_template('user/index.html', 
                         users=users,
                         stats=stats,  # ✅ Pass stats to template
                         # Individual pagination variables
                         page=pagination_data.get('page', 1),
                         per_page=pagination_data.get('per_page', 20),
                         total=pagination_data.get('total', 0),
                         total_pages=pagination_data.get('total_pages', 1),
                         has_next=pagination_data.get('has_next', False),
                         has_prev=pagination_data.get('has_prev', False),
                         # Also pass the full pagination object
                         pagination=pagination_data,
                         search=search,
                         sort=sort)

@users_bp.route('/users/<user_id>')
@any_admin_required
def view_user(user_id):
    """View single user - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.get(f'/api/v1/users/{user_id}')
    
    if not response.get('success'):
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"Error loading user: {response.get('message', 'User not found')}", 'error')
        return redirect(url_for('users.list_users'))
    
    user = response.get('data')
    return render_template('user/view.html', user=user)

@users_bp.route('/users/delete/<user_id>', methods=['POST'])
@super_admin_required
def delete_user(user_id):
    """Delete user - now calls API"""
    # 🔄 Call API instead of service
    response = api_client.delete(f'/api/v1/users/{user_id}')
    
    if response.get('success'):
        flash(' User deleted successfully!', 'success')
    else:
        if response.get('redirect_to_login'):
            flash('Session expired. Please login again.', 'error')
            return redirect(url_for('auth.login'))
        
        flash(f"❌ Error deleting user: {response.get('message', 'Unknown error')}", 'error')
    
    return redirect(url_for('users.list_users'))

@users_bp.route('/users/toggle-status/<user_id>', methods=['POST'])
@super_admin_required
def toggle_status(user_id):
    """Toggle user active status (super admin only)"""
    # 🔄 Call API instead of using service directly
    response = api_client.put(f'/api/v1/users/{user_id}/toggle-status')
    
    if response.get('success'):
        return jsonify(response)
    else:
        if response.get('redirect_to_login'):
            return jsonify({'success': False, 'message': 'Session expired'})
        
        return jsonify({
            'success': False, 
            'message': response.get('message', 'Error updating user status')
        })

@users_bp.route('/users/api/stats')
@any_admin_required
def user_stats():
    """API endpoint for user statistics"""
    db = SessionLocal()
    try:
        users = user_service.get_all_users(db)  #  Use service method
        
        stats = {
            "total_users": len(users),
            "active_users": len([u for u in users if u.is_active]),
            "inactive_users": len([u for u in users if not u.is_active]),
            "recent_users": len([u for u in users if u.created_at])
        }
        
        return jsonify({"success": True, "stats": stats})
    finally:
        db.close()

@users_bp.route('/users/search')
@any_admin_required
def search_users():
    """Search users by name, username, or telegram ID"""
    db = SessionLocal()
    try:
        search_term = request.args.get('q', '').lower()
        
        users = user_service.get_all_users(db)  #  Use service method
        
        # Filter users based on search term
        filtered_users = [
            u for u in users
            if search_term in (u.full_name or '').lower()
            or search_term in (u.username or '').lower()
            or search_term in str(u.telegram_id)
        ]
        
        return jsonify({
            "success": True,
            "users": [{
                "id": u.id,
                "telegram_id": u.telegram_id,
                "full_name": u.full_name,
                "username": u.username,
                "is_active": u.is_active
            } for u in filtered_users]
        })
    finally:
        db.close()

@users_bp.route('/users/send-message', methods=['POST'])
@any_admin_required
def send_message_to_user():
    """Send message to user via Telegram bot"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        message = data.get('message')
        
        if not telegram_id or not message:
            return jsonify({
                'success': False,
                'message': 'Missing telegram_id or message'
            })
        
        # Get bot token from environment
        bot_token = os.getenv('BOT_TOKEN') or os.getenv('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({
                'success': False,
                'message': 'Bot token not configured'
            })
        
        # Send message via Telegram bot
        async def send_telegram_message():
            bot = Bot(token=bot_token)
            admin_name = session.get('admin_info', {}).get('full_name', 'Admin')
            formatted_message = f"📩 *Message from {admin_name}*\n\n{message}"
            
            await bot.send_message(
                chat_id=telegram_id,
                text=formatted_message,
                parse_mode='Markdown'
            )
        
        # Run async function
        asyncio.run(send_telegram_message())
        
        return jsonify({
            'success': True,
            'message': 'Message sent successfully'
        })
        
    except Exception as e:
        print(f"Error sending message: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to send message: {str(e)}'
        })

@users_bp.route('/users/promote/<user_id>', methods=['POST'])
@super_admin_required
def promote_to_admin(user_id):
    """Promote user to admin - now calls API"""
    # Get data from JSON body
    data = request.get_json()
    role = data.get('role', 'admin')
    division = data.get('division')
    
    # 🔄 Call API instead of service
    response = api_client.post(f'/api/v1/users/{user_id}/promote', {
        'role': role,
        'division': division
    })
    
    # Always return JSON for AJAX requests
    return jsonify(response)
    
    return redirect(url_for('users.view_user', user_id=user_id))

@users_bp.route('/api/users')
def get_users():
    """Get all users with formatted timestamps"""
    user_service = UserService()
    users = user_service.get_all_users()
    
    formatted_users = []
    for user in users:
        formatted_users.append({
            'id': user.id,
            'telegram_id': user.telegram_id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'created_at': Helpers.format_timestamp(user.created_at),
            'last_login': Helpers.format_timestamp(user.last_login) if user.last_login else 'Never'
        })
    
    return jsonify(formatted_users)

@users_bp.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get specific user details"""
    user_service = UserService()
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user_data = {
        'id': user.id,
        'telegram_id': user.telegram_id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_active': user.is_active,
        'created_at': Helpers.format_timestamp(user.created_at),
        'last_login': Helpers.format_timestamp(user.last_login) if user.last_login else 'Never'
    }
    
    return jsonify(user_data)

@users_bp.route('/users/api/list')
@any_admin_required
def api_list_users():
    """API endpoint for paginated user list"""
    db = SessionLocal()
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '').lower()
        
        users = user_service.get_all_users(db)
        
        # Filter by search if provided
        if search:
            users = [u for u in users 
                    if search in (u.full_name or '').lower() 
                    or search in (u.username or '').lower()
                    or search in str(u.telegram_id)]
        
        # Apply pagination
        paginated_users = Helpers.paginate(users, page, per_page)
        
        return jsonify({
            'success': True,
            'users': [{
                'id': u.id,
                'telegram_id': u.telegram_id,
                'full_name': u.full_name,
                'username': u.username,
                'is_active': u.is_active,
                'created_at': Helpers.format_timestamp(u.created_at),
                'last_login': Helpers.format_timestamp(u.last_login) if u.last_login else 'Never'
            } for u in paginated_users],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(users),
                'total_pages': (len(users) + per_page - 1) // per_page
            }
        })
    finally:
        db.close()