; Auto-generated. Do not edit!


(cl:in-package armaction-msg)


;//! \htmlinclude ArmControlGoal.msg.html

(cl:defclass <ArmControlGoal> (roslisp-msg-protocol:ros-message)
  ((target_joints
    :reader target_joints
    :initarg :target_joints
    :type (cl:vector cl:float)
   :initform (cl:make-array 0 :element-type 'cl:float :initial-element 0.0))
   (duration
    :reader duration
    :initarg :duration
    :type cl:float
    :initform 0.0)
   (speed
    :reader speed
    :initarg :speed
    :type cl:float
    :initform 0.0))
)

(cl:defclass ArmControlGoal (<ArmControlGoal>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <ArmControlGoal>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'ArmControlGoal)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name armaction-msg:<ArmControlGoal> is deprecated: use armaction-msg:ArmControlGoal instead.")))

(cl:ensure-generic-function 'target_joints-val :lambda-list '(m))
(cl:defmethod target_joints-val ((m <ArmControlGoal>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader armaction-msg:target_joints-val is deprecated.  Use armaction-msg:target_joints instead.")
  (target_joints m))

(cl:ensure-generic-function 'duration-val :lambda-list '(m))
(cl:defmethod duration-val ((m <ArmControlGoal>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader armaction-msg:duration-val is deprecated.  Use armaction-msg:duration instead.")
  (duration m))

(cl:ensure-generic-function 'speed-val :lambda-list '(m))
(cl:defmethod speed-val ((m <ArmControlGoal>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader armaction-msg:speed-val is deprecated.  Use armaction-msg:speed instead.")
  (speed m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <ArmControlGoal>) ostream)
  "Serializes a message object of type '<ArmControlGoal>"
  (cl:let ((__ros_arr_len (cl:length (cl:slot-value msg 'target_joints))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) __ros_arr_len) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) __ros_arr_len) ostream))
  (cl:map cl:nil #'(cl:lambda (ele) (cl:let ((bits (roslisp-utils:encode-single-float-bits ele)))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream)))
   (cl:slot-value msg 'target_joints))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'duration))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
  (cl:let ((bits (roslisp-utils:encode-single-float-bits (cl:slot-value msg 'speed))))
    (cl:write-byte (cl:ldb (cl:byte 8 0) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 8) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 16) bits) ostream)
    (cl:write-byte (cl:ldb (cl:byte 8 24) bits) ostream))
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <ArmControlGoal>) istream)
  "Deserializes a message object of type '<ArmControlGoal>"
  (cl:let ((__ros_arr_len 0))
    (cl:setf (cl:ldb (cl:byte 8 0) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 8) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 16) __ros_arr_len) (cl:read-byte istream))
    (cl:setf (cl:ldb (cl:byte 8 24) __ros_arr_len) (cl:read-byte istream))
  (cl:setf (cl:slot-value msg 'target_joints) (cl:make-array __ros_arr_len))
  (cl:let ((vals (cl:slot-value msg 'target_joints)))
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
    (cl:setf (cl:slot-value msg 'duration) (roslisp-utils:decode-single-float-bits bits)))
    (cl:let ((bits 0))
      (cl:setf (cl:ldb (cl:byte 8 0) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 8) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 16) bits) (cl:read-byte istream))
      (cl:setf (cl:ldb (cl:byte 8 24) bits) (cl:read-byte istream))
    (cl:setf (cl:slot-value msg 'speed) (roslisp-utils:decode-single-float-bits bits)))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<ArmControlGoal>)))
  "Returns string type for a message object of type '<ArmControlGoal>"
  "armaction/ArmControlGoal")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'ArmControlGoal)))
  "Returns string type for a message object of type 'ArmControlGoal"
  "armaction/ArmControlGoal")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<ArmControlGoal>)))
  "Returns md5sum for a message object of type '<ArmControlGoal>"
  "10fd138217332a6be1290c5c92c60103")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'ArmControlGoal)))
  "Returns md5sum for a message object of type 'ArmControlGoal"
  "10fd138217332a6be1290c5c92c60103")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<ArmControlGoal>)))
  "Returns full string definition for message of type '<ArmControlGoal>"
  (cl:format cl:nil "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%~%float32[] target_joints  ~%float32 duration        ~%float32 speed           ~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'ArmControlGoal)))
  "Returns full string definition for message of type 'ArmControlGoal"
  (cl:format cl:nil "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======~%~%float32[] target_joints  ~%float32 duration        ~%float32 speed           ~%~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <ArmControlGoal>))
  (cl:+ 0
     4 (cl:reduce #'cl:+ (cl:slot-value msg 'target_joints) :key #'(cl:lambda (ele) (cl:declare (cl:ignorable ele)) (cl:+ 4)))
     4
     4
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <ArmControlGoal>))
  "Converts a ROS message object to a list"
  (cl:list 'ArmControlGoal
    (cl:cons ':target_joints (target_joints msg))
    (cl:cons ':duration (duration msg))
    (cl:cons ':speed (speed msg))
))
