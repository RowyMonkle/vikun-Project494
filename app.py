import os

from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# LINE Messaging API credentials
LINE_ACCESS_TOKEN = '+8M2DNpX9aSAvIqyCQikmaYA4cXUYGIh9Xv4fVLyHyW+OVa49UkKrPrqmEYG4nJblAuSOxtpc90RZuAX8nXTIH3FlGACxyqMB5P1x9GJSpaDziz1PNRX4f1gCcwiVxZS5YDJJRt79P8jXZHYPmDTdQdB04t89/1O/w1cDnyilFU='
LINE_USER_ID = 'Ud16abf5943c241dea0f049772f3d4ad2'
LINE_API_URL = 'https://api.line.me/v2/bot/message/push'

# web hook endpoint (vikunja's side)
@app.route('/webhook', methods=['POST'])
def vikunja_to_line():
    payload = request.json 
    #GET
    event_name = payload.get('event_name', 'มีการอัปเดต')
    task_data = payload.get('data', {}).get('task', {})
    project_title = payload.get('data', {}).get('project', {}).get('title', 'ไม่ระบุโปรเจกต์')
    task_title = task_data.get('title', 'ไม่ได้ระบุชื่องาน')
    
    message_text = ""
    if event_name == 'task.created':
        message_text = f"🆕 [ฮีโร่รวมพล มีงานใหม่ต้องทำ!]\nโปรเจกต์: {project_title} ชื่องาน: {task_title}"
        
    elif event_name == 'task.updated':
        task_data = payload.get('data', {}).get('task', {})
        is_done = task_data.get('done')

        if is_done is True:
            message_text = f"✅ ขอบคุณที่ทำงานหนัก \nโปรเจกต์: {project_title} ชื่องาน: {task_title} เสร็จสมบูรณ์แล้ว!"
        elif is_done is False:
            message_text = f"🔄 งานถูกเปลี่ยนสถานะ \nโปรเจกต์: {project_title} ชื่องาน: {task_title} ยังไม่เสร็จสิ้น"
        else:
            message_text = f"📝 โปรเจกต์: {project_title} ชื่องาน: {task_title} มีการอัปเดต"
            
    elif event_name == 'task.deleted':
        message_text = f"โปรเจกต์: {project_title} ชื่องาน: {task_title} ถูกลบออกแล้ว"
        
    elif event_name == 'task.comment.created':
        comment_text = payload.get('data', {}).get('comment', {}).get('text', 'ไม่มีข้อความ')
        message_text = f"💬 [มีคอมเมนต์ใหม่]\nโปรเจกต์: {project_title} ชื่องาน: {task_title}\nข้อความ: {comment_text}"
        
    elif event_name in ['task.overdue', 'tasks.overdue']:
        message_text = f"🚨 [กรุงโรมกำลังลุกเป็นไฟ!]\nโปรเจกต์: {project_title} ชื่องาน: {task_title} ถึงเดดไลน์แล้ว!"
        
    else:
        return jsonify({'status': 'ignored', 'message': f'Unhandled event: {event_name}'}), 200
    
    # Line messaging API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_ACCESS_TOKEN}'
    }
    line_payload = {
        "to": LINE_USER_ID,
        "messages": [{"type": "text", "text": message_text}]
    }

    #POST
    requests.post(LINE_API_URL, headers=headers, json=line_payload)
    return jsonify({'status': 'success', 'message': 'Sent to LINE'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)