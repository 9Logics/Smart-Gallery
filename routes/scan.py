from flask import Blueprint, request, jsonify, send_file
from app_globals import *

scan_bp = Blueprint("scan", __name__)

@scan_bp.route('/api/scan/status')
def get_scan_status():
    return jsonify(scan_status)


@scan_bp.route('/api/scan/reevaluate_faces', methods=['POST'])
def reevaluate_faces():
    """
    Recalculate centroids for named people and reassign automatic faces if they match
    another named person significantly better, or unassign if they no longer match.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Get all named people and their centroids (including manual faces for accurate centroids)
        cursor.execute("""
            SELECT p.id, f.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL AND f.is_manual != -1
        """)
        rows = cursor.fetchall()
        
        person_embeddings = {}
        for person_id, emb_blob in rows:
            emb = np.frombuffer(emb_blob, dtype=np.float32)
            if person_id not in person_embeddings:
                person_embeddings[person_id] = []
            person_embeddings[person_id].append(emb)
            
        centroids = {}
        for person_id, embs in person_embeddings.items():
            centroids[person_id] = np.mean(embs, axis=0)
            
        if not centroids:
            return jsonify({"success": True, "reassigned": 0, "unassigned": 0})
            
        # 2. Get all automatic faces assigned to named people
        cursor.execute("""
            SELECT f.id, f.person_id, f.embedding 
            FROM faces f 
            JOIN people p ON f.person_id = p.id
            WHERE p.name NOT LIKE 'Person %' AND f.embedding IS NOT NULL 
              AND (f.is_manual = 0 OR f.is_manual IS NULL)
        """)
        face_rows = cursor.fetchall()
        
        reassigned_count = 0
        unassigned_count = 0
        
        for f_id, current_person_id, emb_blob in face_rows:
            emb = np.frombuffer(emb_blob, dtype=np.float32)
            
            best_other_person_id = None
            best_other_dist = 1.0
            current_dist = 1.0
            
            for p_id, centroid in centroids.items():
                dist = face_processor.compute_cosine_distance(emb, centroid)
                if p_id == current_person_id:
                    current_dist = dist
                elif dist < best_other_dist:
                    best_other_dist = dist
                    best_other_person_id = p_id
                    
            # Logic: If it matches another person much better
            if best_other_person_id is not None and best_other_dist < 0.40 and best_other_dist < (current_dist - 0.05):
                cursor.execute("UPDATE faces SET person_id = ? WHERE id = ?", (best_other_person_id, f_id))
                reassigned_count += 1
            # Logic: If it doesn't match its own person anymore, and no other person is a good match
            elif current_dist > 0.48:
                cursor.execute("UPDATE faces SET person_id = NULL WHERE id = ?", (f_id,))
                unassigned_count += 1
                
        conn.commit()
        
    return jsonify({"success": True, "reassigned": reassigned_count, "unassigned": unassigned_count})



@scan_bp.route('/api/scan_directory', methods=['POST'])
def manual_scan_directory():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'scan_folder'")
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "No directory set"}), 400
        root_dir = row[0]
        
    def scan_task():
        scan_directory(root_dir)
        
    threading.Thread(target=scan_task, daemon=True).start()
    return jsonify({"success": True, "message": "Directory scan started"})


