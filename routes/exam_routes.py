from flask import Blueprint, request, jsonify
from models.exam import ExamModel
import pytesseract
from PIL import Image
from io import BytesIO
import base64
import difflib

exam_bp = Blueprint('exam', __name__)

# API tạo đề thi mới
@exam_bp.route("/exam", methods=["POST"])
def create_exam():
    data = request.json
    title = data.get("title")
    question = data.get("question")
    answer = data.get("answer")
    
    if not title or not question or not answer:
        return jsonify({"message": "Missing required fields"}), 400
    
    ExamModel.create_exam(title, question, answer)
    return jsonify({"message": "Exam created successfully"}), 201

# API lấy danh sách tất cả đề thi
@exam_bp.route("/exam", methods=["GET"])
def get_all_exams():
    exams = ExamModel.get_all_exams()
    return jsonify(exams), 200

# API tải bài làm của học sinh và chấm điểm
@exam_bp.route("/exam/submit", methods=["POST"])
def submit_exam():
    data = request.json
    exam_id = data.get("exam_id")
    student_image_base64 = data.get("image")  # Ảnh bài làm dạng base64

    if not exam_id or not student_image_base64:
        return jsonify({"message": "Missing required fields"}), 400
    
    # Chuyển đổi base64 thành ảnh
    image_bytes = base64.b64decode(student_image_base64)
    student_answer = ocr_from_image(image_bytes)
    
    # Lấy đáp án từ cơ sở dữ liệu
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404
    
    correct_answer = exam.get("answer")
    
    # So sánh bài làm của học sinh với đáp án và tạo nhận xét chi tiết
    score, feedback = compare_answers(student_answer, correct_answer)

    return jsonify({
        "message": "Exam submitted successfully",
        "score": f"{score}/10",
        "feedback": feedback
    }), 200

# Hàm nhận diện văn bản từ ảnh (OCR)
def ocr_from_image(image_bytes):
    img = Image.open(BytesIO(image_bytes))
    text = pytesseract.image_to_string(img)
    return text

# Hàm so sánh bài làm của học sinh với đáp án và tạo nhận xét chi tiết
def compare_answers(student_answer, correct_answer):
    # Chuẩn hóa và tách câu thành danh sách các từ
    student_words = student_answer.strip().lower().split()
    correct_words = correct_answer.strip().lower().split()
    
    # Tính tỷ lệ tương đồng sử dụng difflib
    matcher = difflib.SequenceMatcher(None, correct_words, student_words)
    ratio = matcher.ratio()  # Giá trị từ 0 đến 1
    score = round(ratio * 10)
    
    # Tạo nhận xét chi tiết theo từng từ (HTML diff)
    diff = difflib.ndiff(correct_words, student_words)
    diff_html = ""
    for token in diff:
        if token.startswith("  "):
            # Từ trùng khớp
            diff_html += f"<span style='color:green;'>{token[2:]}</span> "
        elif token.startswith("- "):
            # Từ thiếu hoặc sai (đáp án có nhưng học sinh không)
            diff_html += f"<span style='color:red;text-decoration:line-through;'>{token[2:]}</span> "
        elif token.startswith("+ "):
            # Từ thừa (học sinh thêm vào)
            diff_html += f"<span style='color:orange;'>{token[2:]}</span> "
    return score, diff_html

# API lấy chi tiết đề thi theo ID
@exam_bp.route("/exam/<exam_id>", methods=["GET"])
def get_exam_by_id(exam_id):
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404
    return jsonify(exam), 200

# API sửa đề thi theo ID
@exam_bp.route("/exam/<exam_id>", methods=["PUT"])
def update_exam(exam_id):
    data = request.json
    title = data.get("title")
    question = data.get("question")
    answer = data.get("answer")
    
    if not title or not question or not answer:
        return jsonify({"message": "Missing required fields"}), 400
    
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404

    ExamModel.update_exam(exam_id, title, question, answer)
    return jsonify({"message": "Exam updated successfully"}), 200

# API xóa đề thi theo ID
@exam_bp.route("/exam/<exam_id>", methods=["DELETE"])
def delete_exam(exam_id):
    exam = ExamModel.get_exam_by_id(exam_id)
    if not exam:
        return jsonify({"message": "Exam not found"}), 404
    
    ExamModel.delete_exam(exam_id)
    return jsonify({"message": "Exam deleted successfully"}), 200
