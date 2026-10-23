const mongoose = require("mongoose");

const LeaveLogSchema = new mongoose.Schema({
  leave_request_id: { type: Number, required: true },
  user_id: { type: Number, required: true },
  action: { type: String, required: true }, 
  performed_by: { type: String, required: true },
  
  // Lưu "Nội dung xin nghỉ phép" đầy đủ tại đây
  details: {
    full_name: String,        // Tên nhân viên
    reason_text: String,      // Nội dung lý do nghỉ (Trường 'reason' trong Postgres)
    start_date: Date,         // Ngày bắt đầu
    end_date: Date,           // Ngày kết thúc
    total_days: Number,       // Tổng số ngày nghỉ
    status: String,           // Trạng thái đơn (PENDING/APPROVED/REJECTED)
    rejection_reason: String, // Lý do từ chối (nếu có)
    applied_at: Date          // Thời điểm gửi đơn
  },
  
  timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model("LeaveLog", LeaveLogSchema);