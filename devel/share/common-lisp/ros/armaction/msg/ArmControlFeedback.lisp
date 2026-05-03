; Auto-generated. Do not edit!


(cl:in-package armaction-msg)


;//! \htmlinclude ArmControlFeedback.msg.html

(cl:defclass <ArmControlFeedback> (roslisp-msg-protocol:ros-message)
  ((current_joints
    :reader current_joints
    :initarg :current_joints
    :type (cl:vector cl:float)
   :initform (cl:make-array 0 :element-type 'cl:float :initial-element 0.0))
   (progress
    :reader progress
    :initarg :progress
    :type cl:float
    :initform 0.0)
   (state
    :reader state
    :initarg :state
    :type cl:string
    :initform ""))
)

(cl:defclass ArmControlFeedback (<ArmControlFeedback>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <ArmControlFeedback>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'ArmControlFeedback)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name armaction-msg:<ArmControlFeedback> is deprecated: use armaction-msg:ArmControlFeedback instead.")))

(cl:ensure-generic-function 'current_joints-val :lambda-list '(m))
(cl:defmethod current_joints-val ((m <ArmControlFeedback>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader armaction-msg:current_joints-val is deprecated.  Use armaction-msg:current_joints instead.")
  (current_joints m))

(cl:ensure-generic-function 'progress-val :lambda-list '(m))
(cl:defmethod progress-val ((m <ArmControlFeedback>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader armaction-msg:progress-val is deprecated.  Use armaction-msg:progress instead.")
  (progress m))

(cl:ensure-generic-function 'state-val :lambda-list '(m))
(cl:defmethod state-val ((m <ArmControlFeedback>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader armaction-msg:state-val is deprecated.  Use armaction-msg:state instead.")
  (state m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <ArmControlFeedback>) ostream)
  "Serializes a message object of type '<ArmControlFeedback>"
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'current_joints))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_arr_len) ostream))
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let ((bits (roslisp-utils:encode-single-float-bits ele)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)))
   (cl:slot-value msg 'current_joints))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'progress))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:let ((__ros_str_len (cl:length (cl:slot-value msg 'state))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_str_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_str_len) ostream))
  (cl:map cl:nil #'(cl:lambda (c) (cl:write-byte (cl:char-code c) ostream)) (cl:slot-value msg 'state))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <ArmControlFeedback>) istream)
  "Deserializes a message object of type '<ArmControlFeedback>"
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'current_joints) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'current_joints)))
    (cl:dotimes (i __ros_arr_len)
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:aref vals i) (roslisp-utils:decode-single-float-bits bits))))))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'progress) (roslisp-utils:decode-single-float-bits bits)))
    (cl:let ((__ros_str_len 0))
      (cl:setf (cl:ldb (cl:byte 8 0) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) __ros_str_len) (cl:read-byte istream))
      (cl:setf (cl:slot-value msg 'state) (cl:make-string __ros_str_len))
      (cl:dotimes (__ros_str_idx __ros_str_len msg)
        (cl:setf (cl:char (cl:slot-value msg 'state) __ros_str_idx) (cl:code-char (cl:read-byte istream)))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<ArmControlFeedback>)))
  "Returns string type for a message object of type '<ArmControlFeedback>"
  "armaction/ArmControlFeedback")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ArmControlFeedback)))
  "Returns string type for a message object of type 'ArmControlFeedback"
  "armaction/ArmControlFeedback")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<ArmControlFeedback>)))
  "Returns md5sum for a message object of type '<ArmControlFeedback>"
  "f7cc27d8325ec06677f29e18067f057c")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'ArmControlFeedback)))
  "Returns md5sum for a message object of type 'ArmControlFeedback"
  "f7cc27d8325ec06677f29e18067f057c")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<ArmControlFeedback>)))
  "Returns full string definition for message of type '<ArmControlFeedback>"
  (cl:format cl:nil "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%~%float32[] current_joints ~%float32 progress        ~%string state            ~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'ArmControlFeedback)))
  "Returns full string definition for message of type 'ArmControlFeedback"
  (cl:format cl:nil "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%~%float32[] current_joints ~%float32 progress        ~%string state            ~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <ArmControlFeedback>))
  (cl:+ 0
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'current_joints) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
     4
     4 (cl:length (cl:slot-value msg 'state))
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <ArmControlFeedback>))
  "Converts a ROS message object to a list"
  (cl:list 'ArmControlFeedback
    (cl:cons ':current_joints (current_joints msg))
    (cl:cons ':progress (progress msg))
    (cl:cons ':state (state msg))
))
