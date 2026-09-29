import time
import threading
import requests
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

database_accounts = [
    {"id": 1, "token": "token_dummy_1", "status": "active"},
    {"id": 2, "token": "token_dummy_2", "status": "active"}
]

def generate_new_guest_accounts(count):
    print(f"[+] Generating {count} new guest accounts...")
    for i in range(count):
        new_id = len(database_accounts) + 1
        dummy_token = f"token_dummy_{new_id}_{int(time.time())}"
        database_accounts.append({
            "id": new_id,
            "token": dummy_token,
            "status": "active"
        })
    print(f"[+] Generation completed! Total active accounts: {len(database_accounts)}")

def background_auto_maintenance():
    while True:
        print("[MAINTENANCE] Running 2-day auto cleanup & refresh task...")
        global database_accounts
        database_accounts = [acc for acc in database_accounts if acc['status'] == 'active']
        generate_new_guest_accounts(50)
        time.sleep(172800)

maintenance_thread = threading.Thread(target=background_auto_maintenance, daemon=True)
maintenance_thread.start()

@app.route('/api/send_likes', methods=['POST'])
def api_send_likes():
    data = request.json or {}
    uid = data.get('uid')
    requested_likes = int(data.get('likes', 100))

    if not uid:
        return jsonify({"status": "error", "message": "UID is required!"}), 400

    active_accounts = [acc for acc in database_accounts if acc['status'] == 'active']
    active_count = len(active_accounts)

    if active_count < requested_likes:
        deficit = requested_likes - active_count
        generate_new_guest_accounts(deficit)
        active_accounts = [acc for acc in database_accounts if acc['status'] == 'active']

    sent_count = 0
    accounts_to_use = active_accounts[:requested_likes]

    for acc in accounts_to_use:
        success = hit_garena_like_endpoint(uid, acc['token'])
        
        if success:
            sent_count += 1
        else:
            acc['status'] = 'banned'
            generate_new_guest_accounts(1)

        time.sleep(1.0)

    return jsonify({
        "status": "success",
        "requested": requested_likes,
        "sent": sent_count
    })

def hit_garena_like_endpoint(uid, token):
    return True

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
